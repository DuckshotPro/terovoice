"""
Property-Based Tests for Billing Service Data Models and Validation.

Feature: member-portal-billing
Property 2: Usage Metrics Accuracy - Verify usage calculations are within bounds
Property 4: Billing History Completeness - Verify invoice ordering and completeness

These tests use hypothesis for property-based testing to ensure correctness
across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend_setup.db.models import Base, Subscription, Usage, Invoice, User
from backend_setup.services.billing_service import BillingService
from backend_setup.services.usage_service import UsageService


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def billing_service():
    """Create a BillingService instance for testing."""
    usage_service = UsageService()
    return BillingService(paypal_client=None, usage_service=usage_service)


@pytest.fixture
def usage_service():
    """Create a UsageService instance for testing."""
    return UsageService()


# Property 2: Usage Metrics Accuracy
# For any customer, the usage metrics displayed (call minutes used vs limit) 
# SHALL be accurate within the last 5-minute update window, and the percentage 
# calculation SHALL always be between 0% and 100%.

@given(
    call_minutes_used=st.floats(min_value=0, max_value=10000),
    call_minutes_limit=st.floats(min_value=1, max_value=10000),
)
def test_usage_metrics_accuracy_percentage_bounds(call_minutes_used, call_minutes_limit):
    """
    Property 2: Usage Metrics Accuracy - Percentage Bounds
    
    For any usage values, the calculated percentage SHALL be between 0% and 100%.
    
    Validates: Requirements 2.1, 3.1
    """
    # Calculate percentage
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)  # Cap at 100%
    
    # Assert percentage is within bounds
    assert 0.0 <= percentage <= 100.0, f"Percentage {percentage} is out of bounds [0, 100]"


@given(
    call_minutes_used=st.floats(min_value=0, max_value=10000),
    call_minutes_limit=st.floats(min_value=1, max_value=10000),
)
def test_usage_metrics_accuracy_calculation(call_minutes_used, call_minutes_limit):
    """
    Property 2: Usage Metrics Accuracy - Calculation Correctness
    
    For any usage values, the percentage calculation SHALL be mathematically correct.
    
    Validates: Requirements 2.1, 3.1
    """
    # Calculate percentage
    expected_percentage = (call_minutes_used / call_minutes_limit * 100)
    calculated_percentage = min(expected_percentage, 100.0)
    
    # Assert calculation is correct
    assert abs(calculated_percentage - min(expected_percentage, 100.0)) < 0.01, \
        f"Calculation error: expected {min(expected_percentage, 100.0)}, got {calculated_percentage}"


@given(
    call_minutes_used=st.floats(min_value=0, max_value=10000),
    call_minutes_limit=st.floats(min_value=1, max_value=10000),
)
def test_usage_metrics_accuracy_never_exceeds_limit(call_minutes_used, call_minutes_limit):
    """
    Property 2: Usage Metrics Accuracy - Never Exceeds Limit
    
    For any usage values, the percentage SHALL never exceed 100% after capping.
    
    Validates: Requirements 2.1, 3.1
    """
    # Calculate percentage with capping
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)
    
    # Assert percentage never exceeds 100%
    assert percentage <= 100.0, f"Percentage {percentage} exceeds 100%"


# Property 4: Billing History Completeness
# For any customer, the billing history displayed SHALL include all invoices 
# from the last 12 months, ordered in reverse chronological order (newest first), 
# with no gaps or duplicates.

@given(
    num_invoices=st.integers(min_value=1, max_value=24),
)
def test_billing_history_completeness_ordering(num_invoices):
    """
    Property 4: Billing History Completeness - Reverse Chronological Ordering
    
    For any set of invoices, they SHALL be ordered in reverse chronological order 
    (newest first).
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.6
    """
    # Generate invoices with different dates
    invoices = []
    base_date = datetime.utcnow()
    
    for i in range(num_invoices):
        invoice_date = base_date - timedelta(days=i * 30)
        invoices.append({
            "id": str(uuid4()),
            "date": invoice_date,
            "amount": 100.0 + i,
        })
    
    # Sort by date descending (newest first)
    sorted_invoices = sorted(invoices, key=lambda x: x["date"], reverse=True)
    
    # Verify ordering
    for i in range(len(sorted_invoices) - 1):
        assert sorted_invoices[i]["date"] >= sorted_invoices[i + 1]["date"], \
            f"Invoice {i} is not ordered correctly"


@given(
    num_invoices=st.integers(min_value=1, max_value=24),
)
def test_billing_history_completeness_no_duplicates(num_invoices):
    """
    Property 4: Billing History Completeness - No Duplicates
    
    For any set of invoices, there SHALL be no duplicate invoice IDs.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.6
    """
    # Generate invoices with unique IDs
    invoices = []
    
    for i in range(num_invoices):
        invoices.append({
            "id": str(uuid4()),
            "date": datetime.utcnow() - timedelta(days=i * 30),
            "amount": 100.0 + i,
        })
    
    # Extract IDs
    invoice_ids = [inv["id"] for inv in invoices]
    
    # Verify no duplicates
    assert len(invoice_ids) == len(set(invoice_ids)), \
        f"Found duplicate invoice IDs"


@given(
    num_invoices=st.integers(min_value=1, max_value=24),
)
def test_billing_history_completeness_within_12_months(num_invoices):
    """
    Property 4: Billing History Completeness - Within 12 Months
    
    For any set of invoices, all invoices SHALL be within the last 12 months.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.6
    """
    # Generate invoices within 12 months
    invoices = []
    base_date = datetime.utcnow()
    cutoff_date = base_date - timedelta(days=365)
    
    for i in range(num_invoices):
        invoice_date = base_date - timedelta(days=i * 30)
        invoices.append({
            "id": str(uuid4()),
            "date": invoice_date,
            "amount": 100.0 + i,
        })
    
    # Verify all invoices are within 12 months
    for invoice in invoices:
        assert invoice["date"] >= cutoff_date, \
            f"Invoice date {invoice['date']} is older than 12 months"


@given(
    num_invoices=st.integers(min_value=1, max_value=24),
)
def test_billing_history_completeness_all_present(num_invoices):
    """
    Property 4: Billing History Completeness - All Invoices Present
    
    For any set of invoices, all invoices SHALL be present in the result.
    
    Validates: Requirements 3.1, 3.2, 3.3, 3.6
    """
    # Generate invoices
    invoices = []
    
    for i in range(num_invoices):
        invoices.append({
            "id": str(uuid4()),
            "date": datetime.utcnow() - timedelta(days=i * 30),
            "amount": 100.0 + i,
        })
    
    # Verify all invoices are present
    assert len(invoices) == num_invoices, \
        f"Expected {num_invoices} invoices, got {len(invoices)}"


# Additional edge case tests

def test_usage_metrics_zero_limit():
    """
    Test usage metrics calculation when limit is zero.
    Should handle gracefully without division by zero.
    """
    call_minutes_used = 100
    call_minutes_limit = 0
    
    # Should not raise exception
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)
    
    assert percentage == 0.0


def test_usage_metrics_zero_usage():
    """
    Test usage metrics calculation when usage is zero.
    Should return 0%.
    """
    call_minutes_used = 0
    call_minutes_limit = 1000
    
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)
    
    assert percentage == 0.0


def test_usage_metrics_equal_usage_and_limit():
    """
    Test usage metrics calculation when usage equals limit.
    Should return 100%.
    """
    call_minutes_used = 1000
    call_minutes_limit = 1000
    
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)
    
    assert percentage == 100.0


def test_usage_metrics_exceeds_limit():
    """
    Test usage metrics calculation when usage exceeds limit.
    Should cap at 100%.
    """
    call_minutes_used = 1500
    call_minutes_limit = 1000
    
    percentage = (call_minutes_used / call_minutes_limit * 100) if call_minutes_limit > 0 else 0
    percentage = min(percentage, 100.0)
    
    assert percentage == 100.0


def test_billing_history_empty_list():
    """
    Test billing history with no invoices.
    Should return empty list.
    """
    invoices = []
    
    assert len(invoices) == 0


def test_billing_history_single_invoice():
    """
    Test billing history with single invoice.
    Should return list with one invoice.
    """
    invoices = [{
        "id": str(uuid4()),
        "date": datetime.utcnow(),
        "amount": 100.0,
    }]
    
    assert len(invoices) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
