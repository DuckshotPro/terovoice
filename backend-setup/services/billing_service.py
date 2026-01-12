"""
Billing Service for managing subscriptions, usage metrics, and invoices.
Orchestrates PayPal API integration and database operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend_setup.db.models import Subscription, Usage, Invoice, User
from backend_setup.db.connection import get_db_context

logger = logging.getLogger(__name__)


class BillingService:
    """
    Main service for billing operations.
    Handles subscription management, usage tracking, and invoice operations.
    """

    def __init__(self, paypal_client=None, usage_service=None):
        """
        Initialize BillingService with dependencies.
        
        Args:
            paypal_client: PayPal API client instance
            usage_service: UsageService instance for usage tracking
        """
        self.paypal_client = paypal_client
        self.usage_service = usage_service
        self.cache = {}  # Simple in-memory cache for subscription data

    def get_subscription_status(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current subscription status for a customer.
        Fetches from database and syncs with PayPal if needed.
        
        Args:
            customer_id: Customer/User ID
            
        Returns:
            Subscription status dict or None if not found
        """
        try:
            with get_db_context() as db:
                subscription = db.query(Subscription).filter(
                    Subscription.user_id == customer_id
                ).first()

                if not subscription:
                    logger.warning(f"No subscription found for customer {customer_id}")
                    return None

                # Build response
                status_data = {
                    "subscription_id": str(subscription.id),
                    "customer_id": str(subscription.user_id),
                    "plan_name": subscription.plan,
                    "status": subscription.status,
                    "monthly_price": subscription.monthly_price,
                    "currency": "USD",
                    "paypal_subscription_id": subscription.paypal_subscription_id,
                    "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
                    "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None,
                    "next_billing_date": None,
                    "renewal_date": None,
                    "cancellation_date": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
                }

                logger.info(f"✅ Retrieved subscription status for customer {customer_id}")
                return status_data

        except Exception as e:
            logger.error(f"❌ Error getting subscription status: {e}")
            return None

    def get_usage_metrics(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current usage metrics for a customer.
        
        Args:
            customer_id: Customer/User ID
            
        Returns:
            Usage metrics dict or None if not found
        """
        try:
            with get_db_context() as db:
                # Get current subscription
                subscription = db.query(Subscription).filter(
                    Subscription.user_id == customer_id
                ).first()

                if not subscription:
                    logger.warning(f"No subscription found for customer {customer_id}")
                    return None

                # Get current billing period usage
                today = datetime.utcnow()
                billing_period_start = today.replace(day=1)
                
                usage = db.query(Usage).filter(
                    Usage.subscription_id == subscription.id,
                    Usage.billing_period_start <= today,
                    Usage.billing_period_end >= today
                ).first()

                if not usage:
                    # No usage recorded yet this period
                    usage_data = {
                        "subscription_id": str(subscription.id),
                        "customer_id": str(subscription.user_id),
                        "plan_tier": subscription.plan,
                        "call_minutes_used": 0,
                        "call_minutes_limit": subscription.max_minutes_per_month,
                        "percentage_used": 0.0,
                        "warning_threshold": 80,
                        "alert_threshold": 100,
                        "billing_period_start": billing_period_start.isoformat(),
                        "billing_period_end": (billing_period_start + timedelta(days=30)).isoformat(),
                        "features": self._get_plan_features(subscription.plan),
                    }
                else:
                    # Calculate percentage
                    percentage = (usage.call_minutes_used / subscription.max_minutes_per_month * 100) if subscription.max_minutes_per_month > 0 else 0
                    percentage = min(percentage, 100.0)  # Cap at 100%

                    usage_data = {
                        "subscription_id": str(subscription.id),
                        "customer_id": str(subscription.user_id),
                        "plan_tier": subscription.plan,
                        "call_minutes_used": usage.call_minutes_used,
                        "call_minutes_limit": subscription.max_minutes_per_month,
                        "percentage_used": round(percentage, 2),
                        "warning_threshold": 80,
                        "alert_threshold": 100,
                        "billing_period_start": usage.billing_period_start.isoformat() if usage.billing_period_start else None,
                        "billing_period_end": usage.billing_period_end.isoformat() if usage.billing_period_end else None,
                        "features": self._get_plan_features(subscription.plan),
                    }

                logger.info(f"✅ Retrieved usage metrics for customer {customer_id}")
                return usage_data

        except Exception as e:
            logger.error(f"❌ Error getting usage metrics: {e}")
            return None

    def get_billing_history(self, customer_id: str, limit: int = 12) -> Optional[List[Dict[str, Any]]]:
        """
        Get billing history (invoices) for a customer.
        Returns invoices in reverse chronological order (newest first).
        
        Args:
            customer_id: Customer/User ID
            limit: Maximum number of invoices to return (default 12 months)
            
        Returns:
            List of invoice dicts or None if error
        """
        try:
            with get_db_context() as db:
                # Get customer's subscription
                subscription = db.query(Subscription).filter(
                    Subscription.user_id == customer_id
                ).first()

                if not subscription:
                    logger.warning(f"No subscription found for customer {customer_id}")
                    return []

                # Get invoices, ordered by date descending (newest first)
                invoices = db.query(Invoice).filter(
                    Invoice.subscription_id == subscription.id
                ).order_by(Invoice.created_at.desc()).limit(limit).all()

                if not invoices:
                    logger.info(f"No invoices found for customer {customer_id}")
                    return []

                # Build response
                invoice_list = []
                for invoice in invoices:
                    invoice_data = {
                        "invoice_id": str(invoice.id),
                        "paypal_invoice_id": invoice.paypal_invoice_id,
                        "date": invoice.created_at.isoformat() if invoice.created_at else None,
                        "amount": invoice.amount,
                        "currency": invoice.currency,
                        "status": invoice.status,
                        "plan_name": subscription.plan,
                        "billing_period_start": invoice.period_start.isoformat() if invoice.period_start else None,
                        "billing_period_end": invoice.period_end.isoformat() if invoice.period_end else None,
                        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                        "paid_date": invoice.paid_at.isoformat() if invoice.paid_at else None,
                        "pdf_url": None,  # TODO: Implement PDF generation
                    }
                    invoice_list.append(invoice_data)

                logger.info(f"✅ Retrieved {len(invoice_list)} invoices for customer {customer_id}")
                return invoice_list

        except Exception as e:
            logger.error(f"❌ Error getting billing history: {e}")
            return None

    def record_usage(self, customer_id: str, call_minutes: float) -> bool:
        """
        Record usage for a customer (e.g., call minutes).
        
        Args:
            customer_id: Customer/User ID
            call_minutes: Number of call minutes to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_context() as db:
                # Get customer's subscription
                subscription = db.query(Subscription).filter(
                    Subscription.user_id == customer_id
                ).first()

                if not subscription:
                    logger.warning(f"No subscription found for customer {customer_id}")
                    return False

                # Get or create usage record for current billing period
                today = datetime.utcnow()
                billing_period_start = today.replace(day=1)
                billing_period_end = (billing_period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

                usage = db.query(Usage).filter(
                    Usage.subscription_id == subscription.id,
                    Usage.billing_period_start <= today,
                    Usage.billing_period_end >= today
                ).first()

                if not usage:
                    # Create new usage record
                    usage = Usage(
                        subscription_id=subscription.id,
                        billing_period_start=billing_period_start,
                        billing_period_end=billing_period_end,
                        call_minutes_used=call_minutes,
                        call_minutes_limit=subscription.max_minutes_per_month,
                    )
                    db.add(usage)
                else:
                    # Update existing usage record
                    usage.call_minutes_used += call_minutes
                    usage.updated_at = datetime.utcnow()

                db.commit()
                logger.info(f"✅ Recorded {call_minutes} minutes for customer {customer_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error recording usage: {e}")
            return False

    def check_usage_thresholds(self, customer_id: str) -> Dict[str, Any]:
        """
        Check if customer's usage exceeds warning (80%) or alert (100%) thresholds.
        
        Args:
            customer_id: Customer/User ID
            
        Returns:
            Dict with threshold status
        """
        try:
            usage_metrics = self.get_usage_metrics(customer_id)
            
            if not usage_metrics:
                return {
                    "customer_id": customer_id,
                    "warning_triggered": False,
                    "alert_triggered": False,
                    "percentage_used": 0.0,
                }

            percentage = usage_metrics.get("percentage_used", 0.0)
            
            return {
                "customer_id": customer_id,
                "percentage_used": percentage,
                "warning_triggered": percentage >= 80 and percentage < 100,
                "alert_triggered": percentage >= 100,
                "call_minutes_used": usage_metrics.get("call_minutes_used", 0),
                "call_minutes_limit": usage_metrics.get("call_minutes_limit", 0),
            }

        except Exception as e:
            logger.error(f"❌ Error checking usage thresholds: {e}")
            return {
                "customer_id": customer_id,
                "warning_triggered": False,
                "alert_triggered": False,
                "percentage_used": 0.0,
            }

    def _get_plan_features(self, plan_name: str) -> List[Dict[str, Any]]:
        """
        Get features for a plan tier.
        
        Args:
            plan_name: Plan name (e.g., 'free', 'starter', 'pro', 'enterprise')
            
        Returns:
            List of feature dicts
        """
        features_map = {
            "free": [
                {"name": "Call Minutes", "included": True, "limit": 100, "used": 0},
                {"name": "Multi-location Support", "included": False},
                {"name": "Priority Support", "included": False},
                {"name": "Dedicated Account Manager", "included": False},
            ],
            "starter": [
                {"name": "Call Minutes", "included": True, "limit": 1000, "used": 0},
                {"name": "Multi-location Support", "included": True, "limit": 1},
                {"name": "Priority Support", "included": False},
                {"name": "Dedicated Account Manager", "included": False},
            ],
            "pro": [
                {"name": "Call Minutes", "included": True, "limit": 5000, "used": 0},
                {"name": "Multi-location Support", "included": True, "limit": 5},
                {"name": "Priority Support", "included": True},
                {"name": "Dedicated Account Manager", "included": False},
            ],
            "enterprise": [
                {"name": "Call Minutes", "included": True, "limit": 50000, "used": 0},
                {"name": "Multi-location Support", "included": True, "limit": 100},
                {"name": "Priority Support", "included": True},
                {"name": "Dedicated Account Manager", "included": True},
            ],
        }

        return features_map.get(plan_name, features_map["free"])

    def sync_subscription_data(self, customer_id: str) -> bool:
        """
        Force sync subscription data with PayPal.
        
        Args:
            customer_id: Customer/User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.paypal_client:
                logger.warning("PayPal client not configured")
                return False

            with get_db_context() as db:
                subscription = db.query(Subscription).filter(
                    Subscription.user_id == customer_id
                ).first()

                if not subscription or not subscription.paypal_subscription_id:
                    logger.warning(f"No PayPal subscription found for customer {customer_id}")
                    return False

                # Fetch from PayPal
                paypal_sub = self.paypal_client.getSubscription(subscription.paypal_subscription_id)

                # Update database
                subscription.status = paypal_sub.get("status", "UNKNOWN").lower()
                subscription.updated_at = datetime.utcnow()
                db.commit()

                logger.info(f"✅ Synced subscription data for customer {customer_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error syncing subscription data: {e}")
            return False
