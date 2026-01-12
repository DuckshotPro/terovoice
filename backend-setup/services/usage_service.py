"""
Usage Service for tracking and aggregating usage metrics.
Handles call minutes, feature usage, and threshold checking.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend_setup.db.models import Usage, Subscription
from backend_setup.db.connection import get_db_context

logger = logging.getLogger(__name__)


class UsageService:
    """
    Service for tracking and managing usage metrics.
    Handles recording usage, calculating metrics, and checking thresholds.
    """

    def __init__(self):
        """Initialize UsageService."""
        pass

    def record_usage(self, subscription_id: str, usage_data: Dict[str, Any]) -> bool:
        """
        Record usage for a subscription.
        
        Args:
            subscription_id: Subscription ID
            usage_data: Dict with usage details (call_minutes, features_used, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_context() as db:
                # Get or create usage record for current billing period
                today = datetime.utcnow()
                billing_period_start = today.replace(day=1)
                billing_period_end = (billing_period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

                usage = db.query(Usage).filter(
                    Usage.subscription_id == subscription_id,
                    Usage.billing_period_start <= today,
                    Usage.billing_period_end >= today
                ).first()

                call_minutes = usage_data.get("call_minutes", 0)

                if not usage:
                    # Create new usage record
                    usage = Usage(
                        subscription_id=subscription_id,
                        billing_period_start=billing_period_start,
                        billing_period_end=billing_period_end,
                        call_minutes_used=call_minutes,
                        call_minutes_limit=0,  # Will be set from subscription
                    )
                    db.add(usage)
                else:
                    # Update existing usage record
                    usage.call_minutes_used += call_minutes
                    usage.updated_at = datetime.utcnow()

                db.commit()
                logger.info(f"✅ Recorded usage for subscription {subscription_id}: {call_minutes} minutes")
                return True

        except Exception as e:
            logger.error(f"❌ Error recording usage: {e}")
            return False

    def get_usage_metrics(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get usage metrics for a subscription.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Usage metrics dict or None if not found
        """
        try:
            with get_db_context() as db:
                # Get subscription to get limits
                subscription = db.query(Subscription).filter(
                    Subscription.id == subscription_id
                ).first()

                if not subscription:
                    logger.warning(f"Subscription {subscription_id} not found")
                    return None

                # Get current billing period usage
                today = datetime.utcnow()
                usage = db.query(Usage).filter(
                    Usage.subscription_id == subscription_id,
                    Usage.billing_period_start <= today,
                    Usage.billing_period_end >= today
                ).first()

                if not usage:
                    # No usage recorded yet this period
                    metrics = {
                        "subscription_id": str(subscription_id),
                        "call_minutes_used": 0,
                        "call_minutes_limit": subscription.max_minutes_per_month,
                        "percentage_used": 0.0,
                        "billing_period_start": today.replace(day=1).isoformat(),
                        "billing_period_end": (today.replace(day=1) + timedelta(days=30)).isoformat(),
                    }
                else:
                    # Calculate percentage
                    percentage = (usage.call_minutes_used / subscription.max_minutes_per_month * 100) if subscription.max_minutes_per_month > 0 else 0
                    percentage = min(percentage, 100.0)  # Cap at 100%

                    metrics = {
                        "subscription_id": str(subscription_id),
                        "call_minutes_used": usage.call_minutes_used,
                        "call_minutes_limit": subscription.max_minutes_per_month,
                        "percentage_used": round(percentage, 2),
                        "billing_period_start": usage.billing_period_start.isoformat() if usage.billing_period_start else None,
                        "billing_period_end": usage.billing_period_end.isoformat() if usage.billing_period_end else None,
                    }

                logger.info(f"✅ Retrieved usage metrics for subscription {subscription_id}")
                return metrics

        except Exception as e:
            logger.error(f"❌ Error getting usage metrics: {e}")
            return None

    def check_usage_thresholds(self, subscription_id: str) -> Dict[str, Any]:
        """
        Check if usage exceeds warning (80%) or alert (100%) thresholds.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Dict with threshold status
        """
        try:
            metrics = self.get_usage_metrics(subscription_id)
            
            if not metrics:
                return {
                    "subscription_id": subscription_id,
                    "warning_triggered": False,
                    "alert_triggered": False,
                    "percentage_used": 0.0,
                }

            percentage = metrics.get("percentage_used", 0.0)
            
            return {
                "subscription_id": subscription_id,
                "percentage_used": percentage,
                "warning_triggered": percentage >= 80 and percentage < 100,
                "alert_triggered": percentage >= 100,
                "call_minutes_used": metrics.get("call_minutes_used", 0),
                "call_minutes_limit": metrics.get("call_minutes_limit", 0),
            }

        except Exception as e:
            logger.error(f"❌ Error checking usage thresholds: {e}")
            return {
                "subscription_id": subscription_id,
                "warning_triggered": False,
                "alert_triggered": False,
                "percentage_used": 0.0,
            }

    def reset_usage_period(self, subscription_id: str) -> bool:
        """
        Reset usage for a new billing period.
        Called when a new billing cycle starts.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with get_db_context() as db:
                # Get subscription
                subscription = db.query(Subscription).filter(
                    Subscription.id == subscription_id
                ).first()

                if not subscription:
                    logger.warning(f"Subscription {subscription_id} not found")
                    return False

                # Create new usage record for new billing period
                today = datetime.utcnow()
                billing_period_start = today.replace(day=1)
                billing_period_end = (billing_period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

                new_usage = Usage(
                    subscription_id=subscription_id,
                    billing_period_start=billing_period_start,
                    billing_period_end=billing_period_end,
                    call_minutes_used=0,
                    call_minutes_limit=subscription.max_minutes_per_month,
                )
                db.add(new_usage)
                db.commit()

                logger.info(f"✅ Reset usage period for subscription {subscription_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error resetting usage period: {e}")
            return False

    def get_usage_summary(self, subscription_id: str, months: int = 12) -> Optional[Dict[str, Any]]:
        """
        Get usage summary for multiple billing periods.
        
        Args:
            subscription_id: Subscription ID
            months: Number of months to include (default 12)
            
        Returns:
            Usage summary dict or None if error
        """
        try:
            with get_db_context() as db:
                # Get all usage records for the past N months
                cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
                
                usage_records = db.query(Usage).filter(
                    Usage.subscription_id == subscription_id,
                    Usage.billing_period_start >= cutoff_date
                ).order_by(Usage.billing_period_start.desc()).all()

                if not usage_records:
                    logger.info(f"No usage records found for subscription {subscription_id}")
                    return {
                        "subscription_id": str(subscription_id),
                        "total_call_minutes": 0,
                        "average_monthly_minutes": 0.0,
                        "periods": [],
                    }

                # Calculate totals
                total_minutes = sum(u.call_minutes_used for u in usage_records)
                average_monthly = total_minutes / len(usage_records) if usage_records else 0

                # Build period list
                periods = []
                for usage in usage_records:
                    periods.append({
                        "period_start": usage.billing_period_start.isoformat() if usage.billing_period_start else None,
                        "period_end": usage.billing_period_end.isoformat() if usage.billing_period_end else None,
                        "call_minutes_used": usage.call_minutes_used,
                        "call_minutes_limit": usage.call_minutes_limit,
                    })

                summary = {
                    "subscription_id": str(subscription_id),
                    "total_call_minutes": total_minutes,
                    "average_monthly_minutes": round(average_monthly, 2),
                    "periods": periods,
                }

                logger.info(f"✅ Retrieved usage summary for subscription {subscription_id}")
                return summary

        except Exception as e:
            logger.error(f"❌ Error getting usage summary: {e}")
            return None
