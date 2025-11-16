"""
Bank Account API Endpoints
Handles bank account management and verification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import Dict, Any, List
from datetime import datetime
import uuid

from config.database import get_db
from config.settings import settings
from core.security import get_current_user
from core.exceptions import GamePlatformException
from models.user import User
from models.kyc import BankAccount
from schemas.kyc import (
    AddBankAccountRequest,
    BankAccountResponse,
    BankAccountListResponse,
    SetPrimaryBankAccountRequest,
    VerifyBankAccountRequest,
    VerifyBankAccountResponse
)

router = APIRouter()


# ============================================================================
# Bank Account Endpoints
# ============================================================================

@router.post("/add", response_model=Dict[str, Any])
async def add_bank_account(
    request_data: AddBankAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new bank account
    """
    try:
        # Check if account already exists
        existing = await db.execute(
            select(BankAccount).where(
                and_(
                    BankAccount.user_id == current_user.id,
                    BankAccount.account_number == request_data.account_number,
                    BankAccount.ifsc_code == request_data.ifsc_code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This bank account is already added"
            )

        # Check maximum accounts limit
        count_result = await db.execute(
            select(BankAccount).where(
                and_(
                    BankAccount.user_id == current_user.id,
                    BankAccount.status == "active"
                )
            )
        )
        active_accounts = count_result.scalars().all()

        if len(active_accounts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 bank accounts allowed per user"
            )

        # Check if this will be the first account (make it primary)
        is_first_account = len(active_accounts) == 0

        # Fetch bank details from IFSC (in production, use IFSC API)
        bank_name, branch_name = await _get_bank_details_from_ifsc(request_data.ifsc_code)

        # Create bank account
        bank_account = BankAccount(
            id=uuid.uuid4(),
            user_id=current_user.id,
            account_holder_name=request_data.account_holder_name,
            account_number=request_data.account_number,  # In production, encrypt this
            ifsc_code=request_data.ifsc_code,
            bank_name=bank_name,
            branch_name=branch_name,
            account_type=request_data.account_type,
            is_primary=is_first_account,
            status="active"
        )

        db.add(bank_account)
        await db.commit()
        await db.refresh(bank_account)

        return {
            "success": True,
            "data": {
                "message": "Bank account added successfully",
                "bank_account": _format_bank_account_response(bank_account),
                "verification_required": True
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add bank account: {str(e)}"
        )


@router.get("/list", response_model=Dict[str, Any])
async def list_bank_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of user's bank accounts
    """
    try:
        result = await db.execute(
            select(BankAccount)
            .where(BankAccount.user_id == current_user.id)
            .order_by(BankAccount.is_primary.desc(), BankAccount.created_at.desc())
        )
        accounts = result.scalars().all()

        # Find primary account
        primary_account_id = None
        accounts_response = []

        for account in accounts:
            if account.is_primary:
                primary_account_id = str(account.id)

            accounts_response.append(_format_bank_account_response(account))

        return {
            "success": True,
            "data": {
                "bank_accounts": accounts_response,
                "primary_account_id": primary_account_id,
                "total_count": len(accounts_response)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bank accounts: {str(e)}"
        )


@router.post("/set-primary", response_model=Dict[str, Any])
async def set_primary_bank_account(
    request_data: SetPrimaryBankAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Set a bank account as primary for withdrawals
    """
    try:
        # Get the account to be set as primary
        result = await db.execute(
            select(BankAccount).where(BankAccount.id == uuid.UUID(request_data.bank_account_id))
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this bank account"
            )

        # Check if account is active
        if account.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set inactive account as primary"
            )

        # Unset all primary accounts
        await db.execute(
            update(BankAccount)
            .where(BankAccount.user_id == current_user.id)
            .values(is_primary=False)
        )

        # Set this account as primary
        account.is_primary = True

        await db.commit()
        await db.refresh(account)

        return {
            "success": True,
            "data": {
                "message": "Primary bank account updated successfully",
                "bank_account": _format_bank_account_response(account)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set primary account: {str(e)}"
        )


@router.delete("/{bank_account_id}", response_model=Dict[str, Any])
async def delete_bank_account(
    bank_account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) a bank account
    """
    try:
        # Get the account
        result = await db.execute(
            select(BankAccount).where(BankAccount.id == uuid.UUID(bank_account_id))
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this bank account"
            )

        # Don't actually delete, just mark as inactive
        account.status = "inactive"

        # If this was primary, set another account as primary
        if account.is_primary:
            account.is_primary = False

            # Find another active account to make primary
            other_accounts = await db.execute(
                select(BankAccount).where(
                    and_(
                        BankAccount.user_id == current_user.id,
                        BankAccount.status == "active",
                        BankAccount.id != account.id
                    )
                ).limit(1)
            )
            other_account = other_accounts.scalar_one_or_none()

            if other_account:
                other_account.is_primary = True

        await db.commit()

        return {
            "success": True,
            "data": {
                "message": "Bank account deleted successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bank account: {str(e)}"
        )


@router.post("/verify", response_model=Dict[str, Any])
async def verify_bank_account(
    request_data: VerifyBankAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify bank account using penny drop or manual verification
    """
    try:
        # Get the account
        result = await db.execute(
            select(BankAccount).where(BankAccount.id == uuid.UUID(request_data.bank_account_id))
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        # Verify ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify this bank account"
            )

        # Check if already verified
        if account.is_verified:
            return {
                "success": True,
                "data": {
                    "message": "Bank account is already verified",
                    "bank_account": _format_bank_account_response(account),
                    "verification_status": "verified"
                }
            }

        # In production, integrate with payment gateway for penny drop
        # For now, simulate verification
        verification_success = await _perform_penny_drop_verification(account)

        if verification_success:
            account.is_verified = True
            account.verification_method = "penny_drop"
            account.verified_at = datetime.utcnow()
            account.verification_reference = f"PD{uuid.uuid4().hex[:12].upper()}"

            await db.commit()
            await db.refresh(account)

            return {
                "success": True,
                "data": {
                    "message": "Bank account verified successfully",
                    "bank_account": _format_bank_account_response(account),
                    "verification_status": "verified"
                }
            }
        else:
            return {
                "success": False,
                "data": {
                    "message": "Bank account verification failed. Please check account details.",
                    "verification_status": "failed"
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _format_bank_account_response(account: BankAccount) -> BankAccountResponse:
    """Format bank account for response"""
    return BankAccountResponse(
        id=str(account.id),
        account_holder_name=account.account_holder_name,
        account_number=_mask_account_number(account.account_number),
        ifsc_code=account.ifsc_code,
        bank_name=account.bank_name,
        branch_name=account.branch_name,
        account_type=account.account_type,
        is_verified=account.is_verified,
        is_primary=account.is_primary,
        status=account.status,
        verified_at=account.verified_at,
        created_at=account.created_at
    )


def _mask_account_number(account_number: str) -> str:
    """Mask account number showing only last 4 digits"""
    if not account_number or len(account_number) < 4:
        return "XXXX"

    return f"{'X' * (len(account_number) - 4)}{account_number[-4:]}"


async def _get_bank_details_from_ifsc(ifsc_code: str) -> tuple:
    """
    Fetch bank details from IFSC code
    In production, integrate with IFSC API (https://ifsc.razorpay.com/)
    """
    # Simulated response - in production, call actual API
    # Example: https://ifsc.razorpay.com/SBIN0001234

    # For now, extract bank code from IFSC
    bank_code = ifsc_code[:4]

    bank_mapping = {
        "SBIN": "State Bank of India",
        "HDFC": "HDFC Bank",
        "ICIC": "ICICI Bank",
        "UTIB": "Axis Bank",
        "KKBK": "Kotak Mahindra Bank",
        "PUNB": "Punjab National Bank",
        "BARB": "Bank of Baroda",
        "CNRB": "Canara Bank",
        "UBIN": "Union Bank of India",
        "IDIB": "Indian Bank"
    }

    bank_name = bank_mapping.get(bank_code, "Unknown Bank")
    branch_name = "Main Branch"  # In production, get from API

    return bank_name, branch_name


async def _perform_penny_drop_verification(account: BankAccount) -> bool:
    """
    Perform penny drop verification via payment gateway
    In production, integrate with Razorpay/Cashfree penny drop API
    """
    # Simulated verification - in production, call payment gateway API
    # This would typically:
    # 1. Transfer small amount (¹1) to the account
    # 2. Verify account holder name matches
    # 3. Return success/failure

    # For development, auto-verify
    return True
