"""Basic tests for Pix key creation functionality."""

import pytest
from decimal import Decimal
from uuid import uuid4

from fake_pix_repo.domain.models import Account, Pix, PixKeyType
from fake_pix_repo.domain.validators import validate_pix_key, validate_transaction_amount


class TestPixKeyValidation:
    """Tests for Pix key validation."""
    
    def test_validate_cpf_key(self):
        """Test CPF key validation."""
        # Valid CPF format
        is_valid, error = validate_pix_key("12345678901", PixKeyType.CPF)
        assert is_valid is True
        assert error == ""
        
        # Invalid CPF (too short)
        is_valid, error = validate_pix_key("123", PixKeyType.CPF)
        assert is_valid is False
        assert "Invalid CPF format" in error
    
    def test_validate_email_key(self):
        """Test email key validation."""
        # Valid email
        is_valid, error = validate_pix_key("user@example.com", PixKeyType.EMAIL)
        assert is_valid is True
        assert error == ""
        
        # Invalid email
        is_valid, error = validate_pix_key("invalid-email", PixKeyType.EMAIL)
        assert is_valid is False
        assert "Invalid email format" in error
    
    def test_validate_phone_key(self):
        """Test phone key validation."""
        # Valid phone (11 digits)
        is_valid, error = validate_pix_key("11987654321", PixKeyType.PHONE)
        assert is_valid is True
        assert error == ""
        
        # Valid phone with formatting
        is_valid, error = validate_pix_key("+55 11 98765-4321", PixKeyType.PHONE)
        assert is_valid is True
        assert error == ""
        
        # Invalid phone (too short)
        is_valid, error = validate_pix_key("123", PixKeyType.PHONE)
        assert is_valid is False
        assert "Invalid phone number format" in error
    
    def test_validate_random_key(self):
        """Test random key (UUID) validation."""
        # Valid UUID
        is_valid, error = validate_pix_key(
            "550e8400-e29b-41d4-a716-446655440000",
            PixKeyType.RANDOM
        )
        assert is_valid is True
        assert error == ""
        
        # Invalid UUID
        is_valid, error = validate_pix_key("not-a-uuid", PixKeyType.RANDOM)
        assert is_valid is False
        assert "Invalid random key format" in error


class TestPixKeyCreation:
    """Tests for Pix key creation."""
    
    def test_create_pix_key_with_email(self):
        """Test creating a Pix key with email."""
        account_id = uuid4()
        pix = Pix(
            key="user@example.com",
            key_type=PixKeyType.EMAIL,
            account_id=account_id,
        )
        
        assert pix.key == "user@example.com"
        assert pix.key_type == PixKeyType.EMAIL
        assert pix.account_id == account_id
        assert pix.is_active is True
    
    def test_create_pix_key_with_phone(self):
        """Test creating a Pix key with phone number."""
        account_id = uuid4()
        pix = Pix(
            key="11987654321",
            key_type=PixKeyType.PHONE,
            account_id=account_id,
        )
        
        assert pix.key == "11987654321"
        assert pix.key_type == PixKeyType.PHONE
        assert pix.account_id == account_id
        assert pix.is_active is True
    
    def test_create_pix_key_with_cpf(self):
        """Test creating a Pix key with CPF."""
        account_id = uuid4()
        pix = Pix(
            key="12345678901",
            key_type=PixKeyType.CPF,
            account_id=account_id,
        )
        
        assert pix.key == "12345678901"
        assert pix.key_type == PixKeyType.CPF
        assert pix.account_id == account_id


class TestTransactionValidation:
    """Tests for transaction validation."""
    
    def test_validate_valid_amount(self):
        """Test validation of valid transaction amounts."""
        # Valid amount
        is_valid, error = validate_transaction_amount(Decimal("100.50"))
        assert is_valid is True
        assert error == ""
        
        # Minimum valid amount
        is_valid, error = validate_transaction_amount(Decimal("0.01"))
        assert is_valid is True
        assert error == ""
    
    def test_validate_amount_too_small(self):
        """Test validation rejects amounts below minimum."""
        is_valid, error = validate_transaction_amount(Decimal("0.00"))
        assert is_valid is False
        assert "at least R$ 0.01" in error
    
    def test_validate_amount_too_large(self):
        """Test validation rejects amounts above maximum."""
        is_valid, error = validate_transaction_amount(Decimal("100001.00"))
        assert is_valid is False
        assert "cannot exceed R$ 100,000.00" in error
    
    def test_validate_amount_too_many_decimals(self):
        """Test validation rejects amounts with more than 2 decimal places."""
        is_valid, error = validate_transaction_amount(Decimal("100.123"))
        assert is_valid is False
        assert "more than 2 decimal places" in error


class TestAccountCreation:
    """Tests for account creation."""
    
    def test_create_account_with_initial_balance(self):
        """Test creating an account with initial balance."""
        account = Account(
            account_number="12345",
            agency="0001",
            bank_code="001",
            holder_name="John Doe",
            holder_document="12345678901",
            balance=Decimal("1000.00"),
        )
        
        assert account.account_number == "12345"
        assert account.agency == "0001"
        assert account.bank_code == "001"
        assert account.holder_name == "John Doe"
        assert account.holder_document == "12345678901"
        assert account.balance == Decimal("1000.00")
    
    def test_create_account_with_zero_balance(self):
        """Test creating an account with zero balance."""
        account = Account(
            account_number="12345",
            agency="0001",
            bank_code="001",
            holder_name="Jane Doe",
            holder_document="98765432109",
        )
        
        assert account.balance == Decimal("0.00")
