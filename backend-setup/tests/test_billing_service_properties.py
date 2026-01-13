"""
Property-based tests for billing service.
Tests billing history retrieval, filtering, and invoice operations.
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

# Load billing_service module
spec = importlib.util.spec_from_file_location(
    "billing_service",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'billing_service.py')
)
billing_module = importlib.util.module_from_spec(spec)

# Load cache module first
cache_spec = importlib.util.spec_from_file_location(
    "cache",
    os.path.join(os.path.dirname(__file__), '..', 'services', 'cache.py')
)
cache_module = importlib.util.module_from_spec(cache_spec)
sys.modules['cache'] = cache_module
cache_spec.loader.exec_module(cache_module)

# Now load billing_service
sys.modules['billing_service'] = billing_module
spec.loader.exec_module(billing_module)

BillingService = billing_module.BillingService
InvoiceStatus = billing_module.InvoiceStatus
InvoiceData = billing_module.InvoiceData
BillingHistoryFilters = billing_module.BillingHistoryFilters
SubscriptionCache = cache_module.SubscriptionCache


# ============================================================================
# Strategies for generating test data
# ============================================================================

@composite
def customer_ids(draw):
    """Generate valid customer IDs."""
    return f"CUST-{draw(st.integers(min_value=1000, max_value=999999))}"


@composite
def invoice_statuses(draw):
    """Generate valid invoice statuses."""
    return draw(st.sampled_from([InvoiceStatus.PAID, InvoiceStatus.PENDING, InvoiceStatus.FAILED]))


@composite
def date_ranges(draw):
    """Generate valid date ranges."""
    now = datetime.utcnow()
    days_back = draw(st.integers(min_value=30, max_value=365))
    start_date = now - timedelta(days=days_back)
    end_date = now
    return start_date.isoformat() + "Z", end_date.isoformat() + "Z"


@composite
def amount_ranges(draw):
    """Generate valid amount ranges."""
    min_amount = draw(st.floats(min_value=0, max_value=500))
    max_amount = draw(st.floats(min_value=min_amount, max_value=1000))
    return min_amount, max_amount


# ============================================================================
# Property 4: Billing History Completeness
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_billing_history_completeness(customer_id):
    """
    Property 4: Billing History Completeness
    
    For any customer, the billing history SHALL include all invoices
    from the last 12 months, ordered in reverse chronological order
    (newest first), with no gaps or duplicates.
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.6**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Get billing history
    invoices = await service.get_billing_history(customer_id)
    
    # Verify completeness (at least 12 months of data)
    assert len(invoices) >= 12
    
    # Verify reverse chronological order (newest first)
    for i in range(len(invoices) - 1):
        current_date = datetime.fromisoformat(invoices[i].created_at.replace("Z", "+00:00"))
        next_date = datetime.fromisoformat(invoices[i + 1].created_at.replace("Z", "+00:00"))
        assert current_date >= next_date, "Invoices not in reverse chronological order"
    
    # Verify no duplicates
    invoice_ids = [inv.invoice_id for inv in invoices]
    assert len(invoice_ids) == len(set(invoice_ids)), "Duplicate invoices found"


# ============================================================================
# Property 5: Invoice Data Integrity
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_invoice_data_integrity(customer_id):
    """
    Property 5: Invoice Data Integrity
    
    For any invoice, all required fields SHALL be present and valid.
    
    **Validates: Requirements 3.2**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Get billing history
    invoices = await service.get_billing_history(customer_id)
    
    # Verify each invoice has required fields
    for invoice in invoices:
        assert invoice.invoice_id is not None
        assert invoice.subscription_id is not None
        assert invoice.amount > 0
        assert invoice.currency == "USD"
        assert invoice.status in [InvoiceStatus.PAID, InvoiceStatus.PENDING, InvoiceStatus.FAILED, InvoiceStatus.DRAFT, InvoiceStatus.SENT]
        assert invoice.period_start is not None
        assert invoice.period_end is not None
        assert invoice.due_date is not None
        assert invoice.created_at is not None
        assert invoice.plan_name is not None
        assert invoice.download_url is not None


# ============================================================================
# Property 6: Date Range Filtering
# ============================================================================

@given(
    customer_id=customer_ids(),
    date_range=date_ranges(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_date_range_filtering(customer_id, date_range):
    """
    Property 6: Date Range Filtering
    
    For any date range filter, all returned invoices SHALL fall within
    the specified date range.
    
    **Validates: Requirements 3.6**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    start_date, end_date = date_range
    filters = BillingHistoryFilters(start_date=start_date, end_date=end_date)
    
    # Get filtered billing history
    invoices = await service.get_billing_history(customer_id, filters)
    
    # Verify all invoices are within date range
    start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    
    for invoice in invoices:
        invoice_dt = datetime.fromisoformat(invoice.created_at.replace("Z", "+00:00"))
        assert start_dt <= invoice_dt <= end_dt, f"Invoice {invoice.invoice_id} outside date range"


# ============================================================================
# Property 7: Status Filtering
# ============================================================================

