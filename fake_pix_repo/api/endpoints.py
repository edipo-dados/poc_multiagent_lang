"""FastAPI endpoints for Pix service."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from fake_pix_repo.api.schemas import (
    AccountCreate,
    AccountResponse,
    ErrorResponse,
    PixKeyCreate,
    PixKeyResponse,
    TransactionCreate,
    TransactionResponse,
)
from fake_pix_repo.domain.models import Account, Pix, Transaction
from fake_pix_repo.domain.validators import validate_pix_key, validate_transaction_amount

# Create router
router = APIRouter(prefix="/api/v1", tags=["pix"])

# In-memory storage (for demonstration purposes)
# In a real application, this would be replaced with database operations
accounts_db: dict[UUID, Account] = {}
pix_keys_db: dict[str, Pix] = {}
transactions_db: dict[UUID, Transaction] = {}


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def create_account(account_data: AccountCreate) -> AccountResponse:
    """Create a new bank account.
    
    Args:
        account_data: Account creation data
        
    Returns:
        Created account information
        
    Raises:
        HTTPException: If account with same document already exists
    """
    # Check if account with same document already exists
    # In Brazil, each CPF/CNPJ can only have one account per bank
    for account in accounts_db.values():
        if account.holder_document == account_data.holder_document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with document {account_data.holder_document} already exists"
            )
    
    # Create new account with auto-generated UUID
    account = Account(
        account_number=account_data.account_number,
        agency=account_data.agency,
        bank_code=account_data.bank_code,
        holder_name=account_data.holder_name,
        holder_document=account_data.holder_document,
        balance=account_data.initial_balance,
    )
    
    # Store in in-memory database (would be DB operation in production)
    accounts_db[account.id] = account
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        agency=account.agency,
        bank_code=account.bank_code,
        holder_name=account.holder_name,
        holder_document=account.holder_document,
        balance=account.balance,
        created_at=account.created_at,
    )


@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_account(account_id: UUID) -> AccountResponse:
    """Get account by ID.
    
    Args:
        account_id: Account UUID
        
    Returns:
        Account information
        
    Raises:
        HTTPException: If account not found
    """
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_id} not found"
        )
    
    return AccountResponse(
        id=account.id,
        account_number=account.account_number,
        agency=account.agency,
        bank_code=account.bank_code,
        holder_name=account.holder_name,
        holder_document=account.holder_document,
        balance=account.balance,
        created_at=account.created_at,
    )


@router.post(
    "/pix",
    response_model=PixKeyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def create_pix_key(pix_data: PixKeyCreate) -> PixKeyResponse:
    """Create a new Pix key registration.
    
    Args:
        pix_data: Pix key creation data
        
    Returns:
        Created Pix key information
        
    Raises:
        HTTPException: If validation fails or account not found
    """
    # Validate account exists before creating Pix key
    # This ensures referential integrity
    account = accounts_db.get(pix_data.account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {pix_data.account_id} not found"
        )
    
    # Validate Pix key format based on key type
    # Each key type has specific format requirements (CPF, email, phone, etc.)
    is_valid, error_msg = validate_pix_key(pix_data.key, pix_data.key_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Check if key already exists
    # Each Pix key must be unique across the entire system
    if pix_data.key in pix_keys_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pix key {pix_data.key} already registered"
        )
    
    # Create new Pix key with auto-generated UUID
    pix = Pix(
        key=pix_data.key,
        key_type=pix_data.key_type,
        account_id=pix_data.account_id,
    )
    
    # Store in in-memory database (would be DB operation in production)
    pix_keys_db[pix.key] = pix
    
    return PixKeyResponse(
        id=pix.id,
        key=pix.key,
        key_type=pix.key_type,
        account_id=pix.account_id,
        created_at=pix.created_at,
        is_active=pix.is_active,
    )


@router.get(
    "/pix/{pix_key}",
    response_model=PixKeyResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_pix_key(pix_key: str) -> PixKeyResponse:
    """Get Pix key information.
    
    Args:
        pix_key: Pix key value
        
    Returns:
        Pix key information
        
    Raises:
        HTTPException: If Pix key not found
    """
    pix = pix_keys_db.get(pix_key)
    if not pix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pix key {pix_key} not found"
        )
    
    return PixKeyResponse(
        id=pix.id,
        key=pix.key,
        key_type=pix.key_type,
        account_id=pix.account_id,
        created_at=pix.created_at,
        is_active=pix.is_active,
    )


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def create_transaction(transaction_data: TransactionCreate) -> TransactionResponse:
    """Create a new Pix transaction.
    
    Args:
        transaction_data: Transaction creation data
        
    Returns:
        Created transaction information
        
    Raises:
        HTTPException: If validation fails or keys not found
    """
    # Validate transaction amount against regulatory limits
    # Ensures compliance with Pix transaction rules
    is_valid, error_msg = validate_transaction_amount(transaction_data.amount)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Validate sender Pix key exists
    # Both sender and receiver must have registered Pix keys
    sender_pix = pix_keys_db.get(transaction_data.sender_key)
    if not sender_pix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sender Pix key {transaction_data.sender_key} not found"
        )
    
    # Validate receiver Pix key exists
    receiver_pix = pix_keys_db.get(transaction_data.receiver_key)
    if not receiver_pix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receiver Pix key {transaction_data.receiver_key} not found"
        )
    
    # Create new transaction with PENDING status
    # In a real system, this would trigger payment processing
    transaction = Transaction(
        sender_key=transaction_data.sender_key,
        receiver_key=transaction_data.receiver_key,
        amount=transaction_data.amount,
        description=transaction_data.description or "",
    )
    
    # Store in in-memory database (would be DB operation in production)
    transactions_db[transaction.id] = transaction
    
    return TransactionResponse(
        id=transaction.id,
        sender_key=transaction.sender_key,
        receiver_key=transaction.receiver_key,
        amount=transaction.amount,
        description=transaction.description,
        status=transaction.status,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at,
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_transaction(transaction_id: UUID) -> TransactionResponse:
    """Get transaction by ID.
    
    Args:
        transaction_id: Transaction UUID
        
    Returns:
        Transaction information
        
    Raises:
        HTTPException: If transaction not found
    """
    transaction = transactions_db.get(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    return TransactionResponse(
        id=transaction.id,
        sender_key=transaction.sender_key,
        receiver_key=transaction.receiver_key,
        amount=transaction.amount,
        description=transaction.description,
        status=transaction.status,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at,
    )


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
)
async def list_transactions() -> List[TransactionResponse]:
    """List all transactions.
    
    Returns:
        List of all transactions
    """
    return [
        TransactionResponse(
            id=transaction.id,
            sender_key=transaction.sender_key,
            receiver_key=transaction.receiver_key,
            amount=transaction.amount,
            description=transaction.description,
            status=transaction.status,
            created_at=transaction.created_at,
            completed_at=transaction.completed_at,
        )
        for transaction in transactions_db.values()
    ]
