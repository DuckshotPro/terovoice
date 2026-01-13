"""
Usage metrics tracking and retrieval service.
Handles recording call usage and calculating metrics vs plan limits.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

try:
    from .cache import get_cache, SubscriptionCache
except ImportError:
    from cache import get_cache, SubscriptionCache

logger = logging.getLogger(__name__)


class PlanTier(str, Enum):
    """Plan tier enumeration."""
    SOLO_PRO = "Solo Pro"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"


class UsageThreshold(str, Enum):
    """Usage threshold levels."""
    NORMAL = "NORMAL"  # < 80%
    WARNING = "WARNING"  # 80-99%
    ALERT = "ALERT"  # >= 100%


class PlanLimits:
    """Plan limits configuration."""
    
    LIMITS = {
        PlanTier.SOLO_PRO: {
            "call_minutes": 1000,
            "multi_location_support": 1,
            "priority_support": False,
            "dedicated_account": False,
        },
        PlanTier.PROFESSIONAL: {
            "call_minutes": 3000,
            "multi_location_support": 3,
            "priority_support": True,
            "dedicated_account": False,
        },
        PlanTier.ENTERPRISE: {
            "call_minutes": 10000,
            "multi_location_support": 10,
            "priority_support": True,
            "dedicated_account": True,
        },
    }
    
    @classmethod
    def get_limits(cls, plan_tier: PlanTier) -> Dict[str, Any]:
        """Get limits for a plan tier."""
        return cls.LIMITS.get(plan_tier, cls.LIMITS[PlanTier.SOLO_PRO])


class UsageMetrics:
    """Data class for usage metrics."""
    
    def __init__(
        self,
        customer_id: str,
        plan_tier: PlanTier,
        call_minutes_used: int,
        call_minutes_limit: int,
        percentage_used: float,
        threshold: UsageThreshold,
        billing_period_start: str,
        billing_period_end: str,
        features: List[Dict[str, Any]],
        last_updated: str,
    ):
        """Initialize usage metrics."""
        self.customer_id = customer_id
        self.plan_tier = plan_tier
        self.call_minutes_used = call_minutes_used
        self.call_minutes_limit = call_minutes_limit
        self.percentage_used = percentage_used
        self.threshold = threshold
        self.billing_period_start = billing_period_start
        self.billing_period_end = billing_period_end
        self.features = features
        self.last_updated = last_updated
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_id": self.customer_id,
            "plan_tier": self.plan_tier.value,
            "call_minutes_used": self.call_minutes_used,
            "call_minutes_limit": self.call_minutes_limit,
            "percentage_used": round(self.percentage_used, 2),
            "threshold": self.threshold.value,
            "billing_period_start": self.billing_period_start,
            "billing_period_end": self.billing_period_end,
            "features": self.features,
            "last_updated": self.last_updated,
        }


class UsageService:
    """
    Service for tracking and retrieving usage metrics.
    Handles call minute tracking, threshold checking, and feature usage.
    """
    
    def __init__(self, database=None, cache: Optional[SubscriptionCache] = None):
        """
        Initialize usage service.
        
        Args:
            database: Database connection (optional for testing)
            cache: Cache instance (uses global if None)
        """
        self.database = database
        self.cache = cache or get_cache()
        self.logger = logging.getLogger(__name__)
    
    async def record_usage(
        self,
        customer_id: str,
        call_duration_minutes: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record call usage for a customer.
        
        Args:
            customer_id: Customer ID
            call_duration_minutes: Duration of call in minutes
            metadata: Optional metadata (phone number, location, etc.)
        """
        self.logger.info(
            f"Recording usage: customer={customer_id}, "
            f"duration={call_duration_minutes} minutes"
        )
        
        # In production, this would insert into database
        # For now, we'll use cache for testing
        usage_key = self._get_usage_key(customer_id)
        
        # Get current usage from cache or initialize
        current_usage = self.cache.get(usage_key) or {
            "customer_id": customer_id,
            "call_minutes_used": 0.0,
            "call_count": 0,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }
        
        # Update usage
        current_usage["call_minutes_used"] += call_duration_minutes
        current_usage["call_count"] += 1
        current_usage["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        # Cache with 5-minute TTL (matches real-time update requirement)
        self.cache.set(
            usage_key,
            current_usage,
            ttl_seconds=SubscriptionCache.DEFAULT_USAGE_TTL,
        )
        
        self.logger.info(
            f"Usage recorded: total={current_usage['call_minutes_used']} minutes, "
            f"calls={current_usage['call_count']}"
        )
    
    async def get_usage_metrics(
        self,
        customer_id: str,
        plan_tier: str,
    ) -> UsageMetrics:
        """
        Get usage metrics for a customer.
        
        Args:
            customer_id: Customer ID
            plan_tier: Plan tier name (Solo Pro, Professional, Enterprise)
            
        Returns:
            UsageMetrics object
        """
        self.logger.info(f"Getting usage metrics: customer={customer_id}, plan={plan_tier}")
        
        # Convert plan tier string to enum
        try:
            plan_enum = PlanTier(plan_tier)
        except ValueError:
            self.logger.warning(f"Invalid plan tier: {plan_tier}, defaulting to Solo Pro")
            plan_enum = PlanTier.SOLO_PRO
        
        # Get plan limits
        limits = PlanLimits.get_limits(plan_enum)
        call_minutes_limit = limits["call_minutes"]
        
        # Get current usage from cache or database
        usage_key = self._get_usage_key(customer_id)
        usage_data = self.cache.get(usage_key)
        
        if not usage_data:
            # No usage recorded yet
            call_minutes_used = 0
            last_updated = datetime.utcnow().isoformat() + "Z"
        else:
            call_minutes_used = int(usage_data.get("call_minutes_used", 0))
            last_updated = usage_data.get("last_updated", datetime.utcnow().isoformat() + "Z")
        
        # Calculate percentage
        percentage_used = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
        
        # Determine threshold
        threshold = self._determine_threshold(percentage_used)
        
        # Build features list
        features = self._build_features_list(plan_enum, limits)
        
        # Get billing period (current month)
        now = datetime.utcnow()
        billing_period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Next month's first day
        if now.month == 12:
            billing_period_end = billing_period_start.replace(year=now.year + 1, month=1)
        else:
            billing_period_end = billing_period_start.replace(month=now.month + 1)
        
        return UsageMetrics(
            customer_id=customer_id,
            plan_tier=plan_enum,
            call_minutes_used=call_minutes_used,
            call_minutes_limit=call_minutes_limit,
            percentage_used=percentage_used,
            threshold=threshold,
            billing_period_start=billing_period_start.isoformat() + "Z",
            billing_period_end=billing_period_end.isoformat() + "Z",
            features=features,
            last_updated=last_updated,
        )
    
    def _determine_threshold(self, percentage_used: float) -> UsageThreshold:
        """
        Determine usage threshold based on percentage.
        
        Args:
            percentage_used: Percentage of plan limit used
            
        Returns:
            UsageThreshold enum
        """
        if percentage_used >= 100:
            return UsageThreshold.ALERT
        elif percentage_used >= 80:
            return UsageThreshold.WARNING
        else:
            return UsageThreshold.NORMAL
    
    def _build_features_list(
        self,
        plan_tier: PlanTier,
        limits: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Build features list for plan tier.
        
        Args:
            plan_tier: Plan tier enum
            limits: Plan limits dictionary
            
        Returns:
            List of feature dictionaries
        """
        features = [
            {
                "name": "Call Minutes",
                "included": True,
                "limit": limits["call_minutes"],
                "description": f"{limits['call_minutes']} minutes per month",
            },
            {
                "name": "Multi-Location Support",
                "included": True,
                "limit": limits["multi_location_support"],
                "description": f"Up to {limits['multi_location_support']} locations",
            },
            {
                "name": "Priority Support",
                "included": limits["priority_support"],
                "description": "24/7 priority email and phone support",
            },
            {
                "name": "Dedicated Account Manager",
                "included": limits["dedicated_account"],
                "description": "Personal account manager for onboarding and support",
            },
        ]
        
        return features
    
    def _get_usage_key(self, customer_id: str) -> str:
        """Generate cache key for usage data."""
        return f"usage:{customer_id}"
    
    async def check_usage_thresholds(
        self,
        customer_id: str,
        plan_tier: str,
    ) -> Dict[str, Any]:
        """
        Check if usage exceeds thresholds (80%, 100%).
        
        Args:
            customer_id: Customer ID
            plan_tier: Plan tier name
            
        Returns:
            Dictionary with threshold status and messages
        """
        metrics = await self.get_usage_metrics(customer_id, plan_tier)
        
        result = {
            "threshold": metrics.threshold.value,
            "percentage_used": metrics.percentage_used,
            "should_warn": metrics.threshold == UsageThreshold.WARNING,
            "should_alert": metrics.threshold == UsageThreshold.ALERT,
            "message": None,
            "upgrade_suggested": False,
        }
        
        if metrics.threshold == UsageThreshold.ALERT:
            result["message"] = (
                f"You've used {metrics.call_minutes_used} of {metrics.call_minutes_limit} "
                f"minutes ({metrics.percentage_used:.1f}%). Consider upgrading your plan."
            )
            result["upgrade_suggested"] = True
        elif metrics.threshold == UsageThreshold.WARNING:
            result["message"] = (
                f"You've used {metrics.call_minutes_used} of {metrics.call_minutes_limit} "
                f"minutes ({metrics.percentage_used:.1f}%). You're approaching your limit."
            )
        
        return result
    
    def invalidate_usage_cache(self, customer_id: str) -> None:
        """
        Invalidate usage cache for a customer.
        
        Args:
            customer_id: Customer ID
        """
        usage_key = self._get_usage_key(customer_id)
        self.cache.delete(usage_key)
        self.logger.info(f"Invalidated usage cache: {customer_id}")
