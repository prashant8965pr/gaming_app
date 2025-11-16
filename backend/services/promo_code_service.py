"""
Promo Code Service
Handles promo code validation and application
"""

from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from models.promo_code import PromoCode, PromoCodeUsage, PromoCodeType, PromoCodeStatus
from models.user import User


class PromoCodeService:
    """Service for managing promo codes"""

    @staticmethod
    async def validate_promo_code(
        db: AsyncSession,
        code: str,
        user: User,
        transaction_amount: Optional[float] = None
    ) -> Tuple[bool, Optional[str], Optional[PromoCode]]:
        """
        Validate promo code

        Returns:
            (is_valid, error_message, promo_code)
        """
        # Get promo code
        result = await db.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        promo_code = result.scalar_one_or_none()

        if not promo_code:
            return False, "Invalid promo code", None

        # Check if active
        if promo_code.status != PromoCodeStatus.ACTIVE:
            return False, "Promo code is not active", None

        # Check validity period
        now = datetime.utcnow()
        if now < promo_code.valid_from:
            return False, "Promo code is not yet valid", None
        if now > promo_code.valid_until:
            return False, "Promo code has expired", None

        # Check total usage limit
        if promo_code.max_uses and promo_code.current_uses >= promo_code.max_uses:
            return False, "Promo code usage limit reached", None

        # Check per-user usage limit
        result = await db.execute(
            select(PromoCodeUsage).where(
                and_(
                    PromoCodeUsage.promo_code_id == promo_code.id,
                    PromoCodeUsage.user_id == user.id
                )
            )
        )
        user_usages = result.scalars().all()

        if len(user_usages) >= promo_code.max_uses_per_user:
            return False, f"You have already used this promo code {promo_code.max_uses_per_user} time(s)", None

        # Check if user is targeted (if code is not public)
        if not promo_code.is_public:
            if promo_code.target_user_ids:
                target_ids = promo_code.target_user_ids.split(',')
                if str(user.id) not in target_ids:
                    return False, "This promo code is not available for your account", None

        # Check minimum transaction amount
        if transaction_amount:
            if promo_code.min_transaction_amount and transaction_amount < promo_code.min_transaction_amount:
                return False, f"Minimum transaction amount is ₹{promo_code.min_transaction_amount}", None

        # All validations passed
        return True, None, promo_code

    @staticmethod
    def calculate_discount(
        promo_code: PromoCode,
        transaction_amount: float
    ) -> float:
        """
        Calculate discount amount based on promo code type

        Returns:
            Discount amount
        """
        if promo_code.type == PromoCodeType.PERCENTAGE:
            discount = (transaction_amount * promo_code.value) / 100

            # Apply max discount limit if set
            if promo_code.max_discount:
                discount = min(discount, promo_code.max_discount)

            return round(discount, 2)

        elif promo_code.type == PromoCodeType.FIXED:
            # Fixed amount discount
            return min(promo_code.value, transaction_amount)

        else:
            # Free entry or other types
            return 0.0

    @staticmethod
    async def apply_promo_code(
        db: AsyncSession,
        code: str,
        user: User,
        transaction_amount: float
    ) -> Tuple[bool, Optional[str], float]:
        """
        Apply promo code and record usage

        Returns:
            (success, error_message, discount_amount)
        """
        # Validate promo code
        is_valid, error_msg, promo_code = await PromoCodeService.validate_promo_code(
            db, code, user, transaction_amount
        )

        if not is_valid:
            return False, error_msg, 0.0

        # Calculate discount
        discount_amount = PromoCodeService.calculate_discount(promo_code, transaction_amount)

        # Record usage
        usage = PromoCodeUsage(
            promo_code_id=promo_code.id,
            user_id=user.id,
            discount_amount=discount_amount,
            transaction_amount=transaction_amount
        )
        db.add(usage)

        # Increment usage count
        promo_code.current_uses += 1

        await db.commit()

        return True, None, discount_amount

    @staticmethod
    async def get_user_promo_codes(
        db: AsyncSession,
        user: User
    ) -> list:
        """Get available promo codes for user"""
        now = datetime.utcnow()

        # Get public promo codes or codes targeted to user
        result = await db.execute(
            select(PromoCode).where(
                and_(
                    PromoCode.status == PromoCodeStatus.ACTIVE,
                    PromoCode.valid_from <= now,
                    PromoCode.valid_until >= now,
                    PromoCode.is_public == True
                )
            )
        )
        public_codes = result.scalars().all()

        # Filter out fully used codes
        available_codes = []
        for code in public_codes:
            if code.is_valid:
                # Check user hasn't exceeded per-user limit
                result = await db.execute(
                    select(PromoCodeUsage).where(
                        and_(
                            PromoCodeUsage.promo_code_id == code.id,
                            PromoCodeUsage.user_id == user.id
                        )
                    )
                )
                user_usages = len(result.scalars().all())

                if user_usages < code.max_uses_per_user:
                    available_codes.append(code)

        return available_codes

    @staticmethod
    async def get_promo_code_stats(
        db: AsyncSession,
        promo_code_id: str
    ) -> dict:
        """Get statistics for a promo code"""
        result = await db.execute(
            select(PromoCode).where(PromoCode.id == promo_code_id)
        )
        promo_code = result.scalar_one_or_none()

        if not promo_code:
            return {}

        # Get usage statistics
        result = await db.execute(
            select(PromoCodeUsage).where(PromoCodeUsage.promo_code_id == promo_code_id)
        )
        usages = result.scalars().all()

        total_discount_given = sum(usage.discount_amount for usage in usages)
        unique_users = len(set(usage.user_id for usage in usages))

        return {
            "code": promo_code.code,
            "total_uses": promo_code.current_uses,
            "unique_users": unique_users,
            "total_discount_given": total_discount_given,
            "remaining_uses": promo_code.remaining_uses,
            "is_active": promo_code.status == PromoCodeStatus.ACTIVE,
            "is_valid": promo_code.is_valid
        }
