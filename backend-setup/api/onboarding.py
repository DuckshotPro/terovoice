"""
Onboarding API endpoints for customer setup workflow.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend_setup.db.models import User, OnboardingState, PayPalOrder
from backend_setup.services.email_service import EmailService
from backend_setup.services.analytics_service import AnalyticsService
import os
import uuid
from datetime import datetime

onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/api/onboarding')

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tero_voice')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

email_service = EmailService()
analytics_service = AnalyticsService()


@onboarding_bp.route('/<customer_id>', methods=['GET'])
def get_onboarding_state(customer_id):
    """Get current onboarding state for a customer."""
    try:
        session = SessionLocal()

        # Find user by ID
        user = session.query(User).filter(User.id == customer_id).first()
        if not user:
            return jsonify({'error': 'Customer not found'}), 404

        # Get or create onboarding state
        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            # Create new onboarding state
            onboarding = OnboardingState(
                user_id=customer_id,
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

        # Convert to dict for JSON response
        response_data = {
            'customerId': str(customer_id),
            'currentStep': onboarding.current_step,
            'progress': onboarding.progress,
            'completedSteps': onboarding.completed_steps or [],
            'businessName': onboarding.business_name,
            'industry': onboarding.industry,
            'businessPhone': onboarding.business_phone,
            'serviceDescription': onboarding.service_description,
            'businessDocuments': onboarding.business_documents or [],
            'forwardingNumber': onboarding.forwarding_number,
            'smsEnabled': onboarding.sms_enabled,
            'smsPhoneNumber': onboarding.sms_phone_number,
            'callerResponses': onboarding.caller_responses or {},
            'calendarProvider': onboarding.calendar_provider,
            'calendarConnected': onboarding.calendar_connected,
            'demoCompleted': onboarding.demo_completed,
            'demoTranscripts': onboarding.demo_transcripts or []
        }

        session.close()
        return jsonify(response_data)

    except Exception as e:
        current_app.logger.error(f"Error getting onboarding state: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-1', methods=['POST'])
def update_business_info(customer_id):
    """Update business information (Step 1)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        # Get onboarding state
        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update business information
        onboarding.business_name = data.get('businessName')
        onboarding.industry = data.get('industry')
        onboarding.business_phone = data.get('businessPhone')
        onboarding.service_description = data.get('serviceDescription')
        onboarding.business_documents = data.get('businessDocuments', [])

        # Update progress
        if 1 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [1]
            onboarding.progress = 20
            onboarding.current_step = 2

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 1,
                'step_name': 'business_info',
                'industry': data.get('industry')
            }
        )

        # Send confirmation email
        user = session.query(User).filter(User.id == customer_id).first()
        if user and user.email:
            email_service.send_business_info_confirmation(
                user.email,
                data.get('businessName'),
                data.get('industry')
            )

        session.close()

        return jsonify({
            'success': True,
            'progress': 20,
            'currentStep': 2,
            'message': 'Business information saved successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating business info: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-2', methods=['POST'])
def update_phone_config(customer_id):
    """Update phone configuration (Step 2)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update phone configuration
        onboarding.forwarding_number = data.get('forwardingNumber')
        onboarding.sms_enabled = data.get('smsEnabled', False)
        onboarding.sms_phone_number = data.get('smsPhoneNumber')

        # Update progress
        if 2 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [2]
            onboarding.progress = 40
            onboarding.current_step = 3

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Send test SMS if enabled
        if data.get('smsEnabled') and data.get('smsPhoneNumber'):
            # TODO: Implement SMS service
            pass

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 2,
                'step_name': 'phone_config',
                'sms_enabled': data.get('smsEnabled', False)
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'progress': 40,
            'currentStep': 3,
            'message': 'Phone configuration saved successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating phone config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-3', methods=['POST'])
def update_caller_responses(customer_id):
    """Update caller responses (Step 3)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update caller responses
        onboarding.caller_responses = data.get('callerResponses', {})

        # Update progress
        if 3 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [3]
            onboarding.progress = 60
            onboarding.current_step = 4

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 3,
                'step_name': 'caller_responses',
                'responses_count': len(data.get('callerResponses', {}))
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'progress': 60,
            'currentStep': 4,
            'message': 'Caller responses saved successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating caller responses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-4', methods=['POST'])
