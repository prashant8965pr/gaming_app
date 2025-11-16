"""
Wallet API Endpoints
Handles wallet management, deposits, withdrawals, and transactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid
import json

from config.database import get_db, get_redis
from config.settings import settings
from core.security import get_current_user
from core.exceptions import GamePlatformException
from models.user import User
from models.wallet import Wallet, Transaction, WithdrawalRequest, PaymentOrder
from models.kyc import BankAccount
from schemas.wallet import (
    WalletBalanceResponse,
    WalletResponse,
    TransactionResponse,
    TransactionHistoryRequest,
    TransactionHistoryResponse,
    CreateDepositOrderRequest,
    DepositOrderResponse,
    VerifyDepositRequest,
    VerifyDepositResponse,
    CreateWithdrawalRequest,
    WithdrawalRequestResponse,
    WithdrawalHistoryResponse,
    CancelWithdrawalRequest
)

router = APIRouter()


# ============================================================================
# Wallet Balance Endpoints
# ============================================================================

@router.get("/balance", response_model=Dict[str, Any])
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's wallet balances (Cash, Winnings, Bonus)
    """
    try:
        # Get or create wallets
        wallets = await _get_or_create_wallets(db, current_user.id)

        cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)
        winnings_wallet = next((w for w in wallets if w.wallet_type == "winnings"), None)
        bonus_wallet = next((w for w in wallets if w.wallet_type == "bonus"), None)

        # Convert paise to rupees
        cash_balance = cash_wallet.balance / 100.0 if cash_wallet else 0.0
        winnings_balance = winnings_wallet.balance / 100.0 if winnings_wallet else 0.0
        bonus_balance = bonus_wallet.balance / 100.0 if bonus_wallet else 0.0

        total_balance = cash_balance + winnings_balance + bonus_balance
        withdrawable_balance = cash_balance + winnings_balance

        return {
            "success": True,
            "data": {
                "cash_wallet": WalletResponse(
                    id=str(cash_wallet.id),
                    wallet_type="cash",
                    balance=cash_balance,
                    status=cash_wallet.status,
                    is_locked=cash_wallet.is_locked,
                    created_at=cash_wallet.created_at,
                    updated_at=cash_wallet.updated_at
                ) if cash_wallet else None,
                "winnings_wallet": WalletResponse(
                    id=str(winnings_wallet.id),
                    wallet_type="winnings",
                    balance=winnings_balance,
                    status=winnings_wallet.status,
                    is_locked=winnings_wallet.is_locked,
                    created_at=winnings_wallet.created_at,
                    updated_at=winnings_wallet.updated_at
                ) if winnings_wallet else None,
                "bonus_wallet": WalletResponse(
                    id=str(bonus_wallet.id),
                    wallet_type="bonus",
                    balance=bonus_balance,
                    status=bonus_wallet.status,
                    is_locked=bonus_wallet.is_locked,
                    created_at=bonus_wallet.created_at,
                    updated_at=bonus_wallet.updated_at
                ) if bonus_wallet else None,
                "total_balance": total_balance,
                "withdrawable_balance": withdrawable_balance
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get wallet balance: {str(e)}"
        )


# ============================================================================
# Transaction History Endpoints
# ============================================================================

@router.post("/transactions/history", response_model=Dict[str, Any])
async def get_transaction_history(
    filters: TransactionHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction history with filters
    """
    try:
        # Build query
        query = select(Transaction).where(Transaction.user_id == current_user.id)

        # Apply filters
        if filters.wallet_type:
            wallet_result = await db.execute(
                select(Wallet).where(
                    and_(
                        Wallet.user_id == current_user.id,
                        Wallet.wallet_type == filters.wallet_type
                    )
                )
            )
            wallet = wallet_result.scalar_one_or_none()
            if wallet:
                query = query.where(Transaction.wallet_id == wallet.id)

        if filters.transaction_type:
            query = query.where(Transaction.transaction_type == filters.transaction_type)

        if filters.status:
            query = query.where(Transaction.status == filters.status)

        if filters.start_date:
            query = query.where(Transaction.created_at >= filters.start_date)

        if filters.end_date:
            query = query.where(Transaction.created_at <= filters.end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar()

        # Apply pagination
        query = query.order_by(Transaction.created_at.desc())
        query = query.offset(filters.offset).limit(filters.limit)

        # Execute query
        result = await db.execute(query)
        transactions = result.scalars().all()

        # Format response
        transactions_response = []
        for txn in transactions:
            transactions_response.append(TransactionResponse(
                id=str(txn.id),
                transaction_type=txn.transaction_type,
                amount=txn.amount / 100.0,  # Convert to rupees
                balance_before=txn.balance_before / 100.0,
                balance_after=txn.balance_after / 100.0,
                status=txn.status,
                description=txn.description,
                payment_gateway=txn.payment_gateway,
                payment_method=txn.payment_method,
                gateway_transaction_id=txn.gateway_transaction_id,
                tds_amount=txn.tds_amount / 100.0 if txn.tds_amount else 0.0,
                created_at=txn.created_at
            ))

        has_more = (filters.offset + filters.limit) < total_count

        return {
            "success": True,
            "data": {
                "transactions": transactions_response,
                "total_count": total_count,
                "limit": filters.limit,
                "offset": filters.offset,
                "has_more": has_more
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction history: {str(e)}"
        )


# ============================================================================
# Deposit (Add Money) Endpoints
# ============================================================================

@router.post("/deposit/create-order", response_model=Dict[str, Any])
async def create_deposit_order(
    request_data: CreateDepositOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a deposit order with payment gateway
    """
    try:
        # Get or create cash wallet
        wallets = await _get_or_create_wallets(db, current_user.id)
        cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)

        # Convert amount to paise
        amount_paise = int(request_data.amount * 100)

        # Calculate bonus (if promo code provided)
        bonus_amount = 0
        if request_data.promo_code:
            bonus_amount = await _calculate_promo_bonus(
                request_data.promo_code,
                request_data.amount
            )

        # Create payment order in database
        payment_order = PaymentOrder(
            id=uuid.uuid4(),
            user_id=current_user.id,
            order_amount=amount_paise,
            currency="INR",
            payment_gateway=request_data.payment_gateway,
            gateway_order_id="",  # Will be set after gateway creation
            status="created",
            promo_code=request_data.promo_code,
            bonus_amount=int(bonus_amount * 100) if bonus_amount else 0
        )

        db.add(payment_order)
        await db.flush()

        # Create order with payment gateway
        gateway_response = await _create_payment_gateway_order(
            payment_order,
            request_data.payment_gateway,
            request_data.amount
        )

        # Update payment order with gateway details
        payment_order.gateway_order_id = gateway_response['order_id']

        await db.commit()
        await db.refresh(payment_order)

        return {
            "success": True,
            "data": {
                "order_id": str(payment_order.id),
                "gateway_order_id": gateway_response['order_id'],
                "amount": request_data.amount,
                "currency": "INR",
                "payment_gateway": request_data.payment_gateway,
                "bonus_amount": bonus_amount,
                "total_amount": request_data.amount + bonus_amount,
                "gateway_config": gateway_response.get('config', {})
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deposit order: {str(e)}"
        )


@router.post("/deposit/verify", response_model=Dict[str, Any])
async def verify_deposit_payment(
    request_data: VerifyDepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify deposit payment from payment gateway callback
    """
    try:
        # Get payment order
        result = await db.execute(
            select(PaymentOrder).where(PaymentOrder.id == uuid.UUID(request_data.order_id))
        )
        payment_order = result.scalar_one_or_none()

        if not payment_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order not found"
            )

        # Verify ownership
        if payment_order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Verify payment with gateway
        is_valid = await _verify_payment_with_gateway(
            payment_order,
            request_data.gateway_payment_id,
            request_data.gateway_signature
        )

        if not is_valid:
            payment_order.status = "failed"
            payment_order.failed_at = datetime.utcnow()
            await db.commit()

            return {
                "success": False,
                "data": {
                    "message": "Payment verification failed"
                }
            }

        # Update payment order
        payment_order.gateway_payment_id = request_data.gateway_payment_id
        payment_order.status = "paid"
        payment_order.paid_at = datetime.utcnow()

        # Get cash wallet
        wallets = await _get_or_create_wallets(db, current_user.id)
        cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)

        # Create deposit transaction
        deposit_txn = await _create_transaction(
            db=db,
            user_id=current_user.id,
            wallet=cash_wallet,
            amount=payment_order.order_amount,
            transaction_type="deposit",
            description=f"Deposit via {payment_order.payment_gateway}",
            gateway_order_id=payment_order.gateway_order_id,
            gateway_transaction_id=request_data.gateway_payment_id,
            payment_gateway=payment_order.payment_gateway
        )

        # Credit bonus if applicable
        if payment_order.bonus_amount > 0:
            bonus_wallet = next((w for w in wallets if w.wallet_type == "bonus"), None)
            await _create_transaction(
                db=db,
                user_id=current_user.id,
                wallet=bonus_wallet,
                amount=payment_order.bonus_amount,
                transaction_type="bonus_credit",
                description=f"Bonus for deposit (Promo: {payment_order.promo_code})"
            )

        await db.commit()

        # Get updated balances
        wallets_updated = await _get_or_create_wallets(db, current_user.id)
        balance_response = await _format_wallet_balance_response(wallets_updated)

        return {
            "success": True,
            "data": {
                "message": "Deposit successful",
                "transaction": TransactionResponse(
                    id=str(deposit_txn.id),
                    transaction_type=deposit_txn.transaction_type,
                    amount=deposit_txn.amount / 100.0,
                    balance_before=deposit_txn.balance_before / 100.0,
                    balance_after=deposit_txn.balance_after / 100.0,
                    status=deposit_txn.status,
                    description=deposit_txn.description,
                    payment_gateway=deposit_txn.payment_gateway,
                    payment_method=deposit_txn.payment_method,
                    gateway_transaction_id=deposit_txn.gateway_transaction_id,
                    tds_amount=0.0,
                    created_at=deposit_txn.created_at
                ),
                "wallet_balance": balance_response
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deposit verification failed: {str(e)}"
        )


# ============================================================================
# Withdrawal Endpoints
# ============================================================================

@router.post("/withdrawal/request", response_model=Dict[str, Any])
async def create_withdrawal_request(
    request_data: CreateWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a withdrawal request
    """
    try:
        # Check KYC status
        if settings.KYC_REQUIRED_FOR_WITHDRAWAL and current_user.kyc_status != "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="KYC verification required for withdrawal"
            )

        # Get bank account
        bank_result = await db.execute(
            select(BankAccount).where(BankAccount.id == uuid.UUID(request_data.bank_account_id))
        )
        bank_account = bank_result.scalar_one_or_none()

        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        # Verify ownership
        if bank_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Check if bank account is verified
        if not bank_account.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank account must be verified before withdrawal"
            )

        # Get withdrawable wallets (cash + winnings)
        wallets = await _get_or_create_wallets(db, current_user.id)
        cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)
        winnings_wallet = next((w for w in wallets if w.wallet_type == "winnings"), None)

        total_balance = cash_wallet.balance + winnings_wallet.balance
        requested_amount_paise = int(request_data.amount * 100)

        if requested_amount_paise > total_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        # Calculate TDS (on winnings only, if above threshold)
        tds_amount = 0
        if winnings_wallet.balance > 0:
            winnings_rupees = winnings_wallet.balance / 100.0
            if winnings_rupees > settings.TDS_THRESHOLD:
                tds_amount = int((winnings_wallet.balance * settings.TDS_PERCENTAGE / 100))

        # Calculate final amount
        processing_fee = int(settings.WITHDRAWAL_PROCESSING_FEE * 100)
        final_amount = requested_amount_paise - tds_amount - processing_fee

        if final_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Withdrawal amount too low after deductions"
            )

        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            id=uuid.uuid4(),
            user_id=current_user.id,
            bank_account_id=bank_account.id,
            requested_amount=requested_amount_paise,
            tds_amount=tds_amount,
            processing_fee=processing_fee,
            final_amount=final_amount,
            account_holder_name=bank_account.account_holder_name,
            account_number=bank_account.account_number,
            ifsc_code=bank_account.ifsc_code,
            bank_name=bank_account.bank_name,
            status="pending"
        )

        db.add(withdrawal)

        # Deduct from wallets
        await _deduct_from_wallets(
            db=db,
            user_id=current_user.id,
            wallets=[cash_wallet, winnings_wallet],
            total_amount=requested_amount_paise,
            withdrawal_id=withdrawal.id,
            tds_amount=tds_amount
        )

        await db.commit()
        await db.refresh(withdrawal)

        return {
            "success": True,
            "data": {
                "message": "Withdrawal request submitted successfully",
                "withdrawal": _format_withdrawal_response(withdrawal)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Withdrawal request failed: {str(e)}"
        )


@router.get("/withdrawal/history", response_model=Dict[str, Any])
async def get_withdrawal_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get withdrawal history
    """
    try:
        result = await db.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.user_id == current_user.id)
            .order_by(WithdrawalRequest.created_at.desc())
        )
        withdrawals = result.scalars().all()

        withdrawals_response = [_format_withdrawal_response(w) for w in withdrawals]

        # Calculate stats
        total_count = len(withdrawals)
        pending_count = sum(1 for w in withdrawals if w.status == "pending")
        total_withdrawn = sum(
            w.final_amount / 100.0 for w in withdrawals if w.status == "completed"
        )

        return {
            "success": True,
            "data": {
                "withdrawals": withdrawals_response,
                "total_count": total_count,
                "pending_count": pending_count,
                "total_withdrawn": total_withdrawn
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get withdrawal history: {str(e)}"
        )


@router.post("/withdrawal/cancel", response_model=Dict[str, Any])
async def cancel_withdrawal(
    request_data: CancelWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending withdrawal request
    """
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

        # Verify ownership
        if withdrawal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Check if can be cancelled
        if withdrawal.status not in ["pending", "processing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending withdrawals can be cancelled"
            )

        # Refund amount to wallet
        wallets = await _get_or_create_wallets(db, current_user.id)
        cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)

        await _create_transaction(
            db=db,
            user_id=current_user.id,
            wallet=cash_wallet,
            amount=withdrawal.requested_amount,
            transaction_type="refund",
            description=f"Withdrawal cancelled (ID: {str(withdrawal.id)[:8]})"
        )

        # Update withdrawal status
        withdrawal.status = "cancelled"

        await db.commit()

        return {
            "success": True,
            "data": {
                "message": "Withdrawal cancelled successfully"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cancellation failed: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_or_create_wallets(db: AsyncSession, user_id: uuid.UUID) -> List[Wallet]:
    """Get or create all wallet types for user"""
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == user_id)
    )
    existing_wallets = result.scalars().all()

    wallet_types = ["cash", "winnings", "bonus"]
    existing_types = {w.wallet_type for w in existing_wallets}

    # Create missing wallets
    for wallet_type in wallet_types:
        if wallet_type not in existing_types:
            new_wallet = Wallet(
                id=uuid.uuid4(),
                user_id=user_id,
                wallet_type=wallet_type,
                balance=0,
                status="active"
            )
            db.add(new_wallet)
            existing_wallets.append(new_wallet)

    await db.flush()
    return existing_wallets


