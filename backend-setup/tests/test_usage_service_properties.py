"""
Property-based tests for usage service.
Tests usage tracking, metrics calculation, and threshold checking.
"""
import sys
import os

# Add backend-setup to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite

# Import modules
import importlib.util

# Load usage_service module
spec = importlib.util.spec_from_file_location(
    "usage_service",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'usage_service.py')
)
usage_module = importlib.util.module_from_spec(spec)

# Load cache module first
cache_spec = importlib.util.spec_from_file_location(
    "cache",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cache.py')
)
cache_module = importlib.util.module_from_spec(cache_spec)
sys.modules['cache'] = cache_module
cache_spec.loader.exec_module(cache_module)

# Now load usage_service
sys.modules['usage_service'] = usage_module
spec.loader.exec_module(usage_module)

UsageService = usage_module.UsageService
UsageMetrics = usage_module.UsageMetrics
PlanTier = usage_module.PlanTier
UsageThreshold = usage_module.UsageThreshold
PlanLimits = usage_module.PlanLimits
SubscriptionCache = cache_module.SubscriptionCache


# ============================================================================
# Strategies for generating test data
# ============================================================================

@composite
def customer_ids(draw):
    """Generate valid customer IDs."""
    return f"CUST-{draw(st.integers(min_value=1000, max_value=999999))}"


@composite
def plan_tiers(draw):
    """Generate valid plan tiers."""
    return draw(st.sampled_from([PlanTier.SOLO_PRO, PlanTier.PROFESSIONAL, PlanTier.ENTERPRISE]))


@composite
def call_durations(draw):
    """Generate valid call durations in minutes."""
    return draw(st.floats(min_value=0.1, max_value=120.0))


@composite
def usage_percentages(draw):
    """Generate usage percentages."""
    return draw(st.floats(min_value=0.0, max_value=150.0))


# ============================================================================
# Property 2: Usage Metrics Accuracy
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
    call_duration=call_durations(),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_usage_metrics_accuracy(customer_id, plan_tier, call_duration):
    """
    Property 2: Usage Metrics Accuracy

    For any customer, the usage metrics displayed (call minutes used vs limit)
    SHALL be accurate, and the percentage calculation SHALL always be between
    0% and 150% (allowing for overage).

    **Validates: Requirements 2.1, 2.2, 2.3, 2.6, 2.7**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Record usage
    await service.record_usage(customer_id, call_duration)

    # Get metrics
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)

    # Verify accuracy
    assert metrics.call_minutes_used >= 0
    assert metrics.call_minutes_limit > 0
    assert 0 <= metrics.percentage_used <= 150

    # Verify calculation
    expected_percentage = (metrics.call_minutes_used / metrics.call_minutes_limit) * 100
    assert abs(metrics.percentage_used - expected_percentage) < 0.01


# ============================================================================
# Property 3: Usage Threshold Alerts
# ============================================================================

@given(
    customer_id=customer_ids(),
    percentage=usage_percentages(),
)
@settings(max_examples=100)
def test_usage_threshold_alerts(customer_id, percentage):
    """
    Property 3: Usage Threshold Alerts

    For any usage percentage:
    - < 80%: NORMAL threshold
    - 80-99%: WARNING threshold
    - >= 100%: ALERT threshold

    **Validates: Requirements 2.4, 2.5**
    """
    service = UsageService()

    threshold = service._determine_threshold(percentage)

    if percentage >= 100:
        assert threshold == UsageThreshold.ALERT
    elif percentage >= 80:
        assert threshold == UsageThreshold.WARNING
    else:
        assert threshold == UsageThreshold.NORMAL


# ============================================================================
# Property 4: Usage Accumulation
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
    call_durations=st.lists(call_durations(), min_size=1, max_size=10),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_usage_accumulation(customer_id, plan_tier, call_durations):
    """
    Property 4: Usage Accumulation

    For any sequence of usage recordings, the total usage SHALL equal
    the sum of all individual recordings.

    **Validates: Requirements 2.1, 2.7**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Record multiple usages
    for duration in call_durations:
        await service.record_usage(customer_id, duration)

    # Get metrics
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)

    # Verify accumulation
    expected_total = sum(call_durations)
    assert abs(metrics.call_minutes_used - expected_total) < 0.01


