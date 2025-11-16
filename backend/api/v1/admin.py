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
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


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


# ============================================================================
# Dashboard Statistics Endpoints
# ============================================================================

@router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get admin dashboard statistics
    """
    await _check_admin_permissions(current_user)

    try:
        from models.game import GameSession
        from datetime import timedelta

        # Total users count
        total_users_result = await db.execute(select(func.count()).select_from(User))
        total_users = total_users_result.scalar()

        # Active users (logged in last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users_result = await db.execute(
            select(func.count()).select_from(User).where(User.last_login_at >= seven_days_ago)
        )
        active_users = active_users_result.scalar()

        # New users today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today_result = await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= today_start)
        )
        new_users_today = new_users_today_result.scalar()

        # Suspended/Banned users
        suspended_users_result = await db.execute(
            select(func.count()).select_from(User).where(User.status.in_(["suspended", "banned"]))
        )
        suspended_users = suspended_users_result.scalar()

        # KYC statistics
        pending_kyc_result = await db.execute(
            select(func.count()).select_from(KYCDocument).where(KYCDocument.status.in_(["pending", "under_review"]))
        )
        pending_kyc = pending_kyc_result.scalar()

        approved_kyc_result = await db.execute(
            select(func.count()).select_from(User).where(User.kyc_status == "verified")
        )
        approved_kyc = approved_kyc_result.scalar()

        # Withdrawal statistics
        pending_withdrawals_result = await db.execute(
            select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status.in_(["pending", "processing"]))
        )
        pending_withdrawals = pending_withdrawals_result.scalar()

        pending_withdrawal_amount_result = await db.execute(
            select(func.sum(WithdrawalRequest.final_amount)).where(WithdrawalRequest.status.in_(["pending", "processing"]))
        )
        pending_withdrawal_amount = pending_withdrawal_amount_result.scalar() or 0

        # Transaction statistics (today)
        total_deposits_today_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.transaction_type == "deposit",
                    Transaction.status == "completed",
                    Transaction.created_at >= today_start
                )
            )
        )
        total_deposits_today = total_deposits_today_result.scalar() or 0

        total_withdrawals_today_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.transaction_type == "withdrawal",
                    Transaction.status == "completed",
                    Transaction.created_at >= today_start
                )
            )
        )
        total_withdrawals_today = total_withdrawals_today_result.scalar() or 0

        # Game session statistics
        active_sessions_result = await db.execute(
            select(func.count()).select_from(GameSession).where(GameSession.status.in_(["waiting", "in_progress"]))
        )
        active_sessions = active_sessions_result.scalar()

        # Total revenue (all time)
        total_revenue_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.transaction_type == "deposit",
                    Transaction.status == "completed"
                )
            )
        )
        total_revenue = total_revenue_result.scalar() or 0

        return {
            "success": True,
            "data": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new_today": new_users_today,
                    "suspended": suspended_users
                },
                "kyc": {
                    "pending": pending_kyc,
                    "approved": approved_kyc
                },
                "withdrawals": {
                    "pending_count": pending_withdrawals,
                    "pending_amount": pending_withdrawal_amount / 100.0
                },
                "transactions": {
                    "deposits_today": total_deposits_today / 100.0,
                    "withdrawals_today": total_withdrawals_today / 100.0,
                    "revenue_total": total_revenue / 100.0
                },
                "sessions": {
                    "active": active_sessions
                }
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )


# ============================================================================
# User Management Endpoints
# ============================================================================

@router.get("/users", response_model=Dict[str, Any])
async def get_all_users(
    limit: int = 50,
    offset: int = 0,
    search: str = None,
    status_filter: str = None,
    kyc_status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all users with filtering and pagination
    """
    await _check_admin_permissions(current_user)

    try:
        from models.user import UserStatistics

        # Build query
        query = select(User)

        # Apply filters
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (User.username.ilike(search_pattern)) |
                (User.email.ilike(search_pattern)) |
                (User.phone.ilike(search_pattern))
            )

        if status_filter:
            query = query.where(User.status == status_filter)

        if kyc_status_filter:
            query = query.where(User.kyc_status == kyc_status_filter)

        # Get total count
        count_query = select(func.count()).select_from(User)
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                (User.username.ilike(search_pattern)) |
                (User.email.ilike(search_pattern)) |
                (User.phone.ilike(search_pattern))
            )
        if status_filter:
            count_query = count_query.where(User.status == status_filter)
        if kyc_status_filter:
            count_query = count_query.where(User.kyc_status == kyc_status_filter)

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar()

        # Apply pagination
        query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)

        # Execute query
        result = await db.execute(query)
        users = result.scalars().all()

        # Build response
        users_data = []
        for user in users:
            # Get user statistics
            stats_result = await db.execute(
                select(UserStatistics).where(UserStatistics.user_id == user.id)
            )
            stats = stats_result.scalar_one_or_none()

            # Get wallet balances
            wallets_result = await db.execute(
                select(Wallet).where(Wallet.user_id == user.id)
            )
            wallets = wallets_result.scalars().all()
            total_balance = sum(w.balance for w in wallets)

            users_data.append({
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name,
                "role": user.role,
                "status": user.status,
                "kyc_status": user.kyc_status,
                "is_email_verified": user.is_email_verified,
                "is_phone_verified": user.is_phone_verified,
                "total_balance": total_balance / 100.0 if total_balance else 0.0,
                "games_played": stats.total_games_played if stats else 0,
                "total_winnings": stats.total_winnings / 100.0 if stats else 0.0,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at
            })

        return {
            "success": True,
            "data": {
                "users": users_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user_details(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific user
    """
    await _check_admin_permissions(current_user)

    try:
        from models.user import UserStatistics, UserProfile

        # Get user
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get user statistics
        stats_result = await db.execute(
            select(UserStatistics).where(UserStatistics.user_id == user.id)
        )
        stats = stats_result.scalar_one_or_none()

        # Get user profile
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()

        # Get wallets
        wallets_result = await db.execute(
            select(Wallet).where(Wallet.user_id == user.id)
        )
        wallets = wallets_result.scalars().all()

        wallets_data = [
            {
                "wallet_type": w.wallet_type,
                "balance": w.balance / 100.0
            }
            for w in wallets
        ]

        # Get recent transactions
        recent_txns_result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
            .limit(10)
        )
        recent_txns = recent_txns_result.scalars().all()

        transactions_data = [
            {
                "id": str(t.id),
                "type": t.transaction_type,
                "amount": t.amount / 100.0,
                "status": t.status,
                "description": t.description,
                "created_at": t.created_at
            }
            for t in recent_txns
        ]

        return {
            "success": True,
            "data": {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                    "display_name": user.display_name,
                    "avatar_url": user.avatar_url,
                    "date_of_birth": user.date_of_birth,
                    "role": user.role,
                    "status": user.status,
                    "kyc_status": user.kyc_status,
                    "is_email_verified": user.is_email_verified,
                    "is_phone_verified": user.is_phone_verified,
                    "referral_code": user.referral_code,
                    "created_at": user.created_at,
                    "last_login_at": user.last_login_at
                },
                "statistics": {
                    "total_games_played": stats.total_games_played if stats else 0,
                    "total_games_won": stats.total_games_won if stats else 0,
                    "total_games_lost": stats.total_games_lost if stats else 0,
                    "total_winnings": stats.total_winnings / 100.0 if stats else 0.0,
                    "total_spent": stats.total_spent / 100.0 if stats else 0.0,
                    "current_level": stats.current_level if stats else 1,
                    "experience_points": stats.experience_points if stats else 0
                } if stats else None,
                "profile": {
                    "bio": profile.bio if profile else None,
                    "state": profile.state if profile else None,
                    "city": profile.city if profile else None,
                    "pincode": profile.pincode if profile else None
                } if profile else None,
                "wallets": wallets_data,
                "recent_transactions": transactions_data
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )


@router.put("/users/{user_id}/status", response_model=Dict[str, Any])
async def update_user_status(
    user_id: str,
    status_update: str,
    reason: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user status (active, suspended, banned)
    """
    await _check_admin_permissions(current_user)

    try:
        # Validate status
        valid_statuses = ["active", "suspended", "banned"]
        if status_update not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Get user
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent modifying superadmin status
        if user.is_superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify superadmin status"
            )

        # Update status
        old_status = user.status
        user.status = status_update

        await db.commit()
        await db.refresh(user)

        # Log the action (you can create an admin_actions table for this)
        # For now, we'll just return success

        return {
            "success": True,
            "data": {
                "message": f"User status updated from {old_status} to {status_update}",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "status": user.status
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )
