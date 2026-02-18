"""
SQLAlchemy models for the AI Receptionist SaaS.
Defines all database tables and relationships.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    password_hash = Column(String)  # bcrypt hash
    oauth_provider = Column(String)  # google, github, etc
    oauth_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")


class Subscription(Base):
    """User subscription model."""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan = Column(String, default="free")  # free, starter, pro, enterprise
    status = Column(String, default="active")  # active, cancelled, expired
    paypal_subscription_id = Column(String, unique=True)
    paypal_plan_id = Column(String)
    monthly_price = Column(Float, default=0)
    max_clients = Column(Integer, default=1)
    max_minutes_per_month = Column(Integer, default=100)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    cancelled_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    usage_records = relationship("Usage", back_populates="subscription", cascade="all, delete-orphan")


class Client(Base):
    """Client (business) model."""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    profession = Column(String)  # dentist, plumber, locksmith, etc
    voice_id = Column(String)  # Cartesia or ElevenLabs voice ID
    voice_name = Column(String)  # af_sarah, etc
    system_prompt = Column(Text)  # Custom AI instructions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="clients")
    calls = relationship("Call", back_populates="client", cascade="all, delete-orphan")


class Call(Base):
    """Call log model."""
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    caller_phone = Column(String)
    caller_name = Column(String)
    duration_seconds = Column(Float)
    stt_latency_ms = Column(Float)  # Speech-to-text latency
    llm_latency_ms = Column(Float)  # LLM processing latency
    tts_latency_ms = Column(Float)  # Text-to-speech latency
    transcript = Column(Text)
    sentiment = Column(String)  # POSITIVE, NEGATIVE, NEUTRAL
    success = Column(Boolean, default=True)
    recording_url = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    client = relationship("Client", back_populates="calls")


class Usage(Base):
    """Usage metrics model for tracking subscription usage."""
    __tablename__ = "usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    call_minutes_used = Column(Float, default=0)
    call_minutes_limit = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")


class Invoice(Base):
    """Invoice model for billing."""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    paypal_invoice_id = Column(String, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="draft")  # draft, sent, paid, failed
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    due_date = Column(DateTime)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")


class APIKey(Base):
    """API key for programmatic access."""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, unique=True, nullable=False)  # bcrypt hash
    name = Column(String)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class VectorEmbedding(Base):
    """Vector embeddings for semantic search (pgvector)."""
    __tablename__ = "vector_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    embedding = Column(String)  # pgvector type (stored as string for compatibility)
    created_at = Column(DateTime, server_default=func.now())


class OnboardingState(Base):
    """Onboarding state tracking for new customers."""
    __tablename__ = "onboarding_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    current_step = Column(Integer, default=1)  # 1-7
    progress = Column(Integer, default=0)  # 0-100
    completed_steps = Column(JSON, default=list)  # [1, 2, 3]

    # Business Information (Step 1)
    business_name = Column(String)
    industry = Column(String)
    business_phone = Column(String)
    service_description = Column(Text)
    business_documents = Column(JSON, default=list)  # URLs to uploaded docs

    # Phone Configuration (Step 2)
    forwarding_number = Column(String)
    sms_enabled = Column(Boolean, default=False)
    sms_phone_number = Column(String)

    # Caller Responses (Step 3)
    caller_responses = Column(JSON, default=dict)  # Custom response templates

    # Calendar Integration (Step 4)
    calendar_provider = Column(String)  # google, outlook, apple
    calendar_connected = Column(Boolean, default=False)
    calendar_access_token = Column(String)
    calendar_refresh_token = Column(String)

    # Demo Status (Step 5)
    demo_completed = Column(Boolean, default=False)
    demo_transcripts = Column(JSON, default=list)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="onboarding_state")


class ConversationLog(Base):
    """Detailed conversation logging for fine-tuning and RAG."""
    __tablename__ = "conversation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    # Conversation data
    user_utterance = Column(Text)
    user_audio_url = Column(String)  # Raw audio bytes stored in S3/local
    ai_response = Column(Text)
    ai_audio_url = Column(String)  # Generated audio stored in S3/local

    # Technical metadata
    stt_provider = Column(String)  # on-site, ibm-cloud
    tts_provider = Column(String)  # on-site, ibm-cloud
    confidence = Column(Float)
    sentiment = Column(String)
    intent = Column(String)

    # Business metadata
    industry = Column(String)
    profession = Column(String)
    call_type = Column(String)  # demo, live, test

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    call = relationship("Call", backref="conversation_logs")
    user = relationship("User", backref="conversation_logs")


class AnalyticsEvent(Base):
    """Analytics event tracking for product optimization."""
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False, index=True)  # onboarding_step, demo_start, etc
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    # Event data
    event_data = Column(JSON, default=dict)  # Flexible event properties
    session_id = Column(String, index=True)
    meta_data = Column(JSON, default=dict)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", backref="analytics_events")


class PayPalOrder(Base):
    """PayPal order tracking for payment processing."""
    __tablename__ = "paypal_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paypal_order_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null until captured

    # Order details
    plan_id = Column(String, nullable=False)  # monthly_299, monthly_499, monthly_799
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="created")  # created, approved, captured, failed

    # PayPal data
    paypal_payer_id = Column(String)
    paypal_capture_id = Column(String)
    paypal_data = Column(JSON, default=dict)  # Full PayPal response

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="paypal_orders")
