"""
Payment method management service.
Handles payment method updates, display, and PayPal redirect flows.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

try:
    from .cache import get_cache, SubscriptionCache
except ImportError:
    from cache import get_cache, SubscriptionCache

logger = logging.getLogger(__name__)


class PaymentMethodType(str, Enum):
    """Payment method type enumeration."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_ACCOUNT = "bank_account"


class PaymentMethodData:
    """Data class for payment method information."""
    
    def __init__(
        self,
        payment_method_id: str,
        subscription_id: str,
        method_type: PaymentMethodType,
        last_four_digits: Optional[str],
        card_brand: Optional[str],
        expiry_month: Optional[int],
        expiry_year: Optional[int],
        billing_email: Optional[str],
        updated_at: str,
        is_default: bool = True,
    ):
        """Initialize payment method data."""
        self.payment_method_id = payment_method_id
        self.subscription_id = subscription_id
        self.method_type = method_type
        self.last_four_digits = last_four_digits
        self.card_brand = card_brand
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.billing_email = billing_email
        self.updated_at = updated_at
        self.is_default = is_default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "payment_method_id": self.payment_method_id,
            "subscription_id": self.subscription_id,
            "method_type": self.method_type.value,
            "last_four_digits": self.last_four_digits,
            "card_brand": self.card_brand,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "billing_email": self.billing_email,
            "updated_at": self.updated_at,
            "is_default": self.is_default,
        }
    
    def get_display_name(self) -> str:
        """Get human-readable display name for payment method."""
        if self.method_type == PaymentMethodType.PAYPAL:
            return f"PayPal ({self.billing_email})"
        elif self.last_four_digits and self.card_brand:
            return f"{self.card_brand} ending in {self.last_four_digits}"
        elif self.method_type == PaymentMethodType.BANK_ACCOUNT:
            return f"Bank account ending in {self.last_four_digits}"
        else:
            return "Payment method"
    
    def is_expired(self) -> bool:
        """Check if payment method is expired (for cards)."""
        if self.expiry_month is None or self.expiry_year is None:
            return False
        
        now = datetime.utcnow()
        # Card expires at end of expiry month
        if self.expiry_year < now.year:
            return True
        if self.expiry_year == now.year and self.expiry_month < now.month:
            return True
        
        return False


class PaymentUpdateResult:
    """Result of payment method update operation."""
    
    def __init__(
        self,
        success: bool,
        redirect_url: Optional[str] = None,
        error_message: Optional[str] = None,
        payment_method: Optional[PaymentMethodData] = None,
    ):
        """Initialize payment update result."""
        self.success = success
        self.redirect_url = redirect_url
        self.error_message = error_message
        self.payment_method = payment_method
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "success": self.success,
        }
        
        if self.redirect_url:
            result["redirect_url"] = self.redirect_url
        
        if self.error_message:
            result["error_message"] = self.error_message
        
        if self.payment_method:
            result["payment_method"] = self.payment_method.to_dict()
        
        return result


