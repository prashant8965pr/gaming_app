"""
Admin API Endpoints
Handles admin operations for KYC approval, withdrawal processing, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func
from typing import Dict, Any, List
from datetime import datetime
import uuid

from config.database import get_db
from config.settings import settings
from core.security import get_current_user
from core.exceptions import GamePlatformException
from models.user import User
from models.kyc import KYCDocument, KYCVerificationHistory
from models.wallet import WithdrawalRequest, Transaction, Wallet
from schemas.kyc import ReviewKYCRequest, KYCReviewResponse, KYCDocumentResponse
from schemas.wallet import (
    ReviewWithdrawalRequest,
    ProcessWithdrawalPayoutRequest,
    WithdrawalRequestResponse,
    AdminAdjustBalanceRequest,
    AdminTransactionResponse,
    TransactionResponse
)

router = APIRouter()


# ============================================================================
# Helper: Check if user is admin
# ============================================================================

async def _check_admin_permissions(current_user: User):
    """Check if user has admin permissions"""
    # In production, check user role from database
    # For now, simple check (you can add admin role to User model)
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        # Temporary: Allow all for development
        # In production, uncomment this:
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Admin access required"
        # )
        pass


# ============================================================================
# KYC Management Endpoints
# ============================================================================

@router.get("/kyc/pending", response_model=Dict[str, Any])
async def get_pending_kyc_documents(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of pending KYC documents for review
    """
    await _check_admin_permissions(current_user)

    try:
        # Get pending KYC documents
        result = await db.execute(
            select(KYCDocument)
            .where(KYCDocument.status.in_(["pending", "under_review"]))
            .order_by(KYCDocument.submitted_at.asc())
            .offset(offset)
            .limit(limit)
        )
        documents = result.scalars().all()

        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(KYCDocument)
            .where(KYCDocument.status.in_(["pending", "under_review"]))
        )
        total_count = count_result.scalar()

        documents_response = []
        for doc in documents:
            documents_response.append(KYCDocumentResponse(
                id=str(doc.id),
                user_id=str(doc.user_id),
                document_type=doc.document_type,
                document_number=doc.document_number,  # Admin can see full number
                full_name=doc.full_name,
                date_of_birth=doc.date_of_birth,
                status=doc.status,
                document_front_url=doc.document_front_url,
                document_back_url=doc.document_back_url,
                selfie_url=doc.selfie_url,
                rejection_reason=doc.rejection_reason,
                submitted_at=doc.submitted_at,
                reviewed_at=doc.reviewed_at,
                created_at=doc.created_at
            ))

        return {
            "success": True,
            "data": {
                "documents": documents_response,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending KYC documents: {str(e)}"
        )


@router.post("/kyc/review", response_model=Dict[str, Any])
async def review_kyc_document(
    request_data: ReviewKYCRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Review and approve/reject KYC document
    """
    await _check_admin_permissions(current_user)

    try:
        # Get KYC document
        result = await db.execute(
            select(KYCDocument).where(KYCDocument.id == uuid.UUID(request_data.kyc_id))
        )
        kyc_document = result.scalar_one_or_none()

        if not kyc_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KYC document not found"
            )

        # Check if already processed
        if kyc_document.status in ["approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"KYC document already {kyc_document.status}"
            )

        old_status = kyc_document.status

        # Update KYC document based on action
        if request_data.action == "approve":
            kyc_document.status = "approved"

            # Update user's KYC status
            user_result = await db.execute(
                select(User).where(User.id == kyc_document.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                user.kyc_status = "verified"

        elif request_data.action == "reject":
            kyc_document.status = "rejected"
            kyc_document.rejection_reason = request_data.rejection_reason

        elif request_data.action == "request_resubmit":
            kyc_document.status = "pending"
            kyc_document.rejection_reason = request_data.rejection_reason

        kyc_document.reviewed_by = current_user.id
        kyc_document.reviewed_at = datetime.utcnow()
        kyc_document.admin_notes = request_data.admin_notes

        # Create verification history
        history = KYCVerificationHistory(
            id=uuid.uuid4(),
            user_id=kyc_document.user_id,
            kyc_document_id=kyc_document.id,
            action=request_data.action,
            performed_by=current_user.id,
            old_status=old_status,
            new_status=kyc_document.status,
            notes=request_data.admin_notes
        )

        db.add(history)
        await db.commit()
        await db.refresh(kyc_document)

        return {
            "success": True,
            "data": {
                "message": f"KYC document {request_data.action}d successfully",
                "kyc_document": KYCDocumentResponse(
                    id=str(kyc_document.id),
                    user_id=str(kyc_document.user_id),
                    document_type=kyc_document.document_type,
                    document_number=kyc_document.document_number,
                    full_name=kyc_document.full_name,
                    date_of_birth=kyc_document.date_of_birth,
                    status=kyc_document.status,
                    document_front_url=kyc_document.document_front_url,
                    document_back_url=kyc_document.document_back_url,
                    selfie_url=kyc_document.selfie_url,
                    rejection_reason=kyc_document.rejection_reason,
                    submitted_at=kyc_document.submitted_at,
                    reviewed_at=kyc_document.reviewed_at,
                    created_at=kyc_document.created_at
                )
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KYC review failed: {str(e)}"
        )


# ============================================================================
# Withdrawal Management Endpoints
# ============================================================================

@router.get("/withdrawals/pending", response_model=Dict[str, Any])
async def get_pending_withdrawals(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of pending withdrawal requests
    """
    await _check_admin_permissions(current_user)

    try:
        # Get pending withdrawals
        result = await db.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.status.in_(["pending", "processing"]))
            .order_by(WithdrawalRequest.requested_at.asc())
            .offset(offset)
            .limit(limit)
        )
        withdrawals = result.scalars().all()

        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(WithdrawalRequest)
            .where(WithdrawalRequest.status.in_(["pending", "processing"]))
        )
        total_count = count_result.scalar()

        withdrawals_response = []
        for w in withdrawals:
            withdrawals_response.append(WithdrawalRequestResponse(
                id=str(w.id),
                requested_amount=w.requested_amount / 100.0,
                tds_amount=w.tds_amount / 100.0,
                processing_fee=w.processing_fee / 100.0,
                final_amount=w.final_amount / 100.0,
                status=w.status,
                account_holder_name=w.account_holder_name,
                account_number=w.account_number,  # Admin sees full number
                ifsc_code=w.ifsc_code,
                bank_name=w.bank_name,
                utr_number=w.utr_number,
                rejection_reason=w.rejection_reason,
                requested_at=w.requested_at,
                completed_at=w.completed_at
            ))

        return {
            "success": True,
            "data": {
                "withdrawals": withdrawals_response,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending withdrawals: {str(e)}"
        )


@router.post("/withdrawals/review", response_model=Dict[str, Any])
async def review_withdrawal_request(
    request_data: ReviewWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve or reject withdrawal request
    """
    await _check_admin_permissions(current_user)

    try:
        # Get withdrawal request
        result = await db.execute(
            select(WithdrawalRequest).where(
                WithdrawalRequest.id == uuid.UUID(request_data.withdrawal_id)
            )
        )
        withdrawal = result.scalar_one_or_none()

        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )

        # Check if already processed
        if withdrawal.status not in ["pending", "processing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Withdrawal already {withdrawal.status}"
            )

        if request_data.action == "approve":
            withdrawal.status = "processing"
            withdrawal.reviewed_by = current_user.id
            withdrawal.reviewed_at = datetime.utcnow()
            withdrawal.admin_notes = request_data.admin_notes

            message = "Withdrawal approved and ready for payout"

        elif request_data.action == "reject":
            withdrawal.status = "rejected"
            withdrawal.rejection_reason = request_data.rejection_reason
            withdrawal.reviewed_by = current_user.id
            withdrawal.reviewed_at = datetime.utcnow()
            withdrawal.admin_notes = request_data.admin_notes

            # Refund amount to user's wallet
            cash_result = await db.execute(
                select(Wallet).where(
                    and_(
                        Wallet.user_id == withdrawal.user_id,
                        Wallet.wallet_type == "cash"
                    )
                )
            )
            cash_wallet = cash_result.scalar_one_or_none()

            if cash_wallet:
                # Create refund transaction
                balance_before = cash_wallet.balance
                refund_amount = withdrawal.requested_amount
                balance_after = balance_before + refund_amount

                refund_txn = Transaction(
                    id=uuid.uuid4(),
                    user_id=withdrawal.user_id,
                    wallet_id=cash_wallet.id,
                    transaction_type="refund",
                    amount=refund_amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status="completed",
                    description=f"Withdrawal rejected - Refund",
                    withdrawal_request_id=withdrawal.id,
                    processed_by=current_user.id,
                    processed_at=datetime.utcnow()
                )

                db.add(refund_txn)
                cash_wallet.balance = balance_after

            message = "Withdrawal rejected and amount refunded"

        elif request_data.action == "complete":
            withdrawal.status = "completed"
            withdrawal.completed_at = datetime.utcnow()
            withdrawal.utr_number = request_data.utr_number
            withdrawal.admin_notes = request_data.admin_notes

            message = "Withdrawal completed successfully"

        await db.commit()
        await db.refresh(withdrawal)

        return {
            "success": True,
            "data": {
                "message": message,
                "withdrawal": WithdrawalRequestResponse(
                    id=str(withdrawal.id),
                    requested_amount=withdrawal.requested_amount / 100.0,
                    tds_amount=withdrawal.tds_amount / 100.0,
                    processing_fee=withdrawal.processing_fee / 100.0,
                    final_amount=withdrawal.final_amount / 100.0,
                    status=withdrawal.status,
                    account_holder_name=withdrawal.account_holder_name,
                    account_number=withdrawal.account_number,
                    ifsc_code=withdrawal.ifsc_code,
                    bank_name=withdrawal.bank_name,
                    utr_number=withdrawal.utr_number,
                    rejection_reason=withdrawal.rejection_reason,
                    requested_at=withdrawal.requested_at,
                    completed_at=withdrawal.completed_at
                )
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Withdrawal review failed: {str(e)}"
        )


@router.post("/withdrawals/process-payout", response_model=Dict[str, Any])
async def process_withdrawal_payout(
    request_data: ProcessWithdrawalPayoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payout for approved withdrawal (update with UTR/payout ID)
    """
    await _check_admin_permissions(current_user)

    try:
        # Get withdrawal request
        result = await db.execute(
            select(WithdrawalRequest).where(
                WithdrawalRequest.id == uuid.UUID(request_data.withdrawal_id)
            )
        )
        withdrawal = result.scalar_one_or_none()

        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )

        if withdrawal.status != "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Withdrawal must be in processing status"
            )

        # Update withdrawal with payout details
        withdrawal.status = "completed"
        withdrawal.utr_number = request_data.utr_number
        withdrawal.gateway_payout_id = request_data.gateway_payout_id
        withdrawal.admin_notes = request_data.admin_notes
        withdrawal.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(withdrawal)

        return {
            "success": True,
            "data": {
                "message": "Withdrawal payout processed successfully",
                "withdrawal": WithdrawalRequestResponse(
                    id=str(withdrawal.id),
                    requested_amount=withdrawal.requested_amount / 100.0,
                    tds_amount=withdrawal.tds_amount / 100.0,
                    processing_fee=withdrawal.processing_fee / 100.0,
                    final_amount=withdrawal.final_amount / 100.0,
                    status=withdrawal.status,
                    account_holder_name=withdrawal.account_holder_name,
                    account_number=withdrawal.account_number,
                    ifsc_code=withdrawal.ifsc_code,
                    bank_name=withdrawal.bank_name,
                    utr_number=withdrawal.utr_number,
                    rejection_reason=withdrawal.rejection_reason,
                    requested_at=withdrawal.requested_at,
                    completed_at=withdrawal.completed_at
                )
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payout processing failed: {str(e)}"
        )


# ============================================================================
# Manual Balance Adjustment Endpoints
# ============================================================================

@router.post("/wallet/adjust-balance", response_model=Dict[str, Any])
async def adjust_user_balance(
    request_data: AdminAdjustBalanceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually adjust user's wallet balance (admin only)
    """
    await _check_admin_permissions(current_user)

    try:
        # Get user's wallet
        result = await db.execute(
            select(Wallet).where(
                and_(
                    Wallet.user_id == uuid.UUID(request_data.user_id),
                    Wallet.wallet_type == request_data.wallet_type
                )
            )
        )
        wallet = result.scalar_one_or_none()

        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet not found for user"
            )

        # Convert amount to paise
        amount_paise = int(request_data.amount * 100)

        # Create transaction
        balance_before = wallet.balance
        balance_after = balance_before + amount_paise

        if balance_after < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance for debit"
            )

        transaction_type = "admin_credit" if amount_paise > 0 else "admin_debit"

        transaction = Transaction(
            id=uuid.uuid4(),
            user_id=uuid.UUID(request_data.user_id),
            wallet_id=wallet.id,
            transaction_type=transaction_type,
            amount=amount_paise,
            balance_before=balance_before,
            balance_after=balance_after,
            status="completed",
            description=request_data.reason,
            admin_notes=request_data.admin_notes,
            processed_by=current_user.id,
            processed_at=datetime.utcnow()
        )

        db.add(transaction)

        # Update wallet balance
        wallet.balance = balance_after

        await db.commit()
        await db.refresh(transaction)
        await db.refresh(wallet)

        return {
            "success": True,
            "data": {
                "message": "Balance adjusted successfully",
                "transaction": TransactionResponse(
                    id=str(transaction.id),
                    transaction_type=transaction.transaction_type,
                    amount=transaction.amount / 100.0,
                    balance_before=transaction.balance_before / 100.0,
                    balance_after=transaction.balance_after / 100.0,
                    status=transaction.status,
                    description=transaction.description,
                    payment_gateway=None,
                    payment_method=None,
                    gateway_transaction_id=None,
                    tds_amount=0.0,
                    created_at=transaction.created_at
                ),
                "wallet_balance": {
                    "wallet_type": wallet.wallet_type,
                    "balance": wallet.balance / 100.0
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Balance adjustment failed: {str(e)}"
        )
