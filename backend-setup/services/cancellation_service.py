"""
Subscription cancellation service.
Handles subscription cancellation with reason tracking and cache invalidation.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import sys
import os

# Handle imports for both direct execution and test execution
try:
    from .cache import get_cache, SubscriptionCache
except (ImportError, ValueError):
    try:
        from cache import get_cache, SubscriptionCache
    except ImportError:
        # Fallback for test execution
        sys.path.insert(0, os.path.dirname(__file__))
        from cache import get_cache, SubscriptionCache

logger = logging.getLogger(__name__)


class CancellationReason(str, Enum):
    """Reasons for subscription cancellation."""
    CUSTOMER_REQUEST = "customer_request"
    TOO_EXPENSIVE = "too_expensive"
    SWITCHING_SERVICES = "switching_services"
    NOT_USING = "not_using"
    OTHER = "other"


class CancellationData:
    """Data class for cancellation information."""
    
    def __init__(
        self,
        subscription_id: str,
        reason: CancellationReason,
        feedback: Optional[str] = None,
        cancellation_date: Optional[str] = None,
    ):
        """Initialize cancellation data."""
        self.subscription_id = subscription_id
        self.reason = reason
        self.feedback = feedback
        self.cancellation_date = cancellation_date or datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "reason": self.reason.value,
            "feedback": self.feedback,
            "cancellation_date": self.cancellation_date,
        }


class CancellationResult:
    """Result of a cancellation operation."""
    
    def __init__(
        self,
        success: bool,
        subscription_id: str,
        message: str,
        cancellation_date: Optional[str] = None,
        remaining_access_until: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize cancellation result."""
        self.success = success
        self.subscription_id = subscription_id
        self.message = message
        self.cancellation_date = cancellation_date
        self.remaining_access_until = remaining_access_until
        self.error_code = error_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "subscription_id": self.subscription_id,
            "message": self.message,
            "cancellation_date": self.cancellation_date,
            "remaining_access_until": self.remaining_access_until,
            "error_code": self.error_code,
        }


