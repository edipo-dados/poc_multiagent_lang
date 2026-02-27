"""Domain models for Pix service.

This module contains the core domain entities for the Pix payment system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class PixKeyType(str, Enum):
    """Types of Pix keys supported."""
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE = "phone"
    RANDOM = "random"


class TransactionStatus(str, Enum):
    """Status of a Pix transaction."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Account:
    """Represents a bank account in the Pix system."""
    
    id: UUID = field(default_factory=uuid4)
    account_number: str = ""
    agency: str = ""
    bank_code: str = ""
    holder_name: str = ""
    holder_document: str = ""
    balance: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate account data after initialization."""
        if isinstance(self.balance, (int, float)):
            self.balance = Decimal(str(self.balance))


@dataclass
class Pix:
    """Represents a Pix key registration."""
    
    id: UUID = field(default_factory=uuid4)
    key: str = ""
    key_type: PixKeyType = PixKeyType.RANDOM
    account_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class Transaction:
    """Represents a Pix transaction."""
    
    id: UUID = field(default_factory=uuid4)
    sender_key: str = ""
    receiver_key: str = ""
    amount: Decimal = Decimal("0.00")
    description: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))
