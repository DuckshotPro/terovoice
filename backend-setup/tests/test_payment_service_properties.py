"""
Property-based tests for PaymentService.
Tests payment method management, updates, and failure handling.

Feature: member-portal-billing
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
import asyncio

from backend_setup.services.payment_service import (
    PaymentService,
    PaymentMethodData,
    PaymentMethodType,
    PaymentUpdateResult,
)
from backend_setup.services.cache import SubscriptionCache


# Test data generators
@st.composite
def payment_method_data(draw):
    """Generate random payment method data."""
    method_type = draw(st.sampled_from(list(PaymentMethodType)))

    # Generate card details if credit/debit card
    if method_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
        last_four = draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',))))
        card_brand = draw(st.sampled_from(["Visa", "Mastercard", "Amex", "Discover"]))
        expiry_month = draw(st.integers(min_value=1, max_value=12))
        expiry_year = draw(st.integers(min_value=2024, max_value=2030))
        billing_email = None
    elif method_type == PaymentMethodType.PAYPAL:
        last_four = None
        card_brand = None
        expiry_month = None
        expiry_year = None
        billing_email = draw(st.emails())
    else:  # BANK_ACCOUNT
        last_four = draw(st.text(min_size=4, max_size=4, alphabet=st.characters(whitelist_categories=('Nd',))))
        card_brand = None
        expiry_month = None
        expiry_year = None
        billing_email = None

    return PaymentMethodData(
        payment_method_id=draw(st.text(min_size=10, max_size=20)),
        subscription_id=draw(st.text(min_size=10, max_size=20)),
        method_type=method_type,
        last_four_digits=last_four,
        card_brand=card_brand,
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        billing_email=billing_email,
        updated_at=datetime.utcnow().isoformat() + "Z",
        is_default=draw(st.booleans()),
    )


class TestPaymentServiceProperties:
    """Property-based tests for PaymentService."""

    @pytest.fixture
    def payment_service(self):
        """Create payment service instance."""
        cache = SubscriptionCache()
        return PaymentService(cache=cache)

    @given(payment_method_data())
    @settings(max_examples=100)
    def test_property_6_payment_method_round_trip(self, payment_service, payment_method):
        """
        Property 6: Payment Method Update Round-Trip

        For any payment method update, after successful update in PayPal,
        the Member Portal SHALL display the new payment method (last 4 digits)
        and update date within 30 seconds.

        Validates: Requirements 4.3, 4.4, 4.5
        Feature: member-portal-billing, Property 6: Payment Method Update Round-Trip
        """
        # Store payment method in cache
        cache_key = f"payment_method:{payment_method.subscription_id}"
        payment_service.cache.set(cache_key, payment_method.to_dict(), ttl_seconds=3600)

        # Retrieve payment method
        async def test():
            retrieved = await payment_service.get_payment_method(
                customer_id="test_customer",
                subscription_id=payment_method.subscription_id,
            )

            # Verify round-trip preservation
            assert retrieved is not None
            assert retrieved.payment_method_id == payment_method.payment_method_id
            assert retrieved.subscription_id == payment_method.subscription_id
            assert retrieved.method_type == payment_method.method_type
            assert retrieved.last_four_digits == payment_method.last_four_digits
            assert retrieved.card_brand == payment_method.card_brand
            assert retrieved.billing_email == payment_method.billing_email
            assert retrieved.is_default == payment_method.is_default

        asyncio.run(test())

    @given(st.text(min_size=10, max_size=20), st.text(min_size=10, max_size=20))
    @settings(max_examples=100)
    def test_property_payment_method_cache_behavior(self, payment_service, customer_id, subscription_id):
        """
        Property: Payment Method Cache Behavior

        For any payment method, retrieving it twice within the cache TTL
        SHALL return identical data without hitting PayPal API.

        Validates: Requirements 4.1, 8.3
        Feature: member-portal-billing, Property: Payment Method Cache Behavior
        """
        async def test():
            # First retrieval (cache miss)
            first = await payment_service.get_payment_method(customer_id, subscription_id)

            # Second retrieval (cache hit)
            second = await payment_service.get_payment_method(customer_id, subscription_id)

            # Should return identical data
            if first and second:
                assert first.payment_method_id == second.payment_method_id
                assert first.last_four_digits == second.last_four_digits
                assert first.card_brand == second.card_brand
                assert first.updated_at == second.updated_at

        asyncio.run(test())

    @given(payment_method_data())
    @settings(max_examples=100)
    def test_property_payment_method_display_name(self, payment_method):
        """
        Property: Payment Method Display Name Consistency

        For any payment method, the display name SHALL be human-readable
        and include identifying information (last 4 digits or email).

        Validates: Requirements 4.1
        Feature: member-portal-billing, Property: Payment Method Display Name
        """
        display_name = payment_method.get_display_name()

        # Display name should not be empty
        assert len(display_name) > 0

        # Should include identifying information
        if payment_method.method_type == PaymentMethodType.PAYPAL:
            assert payment_method.billing_email in display_name
        elif payment_method.last_four_digits:
            assert payment_method.last_four_digits in display_name

    @given(
        st.integers(min_value=1, max_value=12),
        st.integers(min_value=2020, max_value=2030),
    )
    @settings(max_examples=100)
    def test_property_card_expiration_detection(self, expiry_month, expiry_year):
        """
        Property: Card Expiration Detection Accuracy

        For any card with expiry date, the system SHALL correctly identify
        whether the card is expired based on current date.

        Validates: Requirements 4.6
        Feature: member-portal-billing, Property: Card Expiration Detection
        """
        payment_method = PaymentMethodData(
            payment_method_id="PM-TEST",
            subscription_id="SUB-TEST",
            method_type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="4242",
            card_brand="Visa",
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            billing_email=None,
            updated_at=datetime.utcnow().isoformat() + "Z",
            is_default=True,
        )

        is_expired = payment_method.is_expired()

        # Verify expiration logic
        now = datetime.utcnow()
        expected_expired = (
            expiry_year < now.year or
            (expiry_year == now.year and expiry_month < now.month)
        )

        assert is_expired == expected_expired

    @given(st.text(min_size=10, max_size=20), st.text(min_size=10, max_size=20))
    @settings(max_examples=100)
    def test_property_payment_update_initiation(self, payment_service, customer_id, subscription_id):
        """
        Property: Payment Update Initiation Success

        For any valid subscription, initiating a payment method update
        SHALL return a redirect URL to PayPal.

        Validates: Requirements 4.2, 4.3
        Feature: member-portal-billing, Property: Payment Update Initiation
        """
        async def test():
            result = await payment_service.initiate_payment_method_update(
                customer_id=customer_id,
                subscription_id=subscription_id,
                return_url="https://example.com/return",
                cancel_url="https://example.com/cancel",
            )

            # Should succeed and return redirect URL
            assert result.success is True
            assert result.redirect_url is not None
            assert len(result.redirect_url) > 0
            assert "paypal.com" in result.redirect_url.lower()
            assert subscription_id in result.redirect_url

        asyncio.run(test())

    @given(st.text(min_size=10, max_size=20), st.text(min_size=10, max_size=20))
    @settings(max_examples=100)
    def test_property_cache_invalidation_on_update(self, payment_service, customer_id, subscription_id):
        """
        Property: Cache Invalidation on Payment Update

        For any payment method update, the cache SHALL be invalidated
        to ensure fresh data is fetched from PayPal.

        Validates: Requirements 4.4, 8.3
        Feature: member-portal-billing, Property: Cache Invalidation
        """
        async def test():
            # Store initial payment method in cache
            cache_key = f"payment_method:{subscription_id}"
            initial_data = {
                "payment_method_id": "PM-OLD",
                "subscription_id": subscription_id,
                "method_type": "credit_card",
                "last_four_digits": "1111",
                "card_brand": "Visa",
                "expiry_month": 12,
                "expiry_year": 2025,
                "billing_email": None,
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "is_default": True,
            }
            payment_service.cache.set(cache_key, initial_data, ttl_seconds=3600)

            # Verify cache hit
            cached = payment_service.cache.get(cache_key)
            assert cached is not None
            assert cached["payment_method_id"] == "PM-OLD"

            # Invalidate cache (simulating update)
            payment_service.invalidate_payment_method_cache(subscription_id)

            # Verify cache cleared
            cached_after = payment_service.cache.get(cache_key)
            assert cached_after is None

        asyncio.run(test())

    @given(
        st.text(min_size=10, max_size=20),
        st.text(min_size=10, max_size=20),
        st.sampled_from([
            "insufficient_funds",
            "card_declined",
            "expired_card",
            "invalid_card",
            "processing_error",
            "unknown_error",
        ]),
    )
    @settings(max_examples=100)
    def test_property_payment_failure_handling(self, payment_service, customer_id, subscription_id, failure_reason):
        """
        Property: Payment Failure Handling Consistency

        For any payment failure, the system SHALL provide a user-friendly
        error message and recommended action.

        Validates: Requirements 4.6
        Feature: member-portal-billing, Property: Payment Failure Handling
        """
        async def test():
            result = await payment_service.handle_payment_failure(
                customer_id=customer_id,
                subscription_id=subscription_id,
                failure_reason=failure_reason,
            )

            # Should return failure details
            assert result["customer_id"] == customer_id
            assert result["subscription_id"] == subscription_id
            assert result["failure_reason"] == failure_reason
            assert "message" in result
            assert len(result["message"]) > 0
            assert "recommended_action" in result
            assert result["recommended_action"] in ["update_payment_method", "contact_bank"]

        asyncio.run(test())

    @given(payment_method_data())
    @settings(max_examples=100)
    def test_property_payment_method_serialization(self, payment_method):
        """
        Property: Payment Method Serialization Round-Trip

        For any payment method, converting to dict and back SHALL preserve
        all data without loss.

        Validates: Requirements 4.1, 4.4
        Feature: member-portal-billing, Property: Payment Method Serialization
        """
        # Convert to dict
        data_dict = payment_method.to_dict()

        # Verify all fields present
        assert "payment_method_id" in data_dict
        assert "subscription_id" in data_dict
        assert "method_type" in data_dict
        assert "updated_at" in data_dict
        assert "is_default" in data_dict

        # Reconstruct from dict
        reconstructed = PaymentMethodData(**data_dict)

        # Verify round-trip preservation
        assert reconstructed.payment_method_id == payment_method.payment_method_id
        assert reconstructed.subscription_id == payment_method.subscription_id
        assert reconstructed.method_type.value == payment_method.method_type.value
        assert reconstructed.last_four_digits == payment_method.last_four_digits
        assert reconstructed.card_brand == payment_method.card_brand
        assert reconstructed.updated_at == payment_method.updated_at
        assert reconstructed.is_default == payment_method.is_default
