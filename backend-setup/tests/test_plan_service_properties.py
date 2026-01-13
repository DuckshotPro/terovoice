"""
Property-based tests for PlanService.
Tests plan change pricing accuracy, proration calculations, and plan transitions.

Feature: member-portal-billing
Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
"""
import sys
import os

# Add backend-setup to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import importlib.util
from unittest.mock import patch

# Load plan_service module
spec = importlib.util.spec_from_file_location(
    "plan_service",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'plan_service.py')
)
plan_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan_module)

# Load cache module
cache_spec = importlib.util.spec_from_file_location(
    "cache",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cache.py')
)
cache_module = importlib.util.module_from_spec(cache_spec)
cache_spec.loader.exec_module(cache_module)

# Extract classes
PlanService = plan_module.PlanService
PlanTier = plan_module.PlanTier
PlanChangeType = plan_module.PlanChangeType
PricingCalculation = plan_module.PricingCalculation
PlanChangeResult = plan_module.PlanChangeResult
SubscriptionCache = cache_module.SubscriptionCache


# Test data generators
@st.composite
def plan_tiers(draw):
    """Generate random plan tier."""
    return draw(st.sampled_from(list(PlanTier)))


@st.composite
def different_plan_tiers(draw):
    """Generate two different plan tiers."""
    all_tiers = list(PlanTier)
    tier1 = draw(st.sampled_from(all_tiers))
    # Ensure tier2 is different from tier1
    tier2 = draw(st.sampled_from([t for t in all_tiers if t != tier1]))
    return tier1, tier2


@st.composite
def billing_dates(draw):
    """Generate random billing dates (current and next cycle)."""
    # Generate a date in the past (current billing cycle start)
    days_ago = draw(st.integers(min_value=1, max_value=29))
    current_billing_date = datetime.utcnow() - timedelta(days=days_ago)
    
    # Next billing date is 30 days after current
    next_billing_date = current_billing_date + timedelta(days=30)
    
    return current_billing_date, next_billing_date


