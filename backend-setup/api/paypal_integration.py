"""
PayPal integration API endpoints for payment processing.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend_setup.db.models import User, Subscription, PayPalOrder, OnboardingState
from backend_setup.services.email_service import EmailService
from backend_setup.services.analytics_service import AnalyticsService
import os
import uuid
import requests
import base64
from datetime import datetime

paypal_bp = Blueprint('paypal', __name__, url_prefix='/api/paypal')

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pgpass@localhost/tero_voice')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# PayPal configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_BASE_URL = os.getenv('PAYPAL_BASE_URL', 'https://api-m.sandbox.paypal.com')  # Use sandbox for testing
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')

email_service = EmailService()
analytics_service = AnalyticsService()

# Plan configurations
PLANS = {
    'monthly_299': {
        'name': 'Solo Pro Plan',
        'price': 299.00,
        'max_clients': 1,
        'max_minutes': 1000
    },
    'monthly_499': {
        'name': 'Pro Plan',
        'price': 499.00,
        'max_clients': 3,
        'max_minutes': 2500
    },
    'monthly_799': {
        'name': 'White-Label Plan',
        'price': 799.00,
        'max_clients': 10,
        'max_minutes': 5000
    }
}


def get_paypal_access_token():
    """Get PayPal access token for API calls."""
    try:
        auth_string = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = 'grant_type=client_credentials'

        response = requests.post(
            f'{PAYPAL_BASE_URL}/v1/oauth2/token',
            headers=headers,
            data=data
        )

        if response.status_code == 200:
            return response.json()['access_token']
        else:
            current_app.logger.error(f"PayPal auth failed: {response.text}")
            return None

    except Exception as e:
        current_app.logger.error(f"Error getting PayPal access token: {str(e)}")
        return None


@paypal_bp.route('/create-order', methods=['POST'])
def create_order():
    """Create a PayPal order for subscription purchase."""
    try:
        data = request.get_json()
        plan_id = data.get('planId')
        return_url = data.get('returnUrl', 'https://app.tero.com/onboarding')
        cancel_url = data.get('cancelUrl', 'https://app.tero.com/pricing')

        if plan_id not in PLANS:
            return jsonify({'error': 'Invalid plan ID'}), 400

        plan = PLANS[plan_id]
        access_token = get_paypal_access_token()

        if not access_token:
            return jsonify({'error': 'PayPal authentication failed'}), 500

        # Create PayPal order
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': str(uuid.uuid4())
        }

        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': 'USD',
                    'value': str(plan['price'])
                },
                'description': f"Tero Voice - {plan['name']} (Monthly Subscription)"
            }],
            'application_context': {
                'return_url': return_url,
                'cancel_url': cancel_url,
                'brand_name': 'Tero Voice',
                'landing_page': 'BILLING',
                'user_action': 'PAY_NOW'
            }
        }

        response = requests.post(
            f'{PAYPAL_BASE_URL}/v2/checkout/orders',
            headers=headers,
            json=order_data
        )

        if response.status_code == 201:
            order_response = response.json()
            paypal_order_id = order_response['id']

            # Save order to database
            session = SessionLocal()
            db_order = PayPalOrder(
                paypal_order_id=paypal_order_id,
                plan_id=plan_id,
                amount=plan['price'],
                currency='USD',
                status='created',
                paypal_data=order_response
            )
            session.add(db_order)
            session.commit()
            session.close()

            # Log analytics event
            analytics_service.log_event(
                user_id=None,
                event_type='paypal_order_created',
                event_data={
                    'plan_id': plan_id,
                    'amount': plan['price'],
                    'paypal_order_id': paypal_order_id
                }
            )

            return jsonify({
                'orderId': paypal_order_id,
                'approvalUrl': next(
                    link['href'] for link in order_response['links']
                    if link['rel'] == 'approve'
                )
            })
        else:
            current_app.logger.error(f"PayPal order creation failed: {response.text}")
            return jsonify({'error': 'Failed to create PayPal order'}), 500

    except Exception as e:
        current_app.logger.error(f"Error creating PayPal order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@paypal_bp.route('/capture-order', methods=['POST'])
def capture_order():
    """Capture a PayPal order and create customer account."""
    try:
        data = request.get_json()
        order_id = data.get('orderId')
        payer_id = data.get('payerId')

        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400

        session = SessionLocal()

        # Get order from database
        db_order = session.query(PayPalOrder).filter(
            PayPalOrder.paypal_order_id == order_id
        ).first()

        if not db_order:
            session.close()
            return jsonify({'error': 'Order not found'}), 404

        access_token = get_paypal_access_token()
        if not access_token:
            session.close()
            return jsonify({'error': 'PayPal authentication failed'}), 500

        # Capture the order
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': str(uuid.uuid4())
        }

        response = requests.post(
            f'{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture',
            headers=headers
        )

        if response.status_code == 201:
            capture_response = response.json()

            # Extract payer information
            payer_info = capture_response.get('payer', {})
            email = payer_info.get('email_address')
            name = payer_info.get('name', {})
            full_name = f"{name.get('given_name', '')} {name.get('surname', '')}".strip()

            if not email:
                session.close()
                return jsonify({'error': 'Payer email not found'}), 400

            # Create or get user
            user = session.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    id=uuid.uuid4(),
                    email=email,
                    name=full_name,
                    is_active=True
                )
                session.add(user)
                session.flush()  # Get the user ID

            # Create subscription
            plan = PLANS[db_order.plan_id]
            subscription = Subscription(
                user_id=user.id,
                plan=db_order.plan_id,
                status='active',
                paypal_subscription_id=order_id,  # Using order ID for now
                paypal_plan_id=db_order.plan_id,
                monthly_price=db_order.amount,
                max_clients=plan['max_clients'],
                max_minutes_per_month=plan['max_minutes']
            )
            session.add(subscription)

            # Update order status
            db_order.user_id = user.id
            db_order.status = 'captured'
            db_order.paypal_payer_id = payer_id
            db_order.paypal_capture_id = capture_response['id']
            db_order.paypal_data = capture_response

            # Create initial onboarding state
            onboarding = OnboardingState(
                user_id=user.id,
                current_step=1,
                progress=0,
                completed_steps=[],
                caller_responses={
                    'appointment_request': 'I\'d be happy to help you schedule an appointment. Let me check our availability.',
                    'pricing_inquiry': 'I can provide you with pricing information. What specific service are you interested in?',
                    'emergency': 'I understand this is urgent. Let me connect you with someone right away.',
                    'other': 'Thank you for calling. How can I assist you today?'
                }
            )
            session.add(onboarding)

            session.commit()

            # Generate portal URL
            portal_url = f"/onboarding/{user.id}"

            # Send welcome email
            email_service.send_welcome_email(email, full_name, portal_url)

            # Log analytics event
            analytics_service.log_event(
                user_id=str(user.id),
                event_type='paypal_order_captured',
                event_data={
                    'plan_id': db_order.plan_id,
                    'amount': db_order.amount,
                    'paypal_order_id': order_id,
                    'new_customer': True
                }
            )

            session.close()

            return jsonify({
                'success': True,
                'customerId': str(user.id),
                'portalUrl': portal_url,
                'email': email,
                'message': 'Payment successful! Check your email for onboarding instructions.'
            })

        else:
            current_app.logger.error(f"PayPal capture failed: {response.text}")
            session.close()
            return jsonify({'error': 'Payment capture failed'}), 500

    except Exception as e:
        current_app.logger.error(f"Error capturing PayPal order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@paypal_bp.route('/verify-webhook', methods=['POST'])
def verify_webhook():
    """Verify PayPal webhook signature and process events."""
    try:
        webhook_data = request.get_json()

        # Verify webhook signature
        transmission_id = request.headers.get('PAYPAL-TRANSMISSION-ID')
        transmission_time = request.headers.get('PAYPAL-TRANSMISSION-TIME')
        cert_url = request.headers.get('PAYPAL-CERT-URL')
        auth_algo = request.headers.get('PAYPAL-AUTH-ALGO')
        transmission_sig = request.headers.get('PAYPAL-TRANSMISSION-SIG')

        # If any header is missing, fail
        if not all([transmission_id, transmission_time, cert_url, auth_algo, transmission_sig]):
             current_app.logger.warning("Missing PayPal webhook headers")
             return jsonify({'error': 'Missing webhook signature headers'}), 400

        # Verify with PayPal
        access_token = get_paypal_access_token()
        if not access_token:
            return jsonify({'error': 'Could not authenticate with PayPal'}), 500

        # Check if PAYPAL_WEBHOOK_ID is configured
        if not PAYPAL_WEBHOOK_ID:
             current_app.logger.warning("PAYPAL_WEBHOOK_ID not configured, skipping verification")
        else:
            verification_payload = {
                "auth_algo": auth_algo,
                "cert_url": cert_url,
                "transmission_id": transmission_id,
                "transmission_sig": transmission_sig,
                "transmission_time": transmission_time,
                "webhook_id": PAYPAL_WEBHOOK_ID,
                "webhook_event": webhook_data
            }

            resp = requests.post(
                f'{PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                },
                json=verification_payload
            )

            if resp.status_code != 200:
                current_app.logger.error(f"PayPal webhook verification failed: {resp.text}")
                return jsonify({'error': 'Webhook verification failed'}), 400

            verification_response = resp.json()
            if verification_response.get('verification_status') != 'SUCCESS':
                 current_app.logger.error(f"PayPal webhook signature invalid: {verification_response}")
                 return jsonify({'error': 'Invalid webhook signature'}), 400

        event_type = webhook_data.get('event_type')

        # Log webhook event
        analytics_service.log_event(
            user_id=None,
            event_type='paypal_webhook_received',
            event_data={
                'event_type': event_type,
                'webhook_id': webhook_data.get('id')
            }
        )

        # Process different webhook events
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Handle successful payment
            pass
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            # Handle subscription cancellation
            pass
        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            # Handle subscription suspension
            pass

        return jsonify({'success': True})

    except Exception as e:
        current_app.logger.error(f"Error processing PayPal webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
