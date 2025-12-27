"""
SQLAlchemy models for the AI Receptionist SaaS.
Defines all database tables and relationships.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
