"""Pydantic schemas for API request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from fake_pix_repo.domain.models import PixKeyType, TransactionStatus


# Account Schemas
class AccountCreate(BaseModel):
    """Schema for creating a new account."""
    
    account_number: str = Field(..., min_length=1, max_length=20)
    agency: str = Field(..., min_length=1, max_length=10)
    bank_code: str = Field(..., min_length=1, max_length=10)
    holder_name: str = Field(..., min_length=1, max_length=255)
    holder_document: str = Field(..., min_length=1, max_length=20)
    initial_balance: Decimal = Field(default=Decimal("0.00"), ge=0)


class AccountResponse(BaseModel):
    """Schema for account response."""
    
    id: UUID
    account_number: str
    agency: str
    bank_code: str
    holder_name: str
    holder_document: str
    balance: Decimal
    created_at: datetime
    
    class Config:
        orm_mode = True


# Pix Key Schemas
class PixKeyCreate(BaseModel):
    """Schema for creating a new Pix key."""
    
    key: str = Field(..., min_length=1, max_length=255)
    key_type: PixKeyType
    account_id: UUID
    
    @validator('key')
    def validate_key_format(cls, v, values):
        """Validate key format based on key_type."""
        # Basic validation - detailed validation happens in the service layer
        if not v or not v.strip():
            raise ValueError("Key cannot be empty")
        return v.strip()


class PixKeyResponse(BaseModel):
    """Schema for Pix key response."""
    
    id: UUID
    key: str
    key_type: PixKeyType
    account_id: UUID
    created_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True


# Transaction Schemas
class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    
    sender_key: str = Field(..., min_length=1, max_length=255)
    receiver_key: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount has at most 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        return v


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    
    id: UUID
    sender_key: str
    receiver_key: str
    amount: Decimal
    description: Optional[str]
    status: TransactionStatus
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        orm_mode = True


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str
    detail: Optional[str] = None


# Success Schemas
class SuccessResponse(BaseModel):
    """Schema for generic success responses."""
    
    message: str
    data: Optional[dict] = None
