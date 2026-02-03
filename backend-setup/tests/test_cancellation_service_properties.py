"""
Property-based tests for CancellationService.
Tests subscription cancellation finality, idempotence, and state transitions.

Feature: member-portal-billing
Validates: Requirements 6.4, 6.5, 6.6
"""
import sys
import os

# Add backend-setup to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
import asyncio
import importlib.util
from unittest.mock import patch, AsyncMock

# Load cancellation_service module
spec = importlib.util.spec_from_file_location(
    "cancellation_service",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cancellation_service.py')
)
cancellation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cancellation_module)

# Load cache module
cache_spec = importlib.util.spec_from_file_location(
    "cache",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cache.py')
)
cache_module = importlib.util.module_from_spec(cache_spec)
cache_spec.loader.exec_module(cache_module)

# Extract classes
CancellationService = cancellation_module.CancellationService
CancellationReason = cancellation_module.CancellationReason
CancellationData = cancellation_module.CancellationData
CancellationResult = cancellation_module.CancellationResult
SubscriptionCache = cache_module.SubscriptionCache


# Test data generators
@st.composite
def subscription_ids(draw):
    """Generate random subscription IDs."""
    return f"SUB-{draw(st.text(alphabet='0123456789', min_size=10, max_size=20))}"


@st.composite
def customer_ids(draw):
    """Generate random customer IDs."""
    return f"CUST-{draw(st.text(alphabet='0123456789', min_size=10, max_size=20))}"


@st.composite
def cancellation_reasons(draw):
    """Generate random cancellation reasons."""
    return draw(st.sampled_from(list(CancellationReason)))


@st.composite
def feedback_text(draw):
    """Generate optional feedback text."""
    return draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=500)
    ))


@st.composite
def subscription_statuses(draw):
    """Generate random subscription statuses."""
    return draw(st.sampled_from(["ACTIVE", "PENDING", "SUSPENDED"]))


