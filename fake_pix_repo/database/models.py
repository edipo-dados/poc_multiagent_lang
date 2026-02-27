"""SQLAlchemy ORM models for Pix service database."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from fake_pix_repo.domain.models import PixKeyType, TransactionStatus

Base = declarative_base()


class AccountModel(Base):
    """Database model for bank accounts."""
    
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_number = Column(String(20), nullable=False)
    agency = Column(String(10), nullable=False)
    bank_code = Column(String(10), nullable=False)
    holder_name = Column(String(255), nullable=False)
    holder_document = Column(String(20), nullable=False, unique=True)
    balance = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    pix_keys = relationship("PixModel", back_populates="account")


class PixModel(Base):
    """Database model for Pix key registrations."""
    
    __tablename__ = "pix_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key = Column(String(255), nullable=False, unique=True)
    key_type = Column(Enum(PixKeyType), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    account = relationship("AccountModel", back_populates="pix_keys")


class TransactionModel(Base):
    """Database model for Pix transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sender_key = Column(String(255), nullable=False)
    receiver_key = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
