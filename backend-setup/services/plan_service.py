"""
Plan upgrade/downgrade service for managing subscription plan changes.

Handles:
- Plan change validation
- Pricing calculations with prorations
- PayPal subscription updates
- Effective date handling
- Plan comparison and recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Tuple
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)


class PlanTier(Enum):
    """Available subscription plan tiers."""
    SOLO_PRO = "solo_pro"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PlanChangeType(Enum):
    """Type of plan change."""
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    LATERAL = "lateral"  # Same tier, different billing cycle


@dataclass
class PlanConfig:
    """Configuration for a subscription plan tier."""
    tier: PlanTier
    name: str
    monthly_price: Decimal
    annual_price: Decimal
    call_minutes_limit: int
    features: List[str] = field(default_factory=list)
    support_level: str = "email"  # email, priority, dedicated
    multi_location_limit: int = 1
    custom_prompts_limit: int = 10
    api_access: bool = False
    sso_enabled: bool = False

    def get_daily_rate(self) -> Decimal:
        """Calculate daily rate for prorations (monthly price / 30)."""
        return (self.monthly_price / Decimal(30)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    def get_hourly_rate(self) -> Decimal:
        """Calculate hourly rate for prorations (daily rate / 24)."""
        return (self.get_daily_rate() / Decimal(24)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )


@dataclass
class PricingCalculation:
    """Result of pricing calculation for plan change."""
    current_plan: PlanConfig
    new_plan: PlanConfig
    change_type: PlanChangeType

    # Pricing details
    current_plan_price: Decimal
    new_plan_price: Decimal
    price_difference: Decimal

    # Proration details
    days_remaining_in_cycle: int
    current_plan_daily_rate: Decimal
    new_plan_daily_rate: Decimal

    # Proration credit (negative = credit, positive = charge)
    proration_credit: Decimal

    # Final amount due
    amount_due: Decimal

    # Effective date
    effective_date: datetime
    next_billing_date: datetime

    # Metadata
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_summary(self) -> Dict:
        """Get human-readable summary of pricing calculation."""
        return {
            "current_plan": self.current_plan.name,
            "new_plan": self.new_plan.name,
            "change_type": self.change_type.value,
            "current_monthly_price": float(self.current_plan_price),
            "new_monthly_price": float(self.new_plan_price),
            "price_difference": float(self.price_difference),
            "days_remaining": self.days_remaining_in_cycle,
            "proration_credit": float(self.proration_credit),
            "amount_due": float(self.amount_due),
            "effective_date": self.effective_date.isoformat(),
            "next_billing_date": self.next_billing_date.isoformat(),
        }


@dataclass
class PlanChangeResult:
    """Result of a plan change operation."""
    success: bool
    plan_change_id: str
    subscription_id: str
    old_plan: PlanConfig
    new_plan: PlanConfig
    pricing: PricingCalculation
    paypal_subscription_id: str
    effective_date: datetime
    next_billing_date: datetime
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response."""
        return {
            "success": self.success,
            "plan_change_id": self.plan_change_id,
            "subscription_id": self.subscription_id,
            "old_plan": self.old_plan.name,
            "new_plan": self.new_plan.name,
            "pricing": self.pricing.get_summary(),
            "effective_date": self.effective_date.isoformat(),
            "next_billing_date": self.next_billing_date.isoformat(),
            "error_message": self.error_message,
            "error_code": self.error_code,
        }


