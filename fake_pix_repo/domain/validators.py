"""Business rule validators for Pix service."""

import re
from decimal import Decimal
from typing import Tuple

from .models import PixKeyType


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF format.
    
    Args:
        cpf: CPF string (can include dots and dashes)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-digit characters (dots, dashes, spaces)
    cpf = re.sub(r'\D', '', cpf)
    
    # Check length - CPF must have exactly 11 digits
    if len(cpf) != 11:
        return False
    
    # Check for known invalid CPFs (all same digit like 111.111.111-11)
    # These are technically valid by the algorithm but not issued
    if cpf == cpf[0] * 11:
        return False
    
    # Validate check digits (simplified validation)
    # In production, this should implement the full CPF validation algorithm
    return True


def validate_cnpj(cnpj: str) -> bool:
    """Validate Brazilian CNPJ format.
    
    Args:
        cnpj: CNPJ string (can include dots, dashes, and slashes)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-digit characters (dots, dashes, slashes, spaces)
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Check length - CNPJ must have exactly 14 digits
    if len(cnpj) != 14:
        return False
    
    # Check for known invalid CNPJs (all same digit like 00.000.000/0000-00)
    # These are technically valid by the algorithm but not issued
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validate check digits (simplified validation)
    # In production, this should implement the full CNPJ validation algorithm
    return True


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email address string
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate Brazilian phone number format.
    
    Args:
        phone: Phone number string (can include +55, parentheses, spaces, dashes)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-digit characters (parentheses, spaces, dashes, plus sign)
    phone = re.sub(r'\D', '', phone)
    
    # Remove country code if present (+55 for Brazil)
    if phone.startswith('55'):
        phone = phone[2:]
    
    # Check length (10 or 11 digits for Brazilian phones)
    # 10 digits: landline (XX) XXXX-XXXX
    # 11 digits: mobile (XX) 9XXXX-XXXX (9 is the mobile prefix)
    return len(phone) in [10, 11]


def validate_random_key(key: str) -> bool:
    """Validate random Pix key format (UUID).
    
    Args:
        key: Random key string
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, key.lower()))


def validate_pix_key(key: str, key_type: PixKeyType) -> Tuple[bool, str]:
    """Validate a Pix key based on its type.
    
    Args:
        key: The Pix key value
        key_type: The type of Pix key
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validators = {
        PixKeyType.CPF: (validate_cpf, "Invalid CPF format"),
        PixKeyType.CNPJ: (validate_cnpj, "Invalid CNPJ format"),
        PixKeyType.EMAIL: (validate_email, "Invalid email format"),
        PixKeyType.PHONE: (validate_phone, "Invalid phone number format"),
        PixKeyType.RANDOM: (validate_random_key, "Invalid random key format"),
    }
    
    validator, error_msg = validators.get(key_type, (lambda x: False, "Unknown key type"))
    
    if not validator(key):
        return False, error_msg
    
    return True, ""


def validate_transaction_amount(amount: Decimal) -> Tuple[bool, str]:
    """Validate transaction amount.
    
    Args:
        amount: Transaction amount
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Minimum transaction amount: R$ 0.01 (one cent)
    # This prevents zero or negative transactions
    if amount < Decimal("0.01"):
        return False, "Transaction amount must be at least R$ 0.01"
    
    # Maximum transaction amount: R$ 100,000.00
    # This is a regulatory limit for instant Pix transactions
    if amount > Decimal("100000.00"):
        return False, "Transaction amount cannot exceed R$ 100,000.00"
    
    # Check decimal places (max 2)
    # Pix transactions use Brazilian Real (BRL) which has 2 decimal places
    # exponent of -2 means 2 decimal places (e.g., 10.50)
    # exponent of -3 would mean 3 decimal places (e.g., 10.505) - invalid
    if amount.as_tuple().exponent < -2:
        return False, "Transaction amount cannot have more than 2 decimal places"
    
    return True, ""


def validate_account_balance(balance: Decimal, withdrawal_amount: Decimal) -> Tuple[bool, str]:
    """Validate if account has sufficient balance for withdrawal.
    
    Args:
        balance: Current account balance
        withdrawal_amount: Amount to withdraw
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if balance < withdrawal_amount:
        return False, f"Insufficient balance. Available: R$ {balance}, Required: R$ {withdrawal_amount}"
    
    return True, ""