async def _create_transaction(
    db: AsyncSession,
    user_id: uuid.UUID,
    wallet: Wallet,
    amount: int,
    transaction_type: str,
    description: str = None,
    gateway_order_id: str = None,
    gateway_transaction_id: str = None,
    payment_gateway: str = None,
    withdrawal_id: uuid.UUID = None,
    tds_amount: int = 0
) -> Transaction:
    """Create a transaction and update wallet balance"""
    balance_before = wallet.balance
    balance_after = balance_before + amount

    transaction = Transaction(
        id=uuid.uuid4(),
        user_id=user_id,
        wallet_id=wallet.id,
        transaction_type=transaction_type,
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        status="completed",
        payment_gateway=payment_gateway,
        gateway_order_id=gateway_order_id,
        gateway_transaction_id=gateway_transaction_id,
        withdrawal_request_id=withdrawal_id,
        tds_amount=tds_amount,
        description=description,
        processed_at=datetime.utcnow()
    )

    db.add(transaction)

    # Update wallet balance
    wallet.balance = balance_after

    await db.flush()
    return transaction


async def _create_payment_gateway_order(
    payment_order: PaymentOrder,
    gateway: str,
    amount: float
) -> Dict[str, Any]:
    """Create order with payment gateway (Razorpay/Paytm/etc)"""
    # In production, integrate with actual payment gateway
    # For now, return mock response

    if gateway == "razorpay":
        # In production: import razorpay and create order
        order_id = f"order_{uuid.uuid4().hex[:16]}"
        return {
            "order_id": order_id,
            "config": {
                "key": settings.RAZORPAY_KEY_ID,
                "amount": int(amount * 100),
                "currency": "INR",
                "name": "Gaming Platform",
                "description": "Add Money to Wallet"
            }
        }

    return {"order_id": f"order_{uuid.uuid4().hex[:16]}"}


