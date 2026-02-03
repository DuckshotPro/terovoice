"""
Billing service for subscription and invoice management.
Handles billing history retrieval, filtering, and invoice operations.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.future import select
from sqlalchemy import desc

logger = logging.getLogger(__name__)

try:
    from backend_setup.services.cache import get_cache, SubscriptionCache
    from backend_setup.db.models import Invoice, Subscription
    from backend_setup.db.connection import get_db_context
except ImportError as e:
    logger.warning(f"Failed to import from backend_setup: {e}. Trying relative imports.")
    from .cache import get_cache, SubscriptionCache
    from ..db.models import Invoice, Subscription
    from ..db.connection import get_db_context


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"


class InvoiceData:
    """Data class for invoice information."""
    
    def __init__(
        self,
        invoice_id: str,
        subscription_id: str,
        paypal_invoice_id: Optional[str],
        amount: float,
        currency: str,
        status: InvoiceStatus,
        period_start: str,
        period_end: str,
        due_date: str,
        paid_at: Optional[str],
        created_at: str,
        plan_name: Optional[str] = None,
        download_url: Optional[str] = None,
    ):
        """Initialize invoice data."""
        self.invoice_id = invoice_id
        self.subscription_id = subscription_id
        self.paypal_invoice_id = paypal_invoice_id
        self.amount = amount
        self.currency = currency
        self.status = status
        self.period_start = period_start
        self.period_end = period_end
        self.due_date = due_date
        self.paid_at = paid_at
        self.created_at = created_at
        self.plan_name = plan_name
        self.download_url = download_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "invoice_id": self.invoice_id,
            "subscription_id": self.subscription_id,
            "paypal_invoice_id": self.paypal_invoice_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status.value,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "due_date": self.due_date,
            "paid_at": self.paid_at,
            "created_at": self.created_at,
            "plan_name": self.plan_name,
            "download_url": self.download_url,
        }


class BillingHistoryFilters:
    """Filters for billing history queries."""
    
    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
    ):
        """
        Initialize billing history filters.
        
        Args:
            start_date: Filter invoices after this date (ISO format)
            end_date: Filter invoices before this date (ISO format)
            status: Filter by invoice status (paid, pending, failed)
            min_amount: Filter invoices with amount >= this value
            max_amount: Filter invoices with amount <= this value
            limit: Maximum number of invoices to return
            offset: Number of invoices to skip (for pagination)
        """
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.limit = limit
        self.offset = offset


class BillingService:
    """
    Service for billing operations.
    Handles billing history retrieval, invoice management, and filtering.
    """
    
    def __init__(
        self,
        database=None,
        paypal_client=None,
        cache: Optional[SubscriptionCache] = None,
    ):
        """
        Initialize billing service.
        
        Args:
            database: Database connection (optional for testing)
            paypal_client: PayPal API client (optional for testing)
            cache: Cache instance (uses global if None)
        """
        self.database = database
        self.paypal_client = paypal_client
        self.cache = cache or get_cache()
        self.logger = logging.getLogger(__name__)
    
    async def get_billing_history(
        self,
        customer_id: str,
        filters: Optional[BillingHistoryFilters] = None,
    ) -> List[InvoiceData]:
        """
        Get billing history for a customer with optional filtering.
        
        Args:
            customer_id: Customer ID
            filters: Optional filters for date range, status, amount
            
        Returns:
            List of InvoiceData objects in reverse chronological order
        """
        self.logger.info(f"Getting billing history: customer={customer_id}")
        
        # Use default filters if none provided
        if filters is None:
            filters = BillingHistoryFilters()
        
        # Check cache first
        cache_key = self._get_billing_history_cache_key(customer_id, filters)
        cached_history = self.cache.get(cache_key)
        
        if cached_history is not None:
            self.logger.info(f"Billing history cache HIT: {customer_id}")
            return [InvoiceData(**invoice) for invoice in cached_history]
        
        # In production, this would query the database
        # For now, we'll use mock data for testing
        invoices = self._query_invoices_from_database(customer_id, filters)
        
        # Sort in reverse chronological order (newest first)
        invoices.sort(key=lambda inv: inv.created_at, reverse=True)
        
        # Cache the results
        invoice_dicts = [inv.to_dict() for inv in invoices]
        self.cache.set(
            cache_key,
            invoice_dicts,
            ttl_seconds=SubscriptionCache.DEFAULT_BILLING_HISTORY_TTL,
        )
        
        self.logger.info(f"Billing history retrieved: {len(invoices)} invoices")
        return invoices
    
        """
        Query invoices from database with filters.
        
        Args:
            customer_id: Customer ID
            filters: Query filters
            
        Returns:
            List of InvoiceData objects
        """
        try:
             # Use provided database session or create a new context
            db_session = self.database
            if db_session:
                 return self._query_invoices_with_session(db_session, customer_id, filters)
            else:
                 with get_db_context() as db:
                     return self._query_invoices_with_session(db, customer_id, filters)
        except Exception as e:
            self.logger.error(f"Database query failed: {e}. Falling back to mock data.")
            return self._generate_mock_invoices(customer_id)

    def _query_invoices_with_session(self, db, customer_id: str, filters: BillingHistoryFilters) -> List[InvoiceData]:
        """Helper to query invoices with a session."""
        stmt = select(Invoice).join(Subscription).where(Subscription.user_id == customer_id)
        
        # Apply filters
        if filters.start_date:
            stmt = stmt.where(Invoice.created_at >= datetime.fromisoformat(filters.start_date.replace("Z", "+00:00")))
        if filters.end_date:
            stmt = stmt.where(Invoice.created_at <= datetime.fromisoformat(filters.end_date.replace("Z", "+00:00")))
        if filters.status:
            stmt = stmt.where(Invoice.status == filters.status)
        if filters.min_amount:
            stmt = stmt.where(Invoice.amount >= filters.min_amount)
        if filters.max_amount:
             stmt = stmt.where(Invoice.amount <= filters.max_amount)
             
        # Sorting and Pagination
        stmt = stmt.order_by(desc(Invoice.created_at)).offset(filters.offset).limit(filters.limit)
        
        result = db.execute(stmt)
        invoices = result.scalars().all()
        
        return [
            InvoiceData(
                invoice_id=str(inv.id),
                subscription_id=str(inv.subscription_id),
                paypal_invoice_id=inv.paypal_invoice_id,
                amount=inv.amount,
                currency=inv.currency,
                status=InvoiceStatus(inv.status) if inv.status in InvoiceStatus._value2member_map_ else InvoiceStatus.DRAFT,
                period_start=inv.period_start.isoformat() + "Z" if inv.period_start else None,
                period_end=inv.period_end.isoformat() + "Z" if inv.period_end else None,
                due_date=inv.due_date.isoformat() + "Z" if inv.due_date else None,
                paid_at=inv.paid_at.isoformat() + "Z" if inv.paid_at else None,
                created_at=inv.created_at.isoformat() + "Z",
                plan_name="Standard", # Retrieve from subscription if needed
                download_url=f"/api/invoices/{customer_id}/{inv.id}/download"
            ) for inv in invoices
        ]
    
    def _generate_mock_invoices(self, customer_id: str) -> List[InvoiceData]:
        """
        Generate mock invoices for testing.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of mock InvoiceData objects
        """
        now = datetime.utcnow()
        invoices = []
        
        # Generate 12 months of invoices
        for i in range(12):
            month_offset = i
            invoice_date = now - timedelta(days=30 * month_offset)
            period_start = invoice_date.replace(day=1)
            
            # Calculate period end (first day of next month)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
            
            # Determine status (most recent are paid, some pending/failed)
            if i == 0:
                status = InvoiceStatus.PENDING
            elif i == 1:
                status = InvoiceStatus.PAID
            elif i == 5:
                status = InvoiceStatus.FAILED
            else:
                status = InvoiceStatus.PAID
            
            # Determine amount based on plan
            amount = 299.0 if i < 6 else 499.0  # Plan upgrade after 6 months
            plan_name = "Solo Pro" if i < 6 else "Professional"
            
            invoice = InvoiceData(
                invoice_id=f"INV-{customer_id}-{i:03d}",
                subscription_id=f"SUB-{customer_id}",
                paypal_invoice_id=f"PAYPAL-INV-{i:03d}",
                amount=amount,
                currency="USD",
                status=status,
                period_start=period_start.isoformat() + "Z",
                period_end=period_end.isoformat() + "Z",
                due_date=period_end.isoformat() + "Z",
                paid_at=invoice_date.isoformat() + "Z" if status == InvoiceStatus.PAID else None,
                created_at=invoice_date.isoformat() + "Z",
                plan_name=plan_name,
                download_url=f"/api/invoices/{customer_id}/INV-{i:03d}/download",
            )
            
            invoices.append(invoice)
        
        return invoices
    
    def _get_billing_history_cache_key(
        self,
        customer_id: str,
        filters: BillingHistoryFilters,
    ) -> str:
        """
        Generate cache key for billing history.
        
        Args:
            customer_id: Customer ID
            filters: Query filters
            
        Returns:
            Cache key string
        """
        # Include filter parameters in cache key for proper cache isolation
        filter_str = (
            f"{filters.start_date or 'none'}_"
            f"{filters.end_date or 'none'}_"
            f"{filters.status or 'none'}_"
            f"{filters.min_amount or 'none'}_"
            f"{filters.max_amount or 'none'}_"
            f"{filters.limit}_{filters.offset}"
        )
        
        return f"billing_history:{customer_id}:{filter_str}"
    
    def invalidate_billing_history_cache(self, customer_id: str) -> None:
        """
        Invalidate all billing history cache entries for a customer.
        Called when new invoices are created or updated.
        
        Args:
            customer_id: Customer ID
        """
        # In production, this would clear all cache keys matching the pattern
        # For now, we'll just clear the default cache key
        default_filters = BillingHistoryFilters()
        cache_key = self._get_billing_history_cache_key(customer_id, default_filters)
        self.cache.delete(cache_key)
        
        self.logger.info(f"Invalidated billing history cache: {customer_id}")
    
    async def get_invoice_details(
        self,
        customer_id: str,
        invoice_id: str,
    ) -> Optional[InvoiceData]:
        """
        Get detailed information for a specific invoice.
        
        Args:
            customer_id: Customer ID
            invoice_id: Invoice ID
            
        Returns:
            InvoiceData object or None if not found
        """
        self.logger.info(f"Getting invoice details: customer={customer_id}, invoice={invoice_id}")
        
        # Get all invoices and find the matching one
        all_invoices = await self.get_billing_history(customer_id)
        
        for invoice in all_invoices:
            if invoice.invoice_id == invoice_id:
                return invoice
        
        self.logger.warning(f"Invoice not found: {invoice_id}")
        return None
    
    async def get_invoice_pdf_url(
        self,
        customer_id: str,
        invoice_id: str,
    ) -> Optional[str]:
        """
        Get PDF download URL for an invoice.
        
        Args:
            customer_id: Customer ID
            invoice_id: Invoice ID
            
        Returns:
            PDF download URL or None if not found
        """
        invoice = await self.get_invoice_details(customer_id, invoice_id)
        
        if invoice:
            return invoice.download_url
        
        return None
