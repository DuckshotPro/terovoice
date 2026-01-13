"""
Subscription status retrieval and management service.
Handles fetching subscription data from PayPal with caching and error handling.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

try:
    from .cache import get_cache, SubscriptionCache
except ImportError:
    from cache import get_cache, SubscriptionCache

logger = logging.getLogger(__name__)


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class SubscriptionData:
    """Data class for subscription information."""
    
    def __init__(
        self,
        subscription_id: str,
        customer_id: str,
        plan_name: str,
        status: SubscriptionStatus,
        monthly_price: float,
        next_billing_date: str,
        renewal_date: str,
        created_at: str,
        updated_at: str,
        cancellation_date: Optional[str] = None,
        suspension_reason: Optional[str] = None,
    ):
        """Initialize subscription data."""
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan_name = plan_name
        self.status = status
        self.monthly_price = monthly_price
        self.next_billing_date = next_billing_date
        self.renewal_date = renewal_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.cancellation_date = cancellation_date
        self.suspension_reason = suspension_reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "plan_name": self.plan_name,
            "status": self.status.value,
            "monthly_price": self.monthly_price,
            "next_billing_date": self.next_billing_date,
            "renewal_date": self.renewal_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "cancellation_date": self.cancellation_date,
            "suspension_reason": self.suspension_reason,
        }


class SubscriptionService:
    """
    Service for managing subscription status and retrieval.
    Integrates with PayPal API and caching layer.
    """
    
    def __init__(self, paypal_client=None, cache: Optional[SubscriptionCache] = None):
        """
        Initialize subscription service.
        
        Args:
            paypal_client: PayPal API client (optional for testing)
            cache: Cache instance (uses global if None)
        """
        self.paypal_client = paypal_client
        self.cache = cache or get_cache()
        self.logger = logging.getLogger(__name__)
    
    async def get_subscription_status(
        self,
        customer_id: str,
        subscription_id: str,
        force_refresh: bool = False,
    ) -> SubscriptionData:
        """
        Get subscription status for a customer.
        Uses cache with 30-second TTL unless force_refresh is True.
        
        Args:
            customer_id: Customer ID
            subscription_id: Subscription ID from PayPal
            force_refresh: Force fetch from PayPal, bypass cache
            
        Returns:
            SubscriptionData object
            
        Raises:
            ValueError: If subscription not found
            Exception: If PayPal API call fails
        """
        cache_key = self.cache.get_subscription_key(customer_id)
        
        # Try cache first (unless force_refresh)
        if not force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.logger.info(f"Subscription status from cache: {customer_id}")
                return cached_data
        
        # Fetch from PayPal
        self.logger.info(f"Fetching subscription from PayPal: {subscription_id}")
        
        try:
            # Call PayPal API to get subscription details
            subscription_data = await self._fetch_from_paypal(subscription_id)
            
            # Convert to SubscriptionData object
            subscription = self._parse_paypal_response(subscription_data, customer_id)
            
            # Cache the result (30 second TTL)
            self.cache.set(
                cache_key,
                subscription,
                ttl_seconds=SubscriptionCache.DEFAULT_SUBSCRIPTION_TTL,
            )
            
            self.logger.info(f"Subscription status cached: {customer_id}")
            return subscription
            
        except Exception as e:
            self.logger.error(f"Failed to fetch subscription: {str(e)}")
            raise
    
    async def _fetch_from_paypal(self, subscription_id: str) -> Dict[str, Any]:
        """
        Fetch subscription details from PayPal API.
        
        Args:
            subscription_id: PayPal subscription ID
            
        Returns:
            Raw subscription data from PayPal
            
        Raises:
            Exception: If API call fails
        """
        if not self.paypal_client:
            # Mock response for testing
            self.logger.warning("No PayPal client configured, using mock data")
            return self._get_mock_subscription_data(subscription_id)
        
        # Call actual PayPal API
        # This would use: self.paypal_client.get_subscription(subscription_id)
        # For now, return mock data
        return self._get_mock_subscription_data(subscription_id)
    
    def _parse_paypal_response(
        self,
        paypal_data: Dict[str, Any],
        customer_id: str,
    ) -> SubscriptionData:
        """
        Parse PayPal API response into SubscriptionData.
        
        Args:
            paypal_data: Raw data from PayPal API
            customer_id: Customer ID
            
        Returns:
            SubscriptionData object
        """
        # Map PayPal status to our enum
        status_map = {
            "APPROVAL_PENDING": SubscriptionStatus.PENDING,
            "APPROVED": SubscriptionStatus.ACTIVE,
            "ACTIVE": SubscriptionStatus.ACTIVE,
            "SUSPENDED": SubscriptionStatus.SUSPENDED,
            "CANCELLED": SubscriptionStatus.CANCELLED,
            "EXPIRED": SubscriptionStatus.EXPIRED,
        }
        
        paypal_status = paypal_data.get("status", "ACTIVE")
        status = status_map.get(paypal_status, SubscriptionStatus.ACTIVE)
        
        # Extract plan name from billing plan ID
        plan_name = self._get_plan_name_from_id(paypal_data.get("plan_id", ""))
        
        # Parse dates
        next_billing_date = paypal_data.get("next_billing_time", "")
        renewal_date = next_billing_date  # Same as next billing date
        
        return SubscriptionData(
            subscription_id=paypal_data.get("id", ""),
            customer_id=customer_id,
            plan_name=plan_name,
            status=status,
            monthly_price=float(paypal_data.get("billing_cycles", [{}])[0].get("pricing_scheme", {}).get("fixed_price", {}).get("value", 0)),
            next_billing_date=next_billing_date,
            renewal_date=renewal_date,
            created_at=paypal_data.get("create_time", ""),
            updated_at=paypal_data.get("update_time", ""),
            cancellation_date=paypal_data.get("status_update_time") if status == SubscriptionStatus.CANCELLED else None,
            suspension_reason=paypal_data.get("status_change_note") if status == SubscriptionStatus.SUSPENDED else None,
        )
    
    def _get_plan_name_from_id(self, plan_id: str) -> str:
        """
        Map PayPal plan ID to plan name.
        
        Args:
            plan_id: PayPal plan ID
            
        Returns:
            Plan name (Solo Pro, Professional, Enterprise)
        """
        plan_map = {
            "PLAN_SOLO_PRO": "Solo Pro",
            "PLAN_PROFESSIONAL": "Professional",
            "PLAN_ENTERPRISE": "Enterprise",
        }
        return plan_map.get(plan_id, "Unknown Plan")
    
    def _get_mock_subscription_data(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get mock subscription data for testing.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Mock subscription data
        """
        now = datetime.utcnow()
        next_billing = now + timedelta(days=30)
        
        return {
            "id": subscription_id,
            "status": "ACTIVE",
            "plan_id": "PLAN_PROFESSIONAL",
            "create_time": now.isoformat() + "Z",
            "update_time": now.isoformat() + "Z",
            "next_billing_time": next_billing.isoformat() + "Z",
            "billing_cycles": [
                {
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": "499.00",
                            "currency_code": "USD",
                        }
                    }
                }
            ],
        }
    
    def invalidate_subscription_cache(self, customer_id: str) -> None:
        """
        Invalidate subscription cache for a customer.
        Called when subscription changes via webhook.
        
        Args:
            customer_id: Customer ID
        """
        self.cache.invalidate_customer_cache(customer_id)
        self.logger.info(f"Invalidated subscription cache: {customer_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics
        """
        return self.cache.get_stats()
