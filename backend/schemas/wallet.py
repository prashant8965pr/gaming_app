"""
Wallet Schemas
Pydantic models for wallet and transaction requests/responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Wallet Schemas
# ============================================================================

class WalletResponse(BaseModel):
    """Response schema for wallet"""
    id: str
    wallet_type: str
    balance: float  # In rupees (converted from paise)
    status: str
    is_locked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletBalanceResponse(BaseModel):
    """Response schema for all wallet balances"""
    cash_wallet: WalletResponse
    winnings_wallet: WalletResponse
    bonus_wallet: WalletResponse
    total_balance: float  # Sum of all wallets in rupees
    withdrawable_balance: float  # Cash + Winnings only


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionResponse(BaseModel):
    """Response schema for transaction"""
    id: str
    transaction_type: str
    amount: float  # In rupees
    balance_before: float
    balance_after: float
    status: str
    description: Optional[str]
    payment_gateway: Optional[str]
    payment_method: Optional[str]
    gateway_transaction_id: Optional[str]
    tds_amount: float = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionHistoryRequest(BaseModel):
    """Request schema for transaction history with filters"""
    wallet_type: Optional[str] = Field(None, example="cash")
    transaction_type: Optional[str] = Field(None, example="deposit")
    status: Optional[str] = Field(None, example="completed")
    start_date: Optional[datetime] = Field(None, example="2025-01-01T00:00:00Z")
    end_date: Optional[datetime] = Field(None, example="2025-12-31T23:59:59Z")
    limit: int = Field(default=50, ge=1, le=100, example=50)
    offset: int = Field(default=0, ge=0, example=0)

    @validator('wallet_type')
    def validate_wallet_type(cls, v):
        if v:
            allowed_types = ['cash', 'winnings', 'bonus']
            if v.lower() not in allowed_types:
                raise ValueError(f'Wallet type must be one of: {", ".join(allowed_types)}')
            return v.lower()
        return v

    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        if v:
            allowed_types = [
                'deposit', 'withdrawal', 'game_entry', 'game_win',
                'bonus_credit', 'referral_bonus', 'tds_deduction',
                'admin_credit', 'admin_debit', 'refund', 'transfer'
            ]
            if v.lower() not in allowed_types:
                raise ValueError(f'Invalid transaction type')
            return v.lower()
        return v


class TransactionHistoryResponse(BaseModel):
    """Response schema for transaction history"""
    transactions: List[TransactionResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool


# ============================================================================
# Add Money (Deposit) Schemas
# ============================================================================

class CreateDepositOrderRequest(BaseModel):
    """Request schema for creating deposit order"""
    amount: float = Field(..., ge=10, le=100000, example=100.0)
    payment_gateway: str = Field(default="razorpay", example="razorpay")
    promo_code: Optional[str] = Field(None, max_length=50, example="WELCOME100")

    @validator('amount')
    def validate_amount(cls, v):
        """Ensure amount is in valid range and has max 2 decimal places"""
        if v < 10:
            raise ValueError('Minimum deposit amount is ₹10')
        if v > 100000:
            raise ValueError('Maximum deposit amount is ₹1,00,000')

        # Check decimal places
        decimal_places = Decimal(str(v)).as_tuple().exponent
        if decimal_places < -2:
            raise ValueError('Amount can have maximum 2 decimal places')

        return round(v, 2)

    @validator('payment_gateway')
    def validate_payment_gateway(cls, v):
        allowed_gateways = ['razorpay', 'paytm', 'phonepe']
        if v.lower() not in allowed_gateways:
            raise ValueError(f'Payment gateway must be one of: {", ".join(allowed_gateways)}')
        return v.lower()


class DepositOrderResponse(BaseModel):
    """Response schema for deposit order"""
    order_id: str
    gateway_order_id: str
    amount: float
    currency: str
    payment_gateway: str
    bonus_amount: float = 0
    total_amount: float  # amount + bonus
    callback_url: Optional[str]
    gateway_config: Dict[str, Any]  # Gateway-specific configuration


class VerifyDepositRequest(BaseModel):
    """Request schema for verifying deposit payment"""
    order_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    gateway_payment_id: str = Field(..., example="pay_MqAbCdEfGhIjKl")
    gateway_signature: Optional[str] = Field(None, example="abc123def456...")


class VerifyDepositResponse(BaseModel):
    """Response schema for deposit verification"""
    success: bool
    message: str
    transaction: Optional[TransactionResponse]
    wallet_balance: Optional[WalletBalanceResponse]


# ============================================================================
# Withdrawal Schemas
# ============================================================================

class CreateWithdrawalRequest(BaseModel):
    """Request schema for withdrawal"""
    amount: float = Field(..., ge=100, le=100000, example=500.0)
    bank_account_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

    @validator('amount')
    def validate_amount(cls, v):
        """Ensure amount is in valid range"""
        if v < 100:
            raise ValueError('Minimum withdrawal amount is ₹100')
        if v > 100000:
            raise ValueError('Maximum withdrawal amount is ₹1,00,000 per transaction')

        # Check decimal places
        decimal_places = Decimal(str(v)).as_tuple().exponent
        if decimal_places < -2:
            raise ValueError('Amount can have maximum 2 decimal places')

        return round(v, 2)


class WithdrawalRequestResponse(BaseModel):
    """Response schema for withdrawal request"""
    id: str
    requested_amount: float
    tds_amount: float
    processing_fee: float
    final_amount: float
    status: str
    account_holder_name: str
    account_number: str  # Masked
    ifsc_code: str
    bank_name: Optional[str]
    utr_number: Optional[str]
    rejection_reason: Optional[str]
    requested_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class WithdrawalHistoryResponse(BaseModel):
    """Response schema for withdrawal history"""
    withdrawals: List[WithdrawalRequestResponse]
    total_count: int
    pending_count: int
    total_withdrawn: float  # Total amount withdrawn (all time)


class CancelWithdrawalRequest(BaseModel):
    """Request schema for canceling withdrawal"""
    withdrawal_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")


# ============================================================================
# Admin Withdrawal Review Schemas
# ============================================================================

class ReviewWithdrawalRequest(BaseModel):
    """Admin request schema for reviewing withdrawal"""
    withdrawal_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    action: str = Field(..., example="approve")  # approve, reject
    rejection_reason: Optional[str] = Field(None, example="Insufficient KYC")
    admin_notes: Optional[str] = Field(None, example="Verified bank account")
    utr_number: Optional[str] = Field(None, max_length=50, example="UTR1234567890")

    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['approve', 'reject', 'complete']
        if v.lower() not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v.lower()


class ProcessWithdrawalPayoutRequest(BaseModel):
    """Admin request schema for processing withdrawal payout"""
    withdrawal_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    utr_number: str = Field(..., max_length=50, example="UTR1234567890")
    gateway_payout_id: Optional[str] = Field(None, example="payout_MqAbCdEfGhIjKl")
    admin_notes: Optional[str] = Field(None, example="Transferred via NEFT")


# ============================================================================
# Promo Code Schemas
# ============================================================================

class ValidatePromoCodeRequest(BaseModel):
    """Request schema for validating promo code"""
    promo_code: str = Field(..., min_length=1, max_length=50, example="WELCOME100")
    amount: float = Field(..., ge=10, example=100.0)


class PromoCodeResponse(BaseModel):
    """Response schema for promo code validation"""
    valid: bool
    promo_code: str
    discount_type: Optional[str]  # percentage, fixed
    discount_value: Optional[float]
    bonus_amount: Optional[float]
    max_discount: Optional[float]
    message: str


# ============================================================================
# Admin Transaction Schemas
# ============================================================================

class AdminAdjustBalanceRequest(BaseModel):
    """Admin request schema for manual balance adjustment"""
    user_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    wallet_type: str = Field(..., example="cash")
    amount: float = Field(..., example=100.0)  # Positive for credit, negative for debit
    reason: str = Field(..., min_length=1, max_length=500, example="Compensation for technical issue")
    admin_notes: Optional[str] = Field(None, example="Approved by manager")

    @validator('wallet_type')
    def validate_wallet_type(cls, v):
        allowed_types = ['cash', 'winnings', 'bonus']
        if v.lower() not in allowed_types:
            raise ValueError(f'Wallet type must be one of: {", ".join(allowed_types)}')
        return v.lower()

    @validator('amount')
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        if abs(v) > 100000:
            raise ValueError('Amount cannot exceed ₹1,00,000')
        return round(v, 2)


class AdminTransactionResponse(BaseModel):
    """Response schema for admin transaction"""
    message: str
    transaction: TransactionResponse
    wallet_balance: WalletBalanceResponse