class TestPlanServiceProperties:
    """Property-based tests for PlanService."""
    
    @pytest.fixture
    def plan_service(self):
        """Create plan service instance."""
        cache = SubscriptionCache()
        return PlanService(cache=cache)
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_7_plan_change_pricing_accuracy(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property 7: Plan Change Pricing Accuracy
        
        For any plan change from tier A to tier B with any billing cycle position,
        the pricing calculation SHALL:
        1. Calculate proration credit correctly: (new_daily_rate - current_daily_rate) * days_remaining
        2. For upgrades: amount_due SHALL be positive (customer pays)
        3. For downgrades: amount_due SHALL be zero (credit applied to next billing)
        4. Effective date SHALL be current time
        5. Next billing date SHALL remain unchanged
        
        Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
        Feature: member-portal-billing, Property 7: Plan Change Pricing Accuracy
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Get plan configs
        current_config = plan_service.get_plan(current_plan)
        new_config = plan_service.get_plan(new_plan)
        
        # Verify pricing calculation is correct
        assert pricing.current_plan == current_config
        assert pricing.new_plan == new_config
        assert pricing.current_plan_price == current_config.monthly_price
        assert pricing.new_plan_price == new_config.monthly_price
        
        # Verify price difference
        expected_price_diff = new_config.monthly_price - current_config.monthly_price
        assert pricing.price_difference == expected_price_diff
        
        # Verify change type
        if current_config.monthly_price < new_config.monthly_price:
            assert pricing.change_type == PlanChangeType.UPGRADE
        else:
            assert pricing.change_type == PlanChangeType.DOWNGRADE
        
        # Verify days remaining calculation (using reference time)
        expected_days_remaining = max(0, (next_billing_date - reference_time).days)
        assert pricing.days_remaining_in_cycle == expected_days_remaining
        
        # Verify daily rates
        current_daily_rate = current_config.get_daily_rate()
        new_daily_rate = new_config.get_daily_rate()
        assert pricing.current_plan_daily_rate == current_daily_rate
        assert pricing.new_plan_daily_rate == new_daily_rate
        
        # Verify proration credit calculation
        expected_proration = (new_daily_rate - current_daily_rate) * Decimal(expected_days_remaining)
        expected_proration = expected_proration.quantize(Decimal('0.01'))
        assert pricing.proration_credit == expected_proration
        
        # Verify amount due logic
        if pricing.change_type == PlanChangeType.UPGRADE:
            # Upgrade: customer pays the difference
            assert pricing.amount_due >= Decimal(0)
            assert pricing.amount_due == pricing.proration_credit
        else:
            # Downgrade: customer gets credit (amount_due is 0)
            assert pricing.amount_due == Decimal(0)
        
        # Verify effective date is the reference time
        assert pricing.effective_date == reference_time
        
        # Verify next billing date is unchanged
        assert pricing.next_billing_date == next_billing_date
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_upgrade_pricing_positive(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Upgrade Pricing Always Positive
        
        For any upgrade (lower tier to higher tier), the amount_due
        SHALL always be positive (customer pays for upgrade).
        
        Validates: Requirements 5.3, 5.4
        Feature: member-portal-billing, Property: Upgrade Pricing Positive
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Get plan configs
        current_config = plan_service.get_plan(current_plan)
        new_config = plan_service.get_plan(new_plan)
        
        # Only test upgrades (new plan is more expensive)
        assume(new_config.monthly_price > current_config.monthly_price)
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify upgrade pricing is positive
        assert pricing.change_type == PlanChangeType.UPGRADE
        assert pricing.amount_due >= Decimal(0)
        
        # For upgrades with days remaining, amount_due should be positive
        if pricing.days_remaining_in_cycle > 0:
            assert pricing.amount_due > Decimal(0)
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_downgrade_pricing_zero(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Downgrade Pricing Always Zero
        
        For any downgrade (higher tier to lower tier), the amount_due
        SHALL always be zero (customer gets credit applied to next billing).
        
        Validates: Requirements 5.5, 5.6
        Feature: member-portal-billing, Property: Downgrade Pricing Zero
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Get plan configs
        current_config = plan_service.get_plan(current_plan)
        new_config = plan_service.get_plan(new_plan)
        
        # Only test downgrades (new plan is less expensive)
        assume(new_config.monthly_price < current_config.monthly_price)
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify downgrade pricing is zero
        assert pricing.change_type == PlanChangeType.DOWNGRADE
        assert pricing.amount_due == Decimal(0)
        
        # Verify proration credit is negative or zero (customer gets credit)
        assert pricing.proration_credit <= Decimal(0)
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_proration_credit_calculation(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Proration Credit Calculation Accuracy
        
        For any plan change, the proration credit SHALL be calculated as:
        (new_daily_rate - current_daily_rate) * days_remaining
        
        Validates: Requirements 5.3, 5.4, 5.5
        Feature: member-portal-billing, Property: Proration Credit Calculation
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Manually calculate expected proration
        current_daily_rate = pricing.current_plan_daily_rate
        new_daily_rate = pricing.new_plan_daily_rate
        days_remaining = pricing.days_remaining_in_cycle
        
        expected_proration = (new_daily_rate - current_daily_rate) * Decimal(days_remaining)
        expected_proration = expected_proration.quantize(Decimal('0.01'))
        
        # Verify calculation matches
        assert pricing.proration_credit == expected_proration
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_effective_date_is_immediate(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Effective Date Is Immediate
        
        For any plan change, the effective date SHALL be the current time
        (within 1 second of calculation).
        
        Validates: Requirements 5.6
        Feature: member-portal-billing, Property: Effective Date Immediate
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify effective date is the reference time
        assert pricing.effective_date == reference_time
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_next_billing_date_unchanged(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Next Billing Date Unchanged
        
        For any plan change, the next billing date SHALL remain unchanged
        from the original subscription.
        
        Validates: Requirements 5.7
        Feature: member-portal-billing, Property: Next Billing Date Unchanged
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify next billing date is unchanged
        assert pricing.next_billing_date == next_billing_date
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_days_remaining_calculation(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Days Remaining Calculation Accuracy
        
        For any plan change, the days_remaining_in_cycle SHALL be calculated as
        the number of days between now and next_billing_date, with minimum of 0.
        
        Validates: Requirements 5.3
        Feature: member-portal-billing, Property: Days Remaining Calculation
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Calculate expected days remaining using reference time
        expected_days = max(0, (next_billing_date - reference_time).days)
        
        # Verify calculation matches
        assert pricing.days_remaining_in_cycle == expected_days
    
    @given(plan_tiers())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_plan_daily_rate_consistency(self, plan_service, plan_tier):
        """
        Property: Plan Daily Rate Consistency
        
        For any plan, the daily rate SHALL be monthly_price / 30,
        rounded to 2 decimal places.
        
        Validates: Requirements 5.3
        Feature: member-portal-billing, Property: Plan Daily Rate Consistency
        """
        plan_config = plan_service.get_plan(plan_tier)
        
        # Get daily rate
        daily_rate = plan_config.get_daily_rate()
        
        # Calculate expected daily rate
        expected_daily_rate = (plan_config.monthly_price / Decimal(30)).quantize(Decimal('0.01'))
        
        # Verify calculation matches
        assert daily_rate == expected_daily_rate
        
        # Verify daily rate is positive
        assert daily_rate > Decimal(0)
        
        # Verify daily rate is less than monthly price
        assert daily_rate < plan_config.monthly_price
    
    @given(plan_tiers())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_plan_hourly_rate_consistency(self, plan_service, plan_tier):
        """
        Property: Plan Hourly Rate Consistency
        
        For any plan, the hourly rate SHALL be daily_rate / 24,
        rounded to 2 decimal places.
        
        Validates: Requirements 5.3
        Feature: member-portal-billing, Property: Plan Hourly Rate Consistency
        """
        plan_config = plan_service.get_plan(plan_tier)
        
        # Get hourly rate
        hourly_rate = plan_config.get_hourly_rate()
        
        # Calculate expected hourly rate
        daily_rate = plan_config.get_daily_rate()
        expected_hourly_rate = (daily_rate / Decimal(24)).quantize(Decimal('0.01'))
        
        # Verify calculation matches
        assert hourly_rate == expected_hourly_rate
        
        # Verify hourly rate is positive
        assert hourly_rate > Decimal(0)
        
        # Verify hourly rate is less than daily rate
        assert hourly_rate < daily_rate
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_pricing_summary_completeness(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Pricing Summary Completeness
        
        For any plan change, the pricing summary SHALL include all required fields:
        - current_plan, new_plan, change_type
        - current_monthly_price, new_monthly_price, price_difference
        - days_remaining, proration_credit, amount_due
        - effective_date, next_billing_date
        
        Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
        Feature: member-portal-billing, Property: Pricing Summary Completeness
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing
            pricing = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Get summary
        summary = pricing.get_summary()
        
        # Verify all required fields are present
        required_fields = [
            "current_plan",
            "new_plan",
            "change_type",
            "current_monthly_price",
            "new_monthly_price",
            "price_difference",
            "days_remaining",
            "proration_credit",
            "amount_due",
            "effective_date",
            "next_billing_date",
        ]
        
        for field in required_fields:
            assert field in summary
            assert summary[field] is not None
        
        # Verify field types
        assert isinstance(summary["current_plan"], str)
        assert isinstance(summary["new_plan"], str)
        assert isinstance(summary["change_type"], str)
        assert isinstance(summary["current_monthly_price"], float)
        assert isinstance(summary["new_monthly_price"], float)
        assert isinstance(summary["price_difference"], float)
        assert isinstance(summary["days_remaining"], int)
        assert isinstance(summary["proration_credit"], float)
        assert isinstance(summary["amount_due"], float)
        assert isinstance(summary["effective_date"], str)
        assert isinstance(summary["next_billing_date"], str)
    
    @given(different_plan_tiers(), billing_dates())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_plan_change_idempotence(
        self, plan_service, plan_tiers_tuple, billing_dates_tuple
    ):
        """
        Property: Plan Change Calculation Idempotence
        
        For any plan change with the same inputs, calculating the pricing
        multiple times SHALL produce identical results.
        
        Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
        Feature: member-portal-billing, Property: Plan Change Idempotence
        """
        current_plan, new_plan = plan_tiers_tuple
        current_billing_date, next_billing_date = billing_dates_tuple
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate pricing twice
            pricing1 = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
            
            pricing2 = plan_service.calculate_plan_change(
                current_plan=current_plan,
                new_plan=new_plan,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify results are identical
        assert pricing1.current_plan == pricing2.current_plan
        assert pricing1.new_plan == pricing2.new_plan
        assert pricing1.change_type == pricing2.change_type
        assert pricing1.current_plan_price == pricing2.current_plan_price
        assert pricing1.new_plan_price == pricing2.new_plan_price
        assert pricing1.price_difference == pricing2.price_difference
        assert pricing1.days_remaining_in_cycle == pricing2.days_remaining_in_cycle
        assert pricing1.current_plan_daily_rate == pricing2.current_plan_daily_rate
        assert pricing1.new_plan_daily_rate == pricing2.new_plan_daily_rate
        assert pricing1.proration_credit == pricing2.proration_credit
        assert pricing1.amount_due == pricing2.amount_due
        assert pricing1.next_billing_date == pricing2.next_billing_date
    
    @given(different_plan_tiers())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_plan_comparison_symmetry(
        self, plan_service, plan_tiers_tuple
    ):
        """
        Property: Plan Comparison Symmetry
        
        For any two plans A and B, comparing A to B and B to A
        SHALL produce opposite change types (upgrade vs downgrade).
        
        Validates: Requirements 5.3, 5.4, 5.5
        Feature: member-portal-billing, Property: Plan Comparison Symmetry
        """
        plan_a, plan_b = plan_tiers_tuple
        
        # Create billing dates
        current_billing_date = datetime.utcnow() - timedelta(days=15)
        next_billing_date = current_billing_date + timedelta(days=30)
        
        # Use a fixed reference time to avoid timing issues
        reference_time = datetime.utcnow()
        
        with patch.object(plan_module, 'datetime') as mock_datetime:
            # Mock datetime.utcnow() to return fixed reference time
            mock_datetime.utcnow.return_value = reference_time
            # Keep other datetime functionality intact
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Calculate A to B
            pricing_a_to_b = plan_service.calculate_plan_change(
                current_plan=plan_a,
                new_plan=plan_b,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
            
            # Calculate B to A
            pricing_b_to_a = plan_service.calculate_plan_change(
                current_plan=plan_b,
                new_plan=plan_a,
                current_billing_date=current_billing_date,
                next_billing_date=next_billing_date,
            )
        
        # Verify change types are opposite
        if pricing_a_to_b.change_type == PlanChangeType.UPGRADE:
            assert pricing_b_to_a.change_type == PlanChangeType.DOWNGRADE
        else:
            assert pricing_b_to_a.change_type == PlanChangeType.UPGRADE
        
        # Verify proration credits are opposite
        assert pricing_a_to_b.proration_credit == -pricing_b_to_a.proration_credit