async def _verify_payment_with_gateway(
    payment_order: PaymentOrder,
    payment_id: str,
    signature: str = None
) -> bool:
    """Verify payment with payment gateway"""
    # In production, verify signature with payment gateway
    # For development, auto-approve
    return True


async def _calculate_promo_bonus(promo_code: str, amount: float) -> float:
    """Calculate bonus amount for promo code"""
    # In production, fetch promo code from database and calculate
    # For now, return 0
    return 0.0


async def _deduct_from_wallets(
    db: AsyncSession,
    user_id: uuid.UUID,
    wallets: List[Wallet],
    total_amount: int,
    withdrawal_id: uuid.UUID,
    tds_amount: int = 0
):
    """Deduct amount from wallets (cash first, then winnings)"""
    remaining = total_amount

    for wallet in wallets:
        if remaining <= 0:
            break

        if wallet.balance > 0:
            deduct_amount = min(wallet.balance, remaining)

            await _create_transaction(
                db=db,
                user_id=user_id,
                wallet=wallet,
                amount=-deduct_amount,
                transaction_type="withdrawal",
                description=f"Withdrawal request",
                withdrawal_id=withdrawal_id
            )

            remaining -= deduct_amount

    # Create TDS transaction if applicable
    if tds_amount > 0:
        winnings_wallet = next((w for w in wallets if w.wallet_type == "winnings"), None)
        if winnings_wallet:
            await _create_transaction(
                db=db,
                user_id=user_id,
                wallet=winnings_wallet,
                amount=-tds_amount,
                transaction_type="tds_deduction",
                description="TDS deduction on winnings",
                tds_amount=tds_amount
            )