class PaymentService:
    """
    Service for payment method management.
    Handles payment method updates, display, and PayPal integration.
    """
    
    def __init__(
        self,
        database=None,
        paypal_client=None,
        cache: Optional[SubscriptionCache] = None,
    ):
        """
        Initialize payment service.
        
        Args:
            database: Database connection (optional for testing)
            paypal_client: PayPal API client (optional for testing)
            cache: Cache instance (uses global if None)
        """
        self.database = database
        self.paypal_client = paypal_client
        self.cache = cache or get_cache()
        self.logger = logging.getLogger(__name__)
    
    async def get_payment_method(
        self,
        customer_id: str,
        subscription_id: str,
    ) -> Optional[PaymentMethodData]:
        """
        Get current payment method for a subscription.
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            
        Returns:
            PaymentMethodData object or None if not found
        """
        self.logger.info(f"Getting payment method: customer={customer_id}, subscription={subscription_id}")
        
        # Check cache first
        cache_key = f"payment_method:{subscription_id}"
        cached_method = self.cache.get(cache_key)
        
        if cached_method is not None:
            self.logger.info(f"Payment method cache HIT: {subscription_id}")
            return PaymentMethodData(**cached_method)
        
        # In production, query PayPal API for payment method details
        # For now, use mock data
        payment_method = self._get_payment_method_from_paypal(subscription_id)
        
        if payment_method:
            # Cache for 1 hour (payment methods don't change often)
            self.cache.set(cache_key, payment_method.to_dict(), ttl_seconds=3600)
        
        return payment_method
    
    def _get_payment_method_from_paypal(
        self,
        subscription_id: str,
    ) -> Optional[PaymentMethodData]:
        """
        Get payment method from PayPal API.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            PaymentMethodData object or None
        """
        # In production, this would call PayPal API:
        # response = self.paypal_client.get_subscription(subscription_id)
        # payment_details = response['billing_info']['last_payment']
        
        # Mock data for testing
        return PaymentMethodData(
            payment_method_id=f"PM-{subscription_id}",
            subscription_id=subscription_id,
            method_type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="4242",
            card_brand="Visa",
            expiry_month=12,
            expiry_year=2025,
            billing_email="customer@example.com",
            updated_at=datetime.utcnow().isoformat() + "Z",
            is_default=True,
        )
    
    async def initiate_payment_method_update(
        self,
        customer_id: str,
        subscription_id: str,
        return_url: str,
        cancel_url: str,
    ) -> PaymentUpdateResult:
        """
        Initiate payment method update flow.
        Returns redirect URL to PayPal for customer to update payment method.
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            return_url: URL to redirect after successful update
            cancel_url: URL to redirect if customer cancels
            
        Returns:
            PaymentUpdateResult with redirect URL
        """
        self.logger.info(f"Initiating payment update: customer={customer_id}, subscription={subscription_id}")
        
        try:
            # In production, call PayPal API to get update URL
            # response = self.paypal_client.create_payment_update_link(
            #     subscription_id=subscription_id,
            #     return_url=return_url,
            #     cancel_url=cancel_url,
            # )
            # redirect_url = response['links'][0]['href']
            
            # Mock redirect URL for testing
            redirect_url = f"https://www.paypal.com/billing/subscriptions/{subscription_id}/update?return_url={return_url}&cancel_url={cancel_url}"
            
            return PaymentUpdateResult(
                success=True,
                redirect_url=redirect_url,
            )
        
        except Exception as e:
            self.logger.error(f"Payment update initiation failed: {e}")
            return PaymentUpdateResult(
                success=False,
                error_message=f"Failed to initiate payment update: {str(e)}",
            )
    
    async def complete_payment_method_update(
        self,
        customer_id: str,
        subscription_id: str,
        payment_token: Optional[str] = None,
    ) -> PaymentUpdateResult:
        """
        Complete payment method update after customer returns from PayPal.
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            payment_token: Payment token from PayPal callback (optional)
            
        Returns:
            PaymentUpdateResult with updated payment method
        """
        self.logger.info(f"Completing payment update: customer={customer_id}, subscription={subscription_id}")
        
        try:
            # Invalidate cache to force fresh fetch
            cache_key = f"payment_method:{subscription_id}"
            self.cache.delete(cache_key)
            
            # Fetch updated payment method from PayPal
            payment_method = await self.get_payment_method(customer_id, subscription_id)
            
            if payment_method:
                return PaymentUpdateResult(
                    success=True,
                    payment_method=payment_method,
                )
            else:
                return PaymentUpdateResult(
                    success=False,
                    error_message="Failed to retrieve updated payment method",
                )
        
        except Exception as e:
            self.logger.error(f"Payment update completion failed: {e}")
            return PaymentUpdateResult(
                success=False,
                error_message=f"Failed to complete payment update: {str(e)}",
            )
    
    async def handle_payment_failure(
        self,
        customer_id: str,
        subscription_id: str,
        failure_reason: str,
    ) -> Dict[str, Any]:
        """
        Handle payment failure notification.
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID
            failure_reason: Reason for payment failure
            
        Returns:
            Dictionary with failure details and recommended actions
        """
        self.logger.warning(f"Payment failure: customer={customer_id}, reason={failure_reason}")
        
        # Get current payment method to check if expired
        payment_method = await self.get_payment_method(customer_id, subscription_id)
        
        is_expired = payment_method.is_expired() if payment_method else False
        
        return {
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "failure_reason": failure_reason,
            "payment_method_expired": is_expired,
            "recommended_action": "update_payment_method" if is_expired else "contact_bank",
            "message": self._get_failure_message(failure_reason, is_expired),
        }
    
    def _get_failure_message(self, failure_reason: str, is_expired: bool) -> str:
        """
        Get user-friendly failure message.
        
        Args:
            failure_reason: Technical failure reason
            is_expired: Whether payment method is expired
            
        Returns:
            User-friendly message
        """
        if is_expired:
            return "Your payment method has expired. Please update your payment information to continue your subscription."
        
        failure_messages = {
            "insufficient_funds": "Your payment was declined due to insufficient funds. Please update your payment method or contact your bank.",
            "card_declined": "Your card was declined. Please update your payment method or contact your bank.",
            "expired_card": "Your card has expired. Please update your payment information.",
            "invalid_card": "Your card information is invalid. Please update your payment method.",
            "processing_error": "There was an error processing your payment. Please try again or contact support.",
        }
        
        return failure_messages.get(
            failure_reason.lower(),
            "Your payment could not be processed. Please update your payment method or contact support.",
        )
    
    def invalidate_payment_method_cache(self, subscription_id: str) -> None:
        """
        Invalidate payment method cache.
        Called when payment method is updated via webhook.
        
        Args:
            subscription_id: Subscription ID
        """
        cache_key = f"payment_method:{subscription_id}"
        self.cache.delete(cache_key)
        self.logger.info(f"Invalidated payment method cache: {subscription_id}")