class PlanService:
    """Service for managing subscription plan changes."""

    # Plan configurations
    PLANS = {
        PlanTier.SOLO_PRO: PlanConfig(
            tier=PlanTier.SOLO_PRO,
            name="Solo Pro",
            monthly_price=Decimal("299.00"),
            annual_price=Decimal("2990.00"),
            call_minutes_limit=1000,
            features=[
                "AI Receptionist",
                "Call Answering",
                "Basic Scheduling",
                "Email Support",
            ],
            support_level="email",
            multi_location_limit=1,
            custom_prompts_limit=10,
            api_access=False,
            sso_enabled=False,
        ),
        PlanTier.PROFESSIONAL: PlanConfig(
            tier=PlanTier.PROFESSIONAL,
            name="Professional",
            monthly_price=Decimal("499.00"),
            annual_price=Decimal("4990.00"),
            call_minutes_limit=5000,
            features=[
                "AI Receptionist",
                "Call Answering",
                "Advanced Scheduling",
                "CRM Integration",
                "Priority Support",
                "Multi-Location (up to 3)",
                "Custom Prompts (up to 50)",
            ],
            support_level="priority",
            multi_location_limit=3,
            custom_prompts_limit=50,
            api_access=True,
            sso_enabled=False,
        ),
        PlanTier.ENTERPRISE: PlanConfig(
            tier=PlanTier.ENTERPRISE,
            name="Enterprise",
            monthly_price=Decimal("799.00"),
            annual_price=Decimal("7990.00"),
            call_minutes_limit=20000,
            features=[
                "AI Receptionist",
                "Call Answering",
                "Advanced Scheduling",
                "CRM Integration",
                "Dedicated Support",
                "Unlimited Locations",
                "Unlimited Custom Prompts",
                "Advanced Analytics",
                "Custom Integrations",
                "SLA Guarantee",
            ],
            support_level="dedicated",
            multi_location_limit=999,  # Effectively unlimited
            custom_prompts_limit=999,  # Effectively unlimited
            api_access=True,
            sso_enabled=True,
        ),
    }

    def __init__(self, paypal_client=None, cache=None):
        """
        Initialize PlanService.

        Args:
            paypal_client: PayPal API client for subscription updates
            cache: Cache service for storing plan change data
        """
        self.paypal_client = paypal_client
        self.cache = cache

    def get_plan(self, tier: PlanTier) -> PlanConfig:
        """
        Get plan configuration by tier.

        Args:
            tier: Plan tier to retrieve

        Returns:
            PlanConfig for the tier

        Raises:
            ValueError: If tier is invalid
        """
        if tier not in self.PLANS:
            raise ValueError(f"Invalid plan tier: {tier}")
        return self.PLANS[tier]

    def get_all_plans(self) -> List[PlanConfig]:
        """Get all available plans."""
        return list(self.PLANS.values())

    def get_plan_by_name(self, name: str) -> Optional[PlanConfig]:
        """Get plan configuration by name."""
        for plan in self.PLANS.values():
            if plan.name.lower() == name.lower():
                return plan
        return None

    def calculate_plan_change(
        self,
        current_plan: PlanTier,
        new_plan: PlanTier,
        current_billing_date: datetime,
        next_billing_date: datetime,
    ) -> PricingCalculation:
        """
        Calculate pricing for a plan change with prorations.

        Args:
            current_plan: Current plan tier
            new_plan: New plan tier to change to
            current_billing_date: Date of current billing cycle start
            next_billing_date: Date of next billing cycle

        Returns:
            PricingCalculation with all pricing details

        Raises:
            ValueError: If plan change is invalid
        """
        if current_plan == new_plan:
            raise ValueError("Cannot change to the same plan")

        current_config = self.get_plan(current_plan)
        new_config = self.get_plan(new_plan)

        # Determine change type
        if current_config.monthly_price < new_config.monthly_price:
            change_type = PlanChangeType.UPGRADE
        else:
            change_type = PlanChangeType.DOWNGRADE

        # Calculate days remaining in current billing cycle
        now = datetime.utcnow()
        days_remaining = (next_billing_date - now).days
        if days_remaining < 0:
            days_remaining = 0

        # Calculate daily rates
        current_daily_rate = current_config.get_daily_rate()
        new_daily_rate = new_config.get_daily_rate()

        # Calculate proration credit
        # Positive = customer owes money (upgrade)
        # Negative = customer gets credit (downgrade)
        proration_credit = (new_daily_rate - current_daily_rate) * Decimal(days_remaining)
        proration_credit = proration_credit.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        # Calculate amount due
        # For upgrades: customer pays the difference
        # For downgrades: customer gets credit applied to next billing
        amount_due = proration_credit
        if amount_due < 0:
            amount_due = Decimal(0)  # Downgrade results in credit, not charge

        # Effective date is immediately
        effective_date = now

        return PricingCalculation(
            current_plan=current_config,
            new_plan=new_config,
            change_type=change_type,
            current_plan_price=current_config.monthly_price,
            new_plan_price=new_config.monthly_price,
            price_difference=new_config.monthly_price - current_config.monthly_price,
            days_remaining_in_cycle=days_remaining,
            current_plan_daily_rate=current_daily_rate,
            new_plan_daily_rate=new_daily_rate,
            proration_credit=proration_credit,
            amount_due=amount_due,
            effective_date=effective_date,
            next_billing_date=next_billing_date,
        )

    async def change_plan(
        self,
        subscription_id: str,
        paypal_subscription_id: str,
        current_plan: PlanTier,
        new_plan: PlanTier,
        current_billing_date: datetime,
        next_billing_date: datetime,
    ) -> PlanChangeResult:
        """
        Execute a plan change with PayPal subscription update.

        Args:
            subscription_id: Internal subscription ID
            paypal_subscription_id: PayPal subscription ID
            current_plan: Current plan tier
            new_plan: New plan tier
            current_billing_date: Current billing cycle start date
            next_billing_date: Next billing cycle date

        Returns:
            PlanChangeResult with success status and details
        """
        try:
            # Validate plan change
            if current_plan == new_plan:
                return PlanChangeResult(
                    success=False,
                    plan_change_id="",
                    subscription_id=subscription_id,
                    old_plan=self.get_plan(current_plan),
                    new_plan=self.get_plan(new_plan),
                    pricing=None,
                    paypal_subscription_id=paypal_subscription_id,
                    effective_date=datetime.utcnow(),
                    next_billing_date=next_billing_date,
                    error_message="Cannot change to the same plan",
                    error_code="SAME_PLAN",
                )

            # Calculate pricing
            pricing = self.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )

            # Update PayPal subscription
            if self.paypal_client:
                try:
                    new_plan_config = self.get_plan(new_plan)
                    await self.paypal_client.update_subscription(
                        subscription_id=paypal_subscription_id,
                        plan_id=new_plan_config.tier.value,
                        new_price=float(new_plan_config.monthly_price),
                    )
                except Exception as e:
                    logger.error(f"PayPal subscription update failed: {e}")
                    return PlanChangeResult(
                        success=False,
                        plan_change_id="",
                        subscription_id=subscription_id,
                        old_plan=self.get_plan(current_plan),
                        new_plan=self.get_plan(new_plan),
                        pricing=pricing,
                        paypal_subscription_id=paypal_subscription_id,
                        effective_date=datetime.utcnow(),
                        next_billing_date=next_billing_date,
                        error_message=f"Failed to update PayPal subscription: {str(e)}",
                        error_code="PAYPAL_UPDATE_FAILED",
                    )

            # Generate plan change ID
            plan_change_id = f"pc_{subscription_id}_{datetime.utcnow().timestamp()}"

            # Cache the plan change
            if self.cache:
                cache_key = f"plan_change:{subscription_id}"
                await self.cache.set(
                    cache_key,
                    {
                        "plan_change_id": plan_change_id,
                        "subscription_id": subscription_id,
                        "old_plan": current_plan.value,
                        "new_plan": new_plan.value,
                        "pricing": pricing.get_summary(),
                        "effective_date": pricing.effective_date.isoformat(),
                        "next_billing_date": pricing.next_billing_date.isoformat(),
                    },
                    ttl=86400,  # 24 hours
                )

            logger.info(
                f"Plan change successful: {subscription_id} "
                f"{current_plan.value} -> {new_plan.value}"
            )

            return PlanChangeResult(
                success=True,
                plan_change_id=plan_change_id,
                subscription_id=subscription_id,
                old_plan=self.get_plan(current_plan),
                new_plan=self.get_plan(new_plan),
                pricing=pricing,
                paypal_subscription_id=paypal_subscription_id,
                effective_date=pricing.effective_date,
                next_billing_date=pricing.next_billing_date,
            )

        except Exception as e:
            logger.error(f"Plan change failed: {e}", exc_info=True)
            return PlanChangeResult(
                success=False,
                plan_change_id="",
                subscription_id=subscription_id,
                old_plan=self.get_plan(current_plan),
                new_plan=self.get_plan(new_plan),
                pricing=None,
                paypal_subscription_id=paypal_subscription_id,
                effective_date=datetime.utcnow(),
                next_billing_date=next_billing_date,
                error_message=f"Unexpected error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    def compare_plans(self, plan1: PlanTier, plan2: PlanTier) -> Dict:
        """
        Compare two plans side-by-side.

        Args:
            plan1: First plan to compare
            plan2: Second plan to compare

        Returns:
            Dictionary with comparison details
        """
        config1 = self.get_plan(plan1)
        config2 = self.get_plan(plan2)

        return {
            "plan1": {
                "name": config1.name,
                "price": float(config1.monthly_price),
                "call_minutes": config1.call_minutes_limit,
                "features": config1.features,
                "support": config1.support_level,
            },
            "plan2": {
                "name": config2.name,
                "price": float(config2.monthly_price),
                "call_minutes": config2.call_minutes_limit,
                "features": config2.features,
                "support": config2.support_level,
            },
            "price_difference": float(config2.monthly_price - config1.monthly_price),
            "call_minutes_difference": config2.call_minutes_limit - config1.call_minutes_limit,
        }

    def get_upgrade_recommendations(self, current_plan: PlanTier) -> List[Dict]:
        """
        Get upgrade recommendations for a plan.

        Args:
            current_plan: Current plan tier

        Returns:
            List of upgrade options with details
        """
        current_config = self.get_plan(current_plan)
        recommendations = []

        for tier, config in self.PLANS.items():
            if config.monthly_price > current_config.monthly_price:
                recommendations.append({
                    "plan": config.name,
                    "tier": tier.value,
                    "price": float(config.monthly_price),
                    "price_increase": float(config.monthly_price - current_config.monthly_price),
                    "call_minutes_increase": config.call_minutes_limit - current_config.call_minutes_limit,
                    "new_features": [
                        f for f in config.features
                        if f not in current_config.features
                    ],
                })

        return recommendations

    def validate_plan_change(
        self,
        current_plan: PlanTier,
        new_plan: PlanTier,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a plan change is allowed.

        Args:
            current_plan: Current plan tier
            new_plan: New plan tier

        Returns:
            Tuple of (is_valid, error_message)
        """
        if current_plan not in self.PLANS:
            return False, f"Invalid current plan: {current_plan}"

        if new_plan not in self.PLANS:
            return False, f"Invalid new plan: {new_plan}"

        if current_plan == new_plan:
            return False, "Cannot change to the same plan"

        return True, None
