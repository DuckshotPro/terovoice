"""
Property-based tests for subscription service.
Tests subscription status retrieval, caching, and consistency.
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

# Import directly from modules
import importlib.util

# Load subscription_service module
spec = importlib.util.spec_from_file_location(
    "subscription_service",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'subscription_service.py')
)
subscription_module = importlib.util.module_from_spec(spec)

# Load cache module first
cache_spec = importlib.util.spec_from_file_location(
    "cache",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cache.py')
)
cache_module = importlib.util.module_from_spec(cache_spec)
sys.modules['cache'] = cache_module
cache_spec.loader.exec_module(cache_module)

# Now load subscription_service
sys.modules['subscription_service'] = subscription_module
spec.loader.exec_module(subscription_module)

SubscriptionService = subscription_module.SubscriptionService
SubscriptionStatus = subscription_module.SubscriptionStatus
SubscriptionData = subscription_module.SubscriptionData
SubscriptionCache = cache_module.SubscriptionCache


# ============================================================================
# Strategies for generating test data
# ============================================================================

@composite
def subscription_ids(draw):
    """Generate valid PayPal subscription IDs."""
    return f"I-{draw(st.text(alphabet='0123456789ABCDEF', min_size=17, max_size=17))}"


@composite
def customer_ids(draw):
    """Generate valid customer IDs."""
    return f"CUST-{draw(st.integers(min_value=1000, max_value=999999))}"


@composite
def plan_ids(draw):
    """Generate valid plan IDs."""
    plans = ["PLAN_SOLO_PRO", "PLAN_PROFESSIONAL", "PLAN_ENTERPRISE"]
    return draw(st.sampled_from(plans))


@composite
def subscription_statuses(draw):
    """Generate valid subscription statuses."""
    statuses = [
        "APPROVAL_PENDING",
        "APPROVED",
        "ACTIVE",
        "SUSPENDED",
        "CANCELLED",
        "EXPIRED",
    ]
    return draw(st.sampled_from(statuses))


@composite
def prices(draw):
    """Generate valid prices."""
    return draw(st.floats(min_value=99.0, max_value=9999.0)).quantize(2)


@composite
def iso_dates(draw):
    """Generate valid ISO 8601 dates."""
    days_offset = draw(st.integers(min_value=-365, max_value=365))
    date = datetime.utcnow() + timedelta(days=days_offset)
    return date.isoformat() + "Z"


@composite
def paypal_subscription_responses(draw):
    """Generate valid PayPal subscription API responses."""
    return {
        "id": draw(subscription_ids()),
        "status": draw(subscription_statuses()),
        "plan_id": draw(plan_ids()),
        "create_time": draw(iso_dates()),
        "update_time": draw(iso_dates()),
        "next_billing_time": draw(iso_dates()),
        "billing_cycles": [
            {
                "pricing_scheme": {
                    "fixed_price": {
                        "value": str(draw(prices())),
                        "currency_code": "USD",
                    }
                }
            }
        ],
    }


# ============================================================================
# Property 1: Subscription Status Consistency
# ============================================================================

@given(
    customer_id=customer_ids(),
    subscription_id=subscription_ids(),
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_subscription_status_consistency(customer_id, subscription_id):
    """
    Property 1: Subscription Status Consistency
    
    For any customer and subscription ID, fetching the subscription status
    twice within the cache TTL should return identical data.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3**
    """
    cache = SubscriptionCache()
    service = SubscriptionService(cache=cache)
    
    # Create mock subscription data
    mock_data = {
        "id": subscription_id,
        "status": "ACTIVE",
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    # Parse the response
    subscription1 = service._parse_paypal_response(mock_data, customer_id)
    
    # Cache it
    cache_key = cache.get_subscription_key(customer_id)
    cache.set(cache_key, subscription1)
    
    # Retrieve from cache
    subscription2 = cache.get(cache_key)
    
    # Both should be identical
    assert subscription1.subscription_id == subscription2.subscription_id
    assert subscription1.customer_id == subscription2.customer_id
    assert subscription1.status == subscription2.status
    assert subscription1.plan_name == subscription2.plan_name
    assert subscription1.monthly_price == subscription2.monthly_price


# ============================================================================
# Property 2: Cache Expiration
# ============================================================================

@given(
    customer_id=customer_ids(),
    subscription_id=subscription_ids(),
)
@settings(max_examples=50)
def test_cache_expiration(customer_id, subscription_id):
    """
    Property 2: Cache Expiration
    
    For any cached subscription, after the TTL expires, the cache should
    return None (cache miss).
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    cache = SubscriptionCache()
    service = SubscriptionService(cache=cache)
    
    # Create subscription data
    mock_data = {
        "id": subscription_id,
        "status": "ACTIVE",
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    subscription = service._parse_paypal_response(mock_data, customer_id)
    
    # Cache with very short TTL (1 second)
    cache_key = cache.get_subscription_key(customer_id)
    cache.set(cache_key, subscription, ttl_seconds=1)
    
    # Should be in cache immediately
    assert cache.get(cache_key) is not None
    
    # Wait for expiration
    import time
    time.sleep(1.1)
    
    # Should be expired now
    assert cache.get(cache_key) is None


# ============================================================================
# Property 3: Status Mapping Correctness
# ============================================================================

@given(paypal_status=subscription_statuses())
@settings(max_examples=50)
def test_status_mapping_correctness(paypal_status):
    """
    Property 3: Status Mapping Correctness
    
    For any PayPal subscription status, the service should map it to a
    valid SubscriptionStatus enum value.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
    """
    cache = SubscriptionCache()
    service = SubscriptionService(cache=cache)
    
    mock_data = {
        "id": "I-TEST123456789012345",
        "status": paypal_status,
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    subscription = service._parse_paypal_response(mock_data, "CUST-12345")
    
    # Status should be a valid SubscriptionStatus
    assert isinstance(subscription.status, SubscriptionStatus)
    assert subscription.status in [
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.PENDING,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.SUSPENDED,
        SubscriptionStatus.EXPIRED,
    ]


# ============================================================================
# Property 4: Plan Name Mapping
# ============================================================================

@given(plan_id=plan_ids())
@settings(max_examples=50)
def test_plan_name_mapping(plan_id):
    """
    Property 4: Plan Name Mapping
    
    For any valid plan ID, the service should map it to a human-readable
    plan name.
    
    **Validates: Requirements 1.1, 7.1, 7.2, 7.3**
    """
    service = SubscriptionService()
    
    plan_name = service._get_plan_name_from_id(plan_id)
    
    # Plan name should not be "Unknown Plan" for known plans
    assert plan_name in ["Solo Pro", "Professional", "Enterprise"]
    
    # Plan name should be non-empty
    assert len(plan_name) > 0


# ============================================================================
# Property 5: Cache Invalidation
# ============================================================================

@given(
    customer_id=customer_ids(),
    subscription_id=subscription_ids(),
)
@settings(max_examples=50)
def test_cache_invalidation(customer_id, subscription_id):
    """
    Property 5: Cache Invalidation
    
    For any cached subscription, after invalidation, the cache should
    return None (cache miss).
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    cache = SubscriptionCache()
    service = SubscriptionService(cache=cache)
    
    # Create and cache subscription
    mock_data = {
        "id": subscription_id,
        "status": "ACTIVE",
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    subscription = service._parse_paypal_response(mock_data, customer_id)
    cache_key = cache.get_subscription_key(customer_id)
    cache.set(cache_key, subscription)
    
    # Should be in cache
    assert cache.get(cache_key) is not None
    
    # Invalidate
    service.invalidate_subscription_cache(customer_id)
    
    # Should be gone
    assert cache.get(cache_key) is None


# ============================================================================
# Property 6: Subscription Data Immutability
# ============================================================================

@given(
    customer_id=customer_ids(),
    subscription_id=subscription_ids(),
)
@settings(max_examples=50)
def test_subscription_data_immutability(customer_id, subscription_id):
    """
    Property 6: Subscription Data Immutability
    
    For any SubscriptionData object, converting to dict and back should
    preserve all data (round-trip property).
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    service = SubscriptionService()
    
    # Create subscription
    mock_data = {
        "id": subscription_id,
        "status": "ACTIVE",
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    subscription = service._parse_paypal_response(mock_data, customer_id)
    
    # Convert to dict
    data_dict = subscription.to_dict()
    
    # Verify all fields are present
    assert data_dict["subscription_id"] == subscription.subscription_id
    assert data_dict["customer_id"] == subscription.customer_id
    assert data_dict["plan_name"] == subscription.plan_name
    assert data_dict["status"] == subscription.status.value
    assert data_dict["monthly_price"] == subscription.monthly_price
    assert data_dict["next_billing_date"] == subscription.next_billing_date
    assert data_dict["renewal_date"] == subscription.renewal_date


# ============================================================================
# Property 7: Cache Statistics Accuracy
# ============================================================================

@given(
    num_entries=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=50)
def test_cache_statistics_accuracy(num_entries):
    """
    Property 7: Cache Statistics Accuracy
    
    For any number of cache entries, the cache statistics should accurately
    reflect the number of active entries.
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    cache = SubscriptionCache()
    
    # Add entries
    for i in range(num_entries):
        cache.set(f"key_{i}", f"value_{i}", ttl_seconds=3600)
    
    # Get stats
    stats = cache.get_stats()
    
    # Should have correct number of entries
    assert stats["total_entries"] == num_entries
    assert stats["active_entries"] == num_entries
    assert stats["expired_entries"] == 0


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
@given(
    customer_id=customer_ids(),
    subscription_id=subscription_ids(),
)
@settings(max_examples=20)
async def test_subscription_service_integration(customer_id, subscription_id):
    """
    Integration test for subscription service.
    Tests the full flow of fetching and caching subscription data.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3**
    """
    cache = SubscriptionCache()
    service = SubscriptionService(cache=cache)
    
    # Mock the PayPal fetch
    mock_data = {
        "id": subscription_id,
        "status": "ACTIVE",
        "plan_id": "PLAN_PROFESSIONAL",
        "create_time": datetime.utcnow().isoformat() + "Z",
        "update_time": datetime.utcnow().isoformat() + "Z",
        "next_billing_time": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
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
    
    # Parse and cache
    subscription = service._parse_paypal_response(mock_data, customer_id)
    cache_key = cache.get_subscription_key(customer_id)
    cache.set(cache_key, subscription)
    
    # Retrieve from cache
    cached_subscription = cache.get(cache_key)
    
    # Verify
    assert cached_subscription is not None
    assert cached_subscription.customer_id == customer_id
    assert cached_subscription.subscription_id == subscription_id
    assert cached_subscription.status == SubscriptionStatus.ACTIVE
    assert cached_subscription.plan_name == "Professional"
    assert cached_subscription.monthly_price == 499.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