def update_calendar_integration(customer_id):
    """Update calendar integration (Step 4)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update calendar integration
        onboarding.calendar_provider = data.get('calendarProvider')
        onboarding.calendar_connected = data.get('calendarConnected', False)
        onboarding.calendar_access_token = data.get('accessToken')
        onboarding.calendar_refresh_token = data.get('refreshToken')

        # Update progress
        if 4 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [4]
            onboarding.progress = 80
            onboarding.current_step = 5

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 4,
                'step_name': 'calendar_integration',
                'provider': data.get('calendarProvider'),
                'connected': data.get('calendarConnected', False)
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'progress': 80,
            'currentStep': 5,
            'message': 'Calendar integration saved successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating calendar integration: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/demo-complete', methods=['POST'])
def complete_demo(customer_id):
    """Mark demo as complete and save transcripts."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update demo status
        onboarding.demo_completed = True
        onboarding.demo_transcripts = data.get('demoTranscripts', [])
        onboarding.updated_at = datetime.utcnow()

        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='demo_completed',
            event_data={
                'transcript_length': len(data.get('demoTranscripts', [])),
                'demo_duration': len(data.get('demoTranscripts', [])) * 0.5  # Estimate
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'message': 'Demo completed successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error completing demo: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-5', methods=['POST'])
def update_demo_step(customer_id):
    """Update demo step (Step 5)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update demo data
        onboarding.demo_completed = data.get('demoCompleted', False)
        onboarding.demo_transcripts = data.get('demoTranscripts', [])

        # Update progress
        if 5 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [5]
            onboarding.progress = 90
            onboarding.current_step = 6

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 5,
                'step_name': 'interactive_demo',
                'demo_completed': data.get('demoCompleted', False),
                'transcript_count': len(data.get('demoTranscripts', []))
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'progress': 90,
            'currentStep': 6,
            'message': 'Demo step completed successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating demo step: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/step-6', methods=['POST'])
def update_review_step(customer_id):
    """Update review step (Step 6)."""
    try:
        data = request.get_json()
        session = SessionLocal()

        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not onboarding:
            return jsonify({'error': 'Onboarding state not found'}), 404

        # Update progress
        if 6 not in onboarding.completed_steps:
            onboarding.completed_steps = (onboarding.completed_steps or []) + [6]
            onboarding.progress = 95
            onboarding.current_step = 7

        onboarding.updated_at = datetime.utcnow()
        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_step_completed',
            event_data={
                'step': 6,
                'step_name': 'review_configuration',
                'reviewed_at': data.get('reviewedAt')
            }
        )

        session.close()

        return jsonify({
            'success': True,
            'progress': 95,
            'currentStep': 7,
            'message': 'Review completed successfully'
        })

    except Exception as e:
        current_app.logger.error(f"Error updating review step: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@onboarding_bp.route('/<customer_id>/complete', methods=['POST'])
def complete_onboarding(customer_id):
    """Mark onboarding as complete and activate customer."""
    try:
        session = SessionLocal()

        # Get user and onboarding state
        user = session.query(User).filter(User.id == customer_id).first()
        onboarding = session.query(OnboardingState).filter(
            OnboardingState.user_id == customer_id
        ).first()

        if not user or not onboarding:
            return jsonify({'error': 'Customer or onboarding state not found'}), 404

        # Mark all steps as complete
        onboarding.completed_steps = [1, 2, 3, 4, 5, 6, 7]
        onboarding.progress = 100
        onboarding.current_step = 7
        onboarding.updated_at = datetime.utcnow()

        # Activate user
        user.is_active = True
        user.updated_at = datetime.utcnow()

        session.commit()

        # Log analytics event
        analytics_service.log_event(
            user_id=customer_id,
            event_type='onboarding_completed',
            event_data={
                'completion_time': datetime.utcnow().isoformat(),
                'industry': onboarding.industry,
                'demo_completed': onboarding.demo_completed
            }
        )

        # Send "Go Live" email
        if user.email:
            email_service.send_go_live_email(
                user.email,
                onboarding.business_name or user.name
            )

        session.close()

        return jsonify({
            'success': True,
            'progress': 100,
            'message': 'Onboarding completed successfully! Your AI receptionist is now live.',
            'portalUrl': f'/portal/{customer_id}'
        })

    except Exception as e:
        current_app.logger.error(f"Error completing onboarding: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500