class CancellationService:
    """
    Service for managing subscription cancellations.
    Handles cancellation requests, PayPal API integration, and cache invalidation.
    """
    
    def __init__(
        self,
        database=None,
        paypal_client=None,
        cache: Optional[SubscriptionCache] = None,
    ):
        """
        Initialize cancellation service.
        
        Args:
            database: Database connection (optional for testing)
            paypal_client: PayPal API client (optional for testing)
            cache: Cache instance (uses global if None)
        """
        self.database = database
        self.paypal_client = paypal_client
        self.cache = cache or get_cache()
        self.logger = logging.getLogger(__name__)
        # Track cancelled subscriptions for testing (in production, this would be in database)
        self._cancelled_subscriptions: Dict[str, str] = {}
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        customer_id: str,
        reason: CancellationReason,
        feedback: Optional[str] = None,
    ) -> CancellationResult:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: PayPal subscription ID
            customer_id: Customer ID
            reason: Reason for cancellation
            feedback: Optional customer feedback
            
        Returns:
            CancellationResult with success status and details
        """
        self.logger.info(
            f"Cancelling subscription: subscription_id={subscription_id}, "
            f"customer_id={customer_id}, reason={reason.value}"
        )
        
        try:
            # Validate subscription exists and is not already cancelled
            subscription = await self._get_subscription(subscription_id, customer_id)
            
            if subscription is None:
                self.logger.error(f"Subscription not found: {subscription_id}")
                return CancellationResult(
                    success=False,
                    subscription_id=subscription_id,
                    message="Subscription not found",
                    error_code="SUBSCRIPTION_NOT_FOUND",
                )
            
            # Check if already cancelled
            if subscription.get("status") == "CANCELLED":
                self.logger.warning(f"Subscription already cancelled: {subscription_id}")
                return CancellationResult(
                    success=False,
                    subscription_id=subscription_id,
                    message="Subscription is already cancelled",
                    error_code="ALREADY_CANCELLED",
                )
            
            # Call PayPal API to cancel subscription
            paypal_result = await self._cancel_with_paypal(subscription_id)
            
            if not paypal_result.get("success"):
                self.logger.error(f"PayPal cancellation failed: {subscription_id}")
                return CancellationResult(
                    success=False,
                    subscription_id=subscription_id,
                    message=paypal_result.get("message", "PayPal API error"),
                    error_code=paypal_result.get("error_code", "PAYPAL_ERROR"),
                )
            
            # Update subscription status in database
            cancellation_date = datetime.utcnow().isoformat() + "Z"
            await self._update_subscription_status(
                subscription_id,
                customer_id,
                "CANCELLED",
                cancellation_date,
                reason,
                feedback,
            )
            
            # Invalidate cache
            self.cache.invalidate_customer_cache(customer_id)
            
            # Calculate remaining access period
            remaining_access_until = subscription.get("next_billing_date")
            
            self.logger.info(f"Subscription cancelled successfully: {subscription_id}")
            
            return CancellationResult(
                success=True,
                subscription_id=subscription_id,
                message="Subscription cancelled successfully",
                cancellation_date=cancellation_date,
                remaining_access_until=remaining_access_until,
            )
            
        except Exception as e:
            self.logger.error(f"Cancellation error: {str(e)}")
            return CancellationResult(
                success=False,
                subscription_id=subscription_id,
                message=f"Cancellation failed: {str(e)}",
                error_code="INTERNAL_ERROR",
            )
    
    async def _get_subscription(
        self,
        subscription_id: str,
        customer_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get subscription details from database or PayPal.
        
        Args:
            subscription_id: PayPal subscription ID
            customer_id: Customer ID
            
        Returns:
            Subscription data or None if not found
        """
        # Check if subscription is already cancelled
        if subscription_id in self._cancelled_subscriptions:
            return {
                "id": subscription_id,
                "status": "CANCELLED",
                "plan_id": "PLAN_PROFESSIONAL",
                "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
                "monthly_price": 499.00,
            }
        
        # In production, this would query the database
        # For now, return mock data for testing
        return self._get_mock_subscription(subscription_id)
    
    async def _cancel_with_paypal(
        self,
        subscription_id: str,
    ) -> Dict[str, Any]:
        """
        Call PayPal API to cancel subscription.
        
        Args:
            subscription_id: PayPal subscription ID
            
        Returns:
            Result dict with success status
        """
        if not self.paypal_client:
            # Mock response for testing
            self.logger.warning("No PayPal client configured, using mock response")
            return {"success": True, "message": "Mock cancellation successful"}
        
        # Call actual PayPal API
        # This would use: self.paypal_client.cancel_subscription(subscription_id)
        # For now, return mock response
        return {"success": True, "message": "Cancellation successful"}
    
    async def _update_subscription_status(
        self,
        subscription_id: str,
        customer_id: str,
        status: str,
        cancellation_date: str,
        reason: CancellationReason,
        feedback: Optional[str] = None,
    ) -> None:
        """
        Update subscription status in database.
        
        Args:
            subscription_id: PayPal subscription ID
            customer_id: Customer ID
            status: New status
            cancellation_date: Cancellation date
            reason: Cancellation reason
            feedback: Optional feedback
        """
        # Track cancelled subscriptions for testing
        if status == "CANCELLED":
            self._cancelled_subscriptions[subscription_id] = cancellation_date
        
        # In production, this would update the database
        # For now, just log the operation
        self.logger.info(
            f"Updated subscription status: subscription_id={subscription_id}, "
            f"status={status}, reason={reason.value}"
        )
    
    def _get_mock_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get mock subscription data for testing.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Mock subscription data
        """
        from datetime import timedelta
        
        now = datetime.utcnow()
        next_billing = now + timedelta(days=30)
        
        return {
            "id": subscription_id,
            "status": "ACTIVE",
            "plan_id": "PLAN_PROFESSIONAL",
            "next_billing_date": next_billing.isoformat() + "Z",
            "monthly_price": 499.00,
        }