# ============================================================================
# Property 5: Cache TTL Behavior
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
    call_duration=call_durations(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_cache_ttl_behavior(customer_id, plan_tier, call_duration):
    """
    Property 5: Cache TTL Behavior

    For any usage recording, the cache SHALL expire after the TTL period
    (5 minutes for usage metrics).

    **Validates: Requirements 2.7**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Record usage
    await service.record_usage(customer_id, call_duration)

    # Verify cache entry exists
    usage_key = service._get_usage_key(customer_id)
    cached_data = cache.get(usage_key)
    assert cached_data is not None

    # Verify cache entry has correct TTL
    entry = cache._cache.get(usage_key)
    assert entry is not None
    assert entry.ttl_seconds == SubscriptionCache.DEFAULT_USAGE_TTL


# ============================================================================
# Property 6: Plan Limits Consistency
# ============================================================================

@given(
    plan_tier=plan_tiers(),
)
@settings(max_examples=10)
def test_plan_limits_consistency(plan_tier):
    """
    Property 6: Plan Limits Consistency

    For any plan tier, the limits SHALL be consistent and positive.

    **Validates: Requirements 2.2, 2.3**
    """
    limits = PlanLimits.get_limits(plan_tier)

    # Verify all limits are positive
    assert limits["call_minutes"] > 0
    assert limits["multi_location_support"] > 0

    # Verify limits increase with tier
    solo_limits = PlanLimits.get_limits(PlanTier.SOLO_PRO)
    pro_limits = PlanLimits.get_limits(PlanTier.PROFESSIONAL)
    enterprise_limits = PlanLimits.get_limits(PlanTier.ENTERPRISE)

    assert solo_limits["call_minutes"] < pro_limits["call_minutes"]
    assert pro_limits["call_minutes"] < enterprise_limits["call_minutes"]


# ============================================================================
# Property 7: Feature List Completeness
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_feature_list_completeness(customer_id, plan_tier):
    """
    Property 7: Feature List Completeness

    For any plan tier, the features list SHALL include all expected features
    with correct inclusion status.

    **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Get metrics
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)

    # Verify features list
    assert len(metrics.features) >= 4  # At least 4 core features

    feature_names = [f["name"] for f in metrics.features]
    assert "Call Minutes" in feature_names
    assert "Multi-Location Support" in feature_names
    assert "Priority Support" in feature_names
    assert "Dedicated Account Manager" in feature_names

    # Verify all features have required fields
    for feature in metrics.features:
        assert "name" in feature
        assert "included" in feature
        assert "description" in feature


# ============================================================================
# Property 8: Threshold Check Consistency
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
    percentage=usage_percentages(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_threshold_check_consistency(customer_id, plan_tier, percentage):
    """
    Property 8: Threshold Check Consistency

    For any usage percentage, the threshold check SHALL return consistent
    results with the metrics threshold.

    **Validates: Requirements 2.4, 2.5**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Calculate usage to achieve target percentage
    limits = PlanLimits.get_limits(plan_tier)
    target_usage = (percentage / 100) * limits["call_minutes"]

    # Record usage
    await service.record_usage(customer_id, target_usage)

    # Get metrics and threshold check
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)
    threshold_result = await service.check_usage_thresholds(customer_id, plan_tier.value)

    # Verify consistency
    assert threshold_result["threshold"] == metrics.threshold.value
    assert abs(threshold_result["percentage_used"] - metrics.percentage_used) < 0.01

    # Verify warning/alert flags
    if metrics.threshold == UsageThreshold.ALERT:
        assert threshold_result["should_alert"] is True
        assert threshold_result["upgrade_suggested"] is True
    elif metrics.threshold == UsageThreshold.WARNING:
        assert threshold_result["should_warn"] is True
    else:
        assert threshold_result["should_warn"] is False
        assert threshold_result["should_alert"] is False


# ============================================================================
# Property 9: Cache Invalidation
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
    call_duration=call_durations(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_cache_invalidation(customer_id, plan_tier, call_duration):
    """
    Property 9: Cache Invalidation

    For any usage recording, invalidating the cache SHALL remove the entry
    and subsequent reads SHALL return fresh data.

    **Validates: Requirements 8.2, 8.4**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Record usage
    await service.record_usage(customer_id, call_duration)

    # Verify cache entry exists
    usage_key = service._get_usage_key(customer_id)
    assert cache.get(usage_key) is not None

    # Invalidate cache
    service.invalidate_usage_cache(customer_id)

    # Verify cache entry is gone
    assert cache.get(usage_key) is None

    # Get metrics should return zero usage
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)
    assert metrics.call_minutes_used == 0


# ============================================================================
# Property 10: Billing Period Consistency
# ============================================================================

@given(
    customer_id=customer_ids(),
    plan_tier=plan_tiers(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_billing_period_consistency(customer_id, plan_tier):
    """
    Property 10: Billing Period Consistency

    For any usage metrics, the billing period SHALL be the current month
    (first day to first day of next month).

    **Validates: Requirements 2.1**
    """
    cache = SubscriptionCache()
    service = UsageService(cache=cache)

    # Get metrics
    metrics = await service.get_usage_metrics(customer_id, plan_tier.value)

    # Parse dates
    start = datetime.fromisoformat(metrics.billing_period_start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(metrics.billing_period_end.replace("Z", "+00:00"))

    # Verify billing period
    assert start.day == 1
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0

    # Verify end is first day of next month
    assert end.day == 1
    assert end > start

    # Verify period is approximately one month
    days_diff = (end - start).days
    assert 28 <= days_diff <= 31


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
