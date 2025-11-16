"""
Wallet Models
SQLAlchemy models for wallet and transaction tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid


class Wallet(Base):
    """User wallet table - supports multiple wallet types"""
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Wallet type: cash, winnings, bonus
    wallet_type = Column(String(20), nullable=False)

    # Balance in smallest currency unit (paise for INR)
    balance = Column(Integer, default=0, nullable=False)

    # Status
    status = Column(String(20), default="active")  # active, frozen, suspended
    is_locked = Column(Boolean, default=False)  # Locked during processing

    # Limits (in paise)
    daily_withdrawal_limit = Column(Integer, nullable=True)
    max_balance_limit = Column(Integer, nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_wallets_user_id', 'user_id'),
        Index('idx_wallets_type', 'wallet_type'),
        Index('idx_wallets_user_type', 'user_id', 'wallet_type', unique=True),  # One wallet per type per user
    )


class Transaction(Base):
    """Transaction history for all wallet operations"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True)

    # Transaction details
    transaction_type = Column(String(30), nullable=False)
    # Types: deposit, withdrawal, game_entry, game_win, bonus_credit, referral_bonus,
    # tds_deduction, admin_credit, admin_debit, refund, transfer

    amount = Column(Integer, nullable=False)  # Amount in paise (can be negative for debits)

    # Balance tracking
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)

    # Status
    status = Column(String(20), default="pending", nullable=False)
    # pending, processing, completed, failed, cancelled, refunded

    # Payment gateway details (for deposits/withdrawals)
    payment_gateway = Column(String(30), nullable=True)  # razorpay, paytm, phonepe, etc.
    gateway_transaction_id = Column(String(100), nullable=True, index=True)
    gateway_order_id = Column(String(100), nullable=True, index=True)
    payment_method = Column(String(30), nullable=True)  # upi, card, netbanking, wallet

    # For game-related transactions
    game_id = Column(UUID(as_uuid=True), nullable=True)
    contest_id = Column(UUID(as_uuid=True), nullable=True)

    # For withdrawals
    withdrawal_request_id = Column(UUID(as_uuid=True), ForeignKey("withdrawal_requests.id", ondelete="SET NULL"), nullable=True)

    # Tax deductions (TDS)
    tds_amount = Column(Integer, default=0)  # TDS deducted
    tds_percentage = Column(Numeric(5, 2), nullable=True)  # TDS rate applied

    # Description and notes
    description = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Processing details
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # For admin actions
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_transactions_user_id', 'user_id'),
        Index('idx_transactions_wallet_id', 'wallet_id'),
        Index('idx_transactions_type', 'transaction_type'),
        Index('idx_transactions_status', 'status'),
        Index('idx_transactions_created_at', 'created_at'),
        Index('idx_transactions_gateway_id', 'gateway_transaction_id'),
    )


class WithdrawalRequest(Base):
    """Withdrawal requests from users"""
    __tablename__ = "withdrawal_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True)

    # Amount details (in paise)
    requested_amount = Column(Integer, nullable=False)
    tds_amount = Column(Integer, default=0)
    processing_fee = Column(Integer, default=0)
    final_amount = Column(Integer, nullable=False)  # Amount to be transferred

    # Status
    status = Column(String(20), default="pending", nullable=False)
    # pending, processing, approved, completed, rejected, cancelled, failed

    # Bank details (snapshot at time of request)
    account_holder_name = Column(String(200), nullable=False)
    account_number = Column(String(50), nullable=False)
    ifsc_code = Column(String(11), nullable=False)
    bank_name = Column(String(200), nullable=True)

    # Processing details
    payment_gateway = Column(String(30), nullable=True)  # razorpay, manual, etc.
    gateway_payout_id = Column(String(100), nullable=True)
    utr_number = Column(String(50), nullable=True)  # Unique Transaction Reference

    # Admin review
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Completion
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_withdrawals_user_id', 'user_id'),
        Index('idx_withdrawals_status', 'status'),
        Index('idx_withdrawals_created_at', 'created_at'),
        Index('idx_withdrawals_bank_account_id', 'bank_account_id'),
    )


class PaymentOrder(Base):
    """Payment orders for deposits (Razorpay/Paytm orders)"""
    __tablename__ = "payment_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Order details
    order_amount = Column(Integer, nullable=False)  # Amount in paise
    currency = Column(String(3), default="INR")

    # Payment gateway
    payment_gateway = Column(String(30), nullable=False)  # razorpay, paytm, phonepe
    gateway_order_id = Column(String(100), nullable=False, index=True)
    gateway_payment_id = Column(String(100), nullable=True, index=True)

    # Status
    status = Column(String(20), default="created", nullable=False)
    # created, attempted, paid, failed, cancelled, refunded

    # Payment details
    payment_method = Column(String(30), nullable=True)
    payment_card_network = Column(String(20), nullable=True)  # visa, mastercard, etc.
    payment_bank = Column(String(100), nullable=True)
    payment_wallet = Column(String(30), nullable=True)

    # Promo/Bonus
    promo_code = Column(String(50), nullable=True)
    bonus_amount = Column(Integer, default=0)  # Bonus credited

    # Timestamps
    paid_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_payment_orders_user_id', 'user_id'),
        Index('idx_payment_orders_status', 'status'),
        Index('idx_payment_orders_gateway_order_id', 'gateway_order_id', unique=True),
    )