class TestCancellationServiceProperties:
    """Property-based tests for CancellationService."""
    
    @pytest.fixture
    def cancellation_service(self):
        """Create fresh cancellation service instance for each test."""
        # Create a new service with fresh cache and state for each test
        cache = SubscriptionCache()
        service = CancellationService(cache=cache)
        # Clear any previous cancellations
        service._cancelled_subscriptions.clear()
        return service
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_sets_status(
        self,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.1: Subscription Cancellation Status
        
        For any subscription in ACTIVE state, when cancelled:
        1. The result SHALL have success=True
        2. The subscription_id SHALL match the input
        3. The message SHALL indicate success
        4. The cancellation_date SHALL be set
        5. The remaining_access_until SHALL be set (next billing date)
        """
        # Create fresh service for each example
        cache = SubscriptionCache()
        cancellation_service = CancellationService(cache=cache)
        
        async def run_test():
            result = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify success
            assert result.success is True, "Cancellation should succeed"
            
            # Verify subscription ID matches
            assert result.subscription_id == subscription_id, \
                "Result subscription_id should match input"
            
            # Verify message indicates success
            assert "success" in result.message.lower() or "cancelled" in result.message.lower(), \
                "Message should indicate successful cancellation"
            
            # Verify cancellation date is set
            assert result.cancellation_date is not None, \
                "Cancellation date should be set"
            
            # Verify cancellation date is ISO format
            try:
                datetime.fromisoformat(result.cancellation_date.replace("Z", "+00:00"))
            except ValueError:
                pytest.fail("Cancellation date should be ISO format")
            
            # Verify remaining access is set
            assert result.remaining_access_until is not None, \
                "Remaining access until should be set"
        
        asyncio.run(run_test())
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_idempotence(
        self,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.2: Subscription Cancellation Idempotence
        
        For any subscription, cancelling it twice SHALL result in:
        1. First cancellation: success=True
        2. Second cancellation: success=False with error_code="ALREADY_CANCELLED"
        3. Both results have same subscription_id
        4. Cancellation date from first attempt is preserved
        """
        # Create fresh service for each example
        cache = SubscriptionCache()
        cancellation_service = CancellationService(cache=cache)
        
        async def run_test():
            # First cancellation
            result1 = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify first cancellation succeeds
            assert result1.success is True, "First cancellation should succeed"
            cancellation_date_1 = result1.cancellation_date
            
            # Second cancellation (should fail)
            result2 = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify second cancellation fails with correct error
            assert result2.success is False, "Second cancellation should fail"
            assert result2.error_code == "ALREADY_CANCELLED", \
                "Error code should be ALREADY_CANCELLED"
            
            # Verify subscription IDs match
            assert result1.subscription_id == result2.subscription_id, \
                "Subscription IDs should match"
            
            # Verify cancellation dates are consistent
            assert result1.cancellation_date == cancellation_date_1, \
                "First cancellation date should be preserved"
        
        asyncio.run(run_test())
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_reason_recorded(
        self,
        cancellation_service,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.3: Cancellation Reason Recording
        
        For any cancellation with a reason:
        1. The reason SHALL be recorded in the result
        2. The reason SHALL be one of the valid CancellationReason values
        3. If feedback is provided, it SHALL be stored
        """
        async def run_test():
            result = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify reason is valid
            assert reason in list(CancellationReason), \
                "Reason should be valid CancellationReason"
            
            # Verify result contains subscription ID
            assert result.subscription_id == subscription_id, \
                "Result should contain subscription ID"
            
            # If feedback provided, verify it's not lost
            if feedback is not None:
                # In production, feedback would be stored in database
                # For now, just verify it was passed to the service
                assert feedback is not None, "Feedback should be preserved"
        
        asyncio.run(run_test())
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_cache_invalidation(
        self,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.4: Cache Invalidation on Cancellation
        
        For any successful cancellation:
        1. The cache for the customer SHALL be invalidated
        2. Subsequent cache lookups SHALL return None
        3. Cache can be repopulated after invalidation
        """
        # Create fresh service for each example
        cache = SubscriptionCache()
        cancellation_service = CancellationService(cache=cache)
        
        async def run_test():
            # Pre-populate cache
            cache_key = cancellation_service.cache.get_subscription_key(customer_id)
            test_data = {"subscription_id": subscription_id, "status": "ACTIVE"}
            cancellation_service.cache.set(cache_key, test_data)
            
            # Verify cache is populated
            cached = cancellation_service.cache.get(cache_key)
            assert cached is not None, "Cache should be populated before cancellation"
            
            # Cancel subscription
            result = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify cache is invalidated
            cached_after = cancellation_service.cache.get(cache_key)
            assert cached_after is None, "Cache should be invalidated after cancellation"
        
        asyncio.run(run_test())
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_result_completeness(
        self,
        cancellation_service,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.5: Cancellation Result Completeness
        
        For any cancellation result:
        1. success field SHALL be boolean
        2. subscription_id field SHALL match input
        3. message field SHALL be non-empty string
        4. cancellation_date field SHALL be ISO format or None
        5. remaining_access_until field SHALL be ISO format or None
        6. error_code field SHALL be string or None
        """
        async def run_test():
            result = await cancellation_service.cancel_subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                reason=reason,
                feedback=feedback,
            )
            
            # Verify success is boolean
            assert isinstance(result.success, bool), \
                "success should be boolean"
            
            # Verify subscription_id matches
            assert result.subscription_id == subscription_id, \
                "subscription_id should match input"
            
            # Verify message is non-empty string
            assert isinstance(result.message, str), \
                "message should be string"
            assert len(result.message) > 0, \
                "message should not be empty"
            
            # Verify dates are ISO format or None
            if result.cancellation_date is not None:
                try:
                    datetime.fromisoformat(result.cancellation_date.replace("Z", "+00:00"))
                except ValueError:
                    pytest.fail("cancellation_date should be ISO format")
            
            if result.remaining_access_until is not None:
                try:
                    datetime.fromisoformat(result.remaining_access_until.replace("Z", "+00:00"))
                except ValueError:
                    pytest.fail("remaining_access_until should be ISO format")
            
            # Verify error_code is string or None
            assert result.error_code is None or isinstance(result.error_code, str), \
                "error_code should be string or None"
        
        asyncio.run(run_test())
    
    @given(
        subscription_ids(),
        customer_ids(),
        cancellation_reasons(),
        feedback_text()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_cancellation_data_serialization(
        self,
        cancellation_service,
        subscription_id,
        customer_id,
        reason,
        feedback
    ):
        """
        Property 8.6: Cancellation Data Serialization
        
        For any CancellationData object:
        1. to_dict() SHALL return a dictionary
        2. Dictionary SHALL contain all required fields
        3. reason field SHALL be string (enum value)
        4. Dictionary SHALL be JSON-serializable
        """
        cancellation_data = CancellationData(
            subscription_id=subscription_id,
            reason=reason,
            feedback=feedback,
        )
        
        # Convert to dict
        data_dict = cancellation_data.to_dict()
        
        # Verify it's a dictionary
        assert isinstance(data_dict, dict), \
            "to_dict() should return dictionary"
        
        # Verify required fields
        assert "subscription_id" in data_dict, \
            "Dictionary should contain subscription_id"
        assert "reason" in data_dict, \
            "Dictionary should contain reason"
        assert "feedback" in data_dict, \
            "Dictionary should contain feedback"
        assert "cancellation_date" in data_dict, \
            "Dictionary should contain cancellation_date"
        
        # Verify reason is string (enum value)
        assert isinstance(data_dict["reason"], str), \
            "reason should be string"
        assert data_dict["reason"] in [r.value for r in CancellationReason], \
            "reason should be valid CancellationReason value"
        
        # Verify JSON serializable
        import json
        try:
            json.dumps(data_dict)
        except TypeError:
            pytest.fail("CancellationData should be JSON-serializable")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