def _format_withdrawal_response(withdrawal: WithdrawalRequest) -> WithdrawalRequestResponse:
    """Format withdrawal for response"""
    return WithdrawalRequestResponse(
        id=str(withdrawal.id),
        requested_amount=withdrawal.requested_amount / 100.0,
        tds_amount=withdrawal.tds_amount / 100.0,
        processing_fee=withdrawal.processing_fee / 100.0,
        final_amount=withdrawal.final_amount / 100.0,
        status=withdrawal.status,
        account_holder_name=withdrawal.account_holder_name,
        account_number=f"{'X' * (len(withdrawal.account_number) - 4)}{withdrawal.account_number[-4:]}",
        ifsc_code=withdrawal.ifsc_code,
        bank_name=withdrawal.bank_name,
        utr_number=withdrawal.utr_number,
        rejection_reason=withdrawal.rejection_reason,
        requested_at=withdrawal.requested_at,
        completed_at=withdrawal.completed_at
    )


async def _format_wallet_balance_response(wallets: List[Wallet]) -> Dict[str, Any]:
    """Format wallet balance response"""
    cash_wallet = next((w for w in wallets if w.wallet_type == "cash"), None)
    winnings_wallet = next((w for w in wallets if w.wallet_type == "winnings"), None)
    bonus_wallet = next((w for w in wallets if w.wallet_type == "bonus"), None)

    cash_balance = cash_wallet.balance / 100.0 if cash_wallet else 0.0
    winnings_balance = winnings_wallet.balance / 100.0 if winnings_wallet else 0.0
    bonus_balance = bonus_wallet.balance / 100.0 if bonus_wallet else 0.0

    return {
        "cash_balance": cash_balance,
        "winnings_balance": winnings_balance,
        "bonus_balance": bonus_balance,
        "total_balance": cash_balance + winnings_balance + bonus_balance,
        "withdrawable_balance": cash_balance + winnings_balance
    }