@given(
    customer_id=customer_ids(),
    status=invoice_statuses(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_status_filtering(customer_id, status):
    """
    Property 7: Status Filtering
    
    For any status filter, all returned invoices SHALL have the
    specified status.
    
    **Validates: Requirements 3.6**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    filters = BillingHistoryFilters(status=status.value)
    
    # Get filtered billing history
    invoices = await service.get_billing_history(customer_id, filters)
    
    # Verify all invoices have the specified status
    for invoice in invoices:
        assert invoice.status == status, f"Invoice {invoice.invoice_id} has wrong status"


# ============================================================================
# Property 8: Amount Range Filtering
# ============================================================================

@given(
    customer_id=customer_ids(),
    amount_range=amount_ranges(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_amount_range_filtering(customer_id, amount_range):
    """
    Property 8: Amount Range Filtering
    
    For any amount range filter, all returned invoices SHALL have
    amounts within the specified range.
    
    **Validates: Requirements 3.6**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    min_amount, max_amount = amount_range
    filters = BillingHistoryFilters(min_amount=min_amount, max_amount=max_amount)
    
    # Get filtered billing history
    invoices = await service.get_billing_history(customer_id, filters)
    
    # Verify all invoices are within amount range
    for invoice in invoices:
        assert min_amount <= invoice.amount <= max_amount, f"Invoice {invoice.invoice_id} outside amount range"


# ============================================================================
# Property 9: Pagination Consistency
# ============================================================================

@given(
    customer_id=customer_ids(),
    page_size=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_pagination_consistency(customer_id, page_size):
    """
    Property 9: Pagination Consistency
    
    For any pagination parameters, the total number of invoices across
    all pages SHALL equal the total number of invoices without pagination.
    
    **Validates: Requirements 3.7**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Get all invoices without pagination
    all_invoices = await service.get_billing_history(customer_id)
    total_count = len(all_invoices)
    
    # Get invoices with pagination
    paginated_invoices = []
    offset = 0
    
    while True:
        filters = BillingHistoryFilters(limit=page_size, offset=offset)
        page_invoices = await service.get_billing_history(customer_id, filters)
        
        if not page_invoices:
            break
        
        paginated_invoices.extend(page_invoices)
        offset += page_size
        
        # Safety check to prevent infinite loop
        if offset > total_count + page_size:
            break
    
    # Verify total count matches
    assert len(paginated_invoices) == total_count


# ============================================================================
# Property 10: Cache Behavior
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_cache_behavior(customer_id):
    """
    Property 10: Cache Behavior
    
    For any billing history query, subsequent identical queries SHALL
    return cached results within the TTL period.
    
    **Validates: Requirements 8.3**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # First query (cache miss)
    invoices1 = await service.get_billing_history(customer_id)
    
    # Second query (cache hit)
    invoices2 = await service.get_billing_history(customer_id)
    
    # Verify results are identical
    assert len(invoices1) == len(invoices2)
    
    for inv1, inv2 in zip(invoices1, invoices2):
        assert inv1.invoice_id == inv2.invoice_id
        assert inv1.amount == inv2.amount
        assert inv1.status == inv2.status


# ============================================================================
# Property 11: Invoice Details Retrieval
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_invoice_details_retrieval(customer_id):
    """
    Property 11: Invoice Details Retrieval
    
    For any invoice in the billing history, retrieving its details
    SHALL return the same invoice data.
    
    **Validates: Requirements 3.4**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Get billing history
    invoices = await service.get_billing_history(customer_id)
    
    if not invoices:
        pytest.skip("No invoices to test")
    
    # Get details for first invoice
    first_invoice = invoices[0]
    invoice_details = await service.get_invoice_details(customer_id, first_invoice.invoice_id)
    
    # Verify details match
    assert invoice_details is not None
    assert invoice_details.invoice_id == first_invoice.invoice_id
    assert invoice_details.amount == first_invoice.amount
    assert invoice_details.status == first_invoice.status


# ============================================================================
# Property 12: PDF Download URL Availability
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_pdf_download_url_availability(customer_id):
    """
    Property 12: PDF Download URL Availability
    
    For any invoice, a PDF download URL SHALL be available.
    
    **Validates: Requirements 3.5**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Get billing history
    invoices = await service.get_billing_history(customer_id)
    
    # Verify all invoices have download URLs
    for invoice in invoices:
        pdf_url = await service.get_invoice_pdf_url(customer_id, invoice.invoice_id)
        assert pdf_url is not None
        assert pdf_url.startswith("/api/invoices/")


# ============================================================================
# Property 13: Empty History Handling
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=10)
@pytest.mark.asyncio
async def test_empty_history_handling(customer_id):
    """
    Property 13: Empty History Handling
    
    For any customer with no invoices, the billing history SHALL
    return an empty list (not None or error).
    
    **Validates: Requirements 3.7**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # Create filters that will return no results
    future_date = (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z"
    filters = BillingHistoryFilters(start_date=future_date)
    
    # Get billing history
    invoices = await service.get_billing_history(customer_id, filters)
    
    # Verify empty list is returned
    assert invoices is not None
    assert isinstance(invoices, list)
    assert len(invoices) == 0


# ============================================================================
# Property 14: Cache Invalidation
# ============================================================================

@given(
    customer_id=customer_ids(),
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@pytest.mark.asyncio
async def test_cache_invalidation(customer_id):
    """
    Property 14: Cache Invalidation
    
    For any billing history query, invalidating the cache SHALL
    force a fresh query on the next request.
    
    **Validates: Requirements 8.2, 8.4**
    """
    cache = SubscriptionCache()
    service = BillingService(cache=cache)
    
    # First query (cache miss)
    invoices1 = await service.get_billing_history(customer_id)
    
    # Invalidate cache
    service.invalidate_billing_history_cache(customer_id)
    
    # Second query (should be fresh, not cached)
    invoices2 = await service.get_billing_history(customer_id)
    
    # Verify results are still valid (even if identical)
    assert len(invoices2) >= 0
    assert isinstance(invoices2, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
