"""
Promo Code Models
For marketing campaigns and user discounts
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from config.database import Base


class PromoCodeType(str, enum.Enum):
    """Promo code types"""
    PERCENTAGE = "percentage"  # e.g., 20% bonus
    FIXED = "fixed"  # e.g., ₹100 bonus
    FREE_ENTRY = "free_entry"  # Free game entry


class PromoCodeStatus(str, enum.Enum):
    """Promo code status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class PromoCode(Base):
    """Promo codes for marketing campaigns"""

    __tablename__ = "promo_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Code details
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)

    # Type and value
    type = Column(SQLEnum(PromoCodeType), nullable=False)
    value = Column(Float, nullable=False)  # Percentage or fixed amount
    max_discount = Column(Float, nullable=True)  # Max discount for percentage type

    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Total uses allowed (None = unlimited)
    max_uses_per_user = Column(Integer, default=1, nullable=False)
    current_uses = Column(Integer, default=0, nullable=False)

    # Minimum requirements
    min_deposit_amount = Column(Float, nullable=True)  # Minimum deposit to use code
    min_transaction_amount = Column(Float, nullable=True)

    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(PromoCodeStatus), default=PromoCodeStatus.ACTIVE, nullable=False)

    # Target audience (optional)
    is_public = Column(Boolean, default=True, nullable=False)  # Public or invite-only
    target_user_ids = Column(String, nullable=True)  # Comma-separated user IDs (for targeted promos)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    usages = relationship("PromoCodeUsage", back_populates="promo_code", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PromoCode(code={self.code}, type={self.type}, value={self.value})>"

    @property
    def is_valid(self) -> bool:
        """Check if promo code is currently valid"""
        now = datetime.utcnow()
        return (
            self.status == PromoCodeStatus.ACTIVE and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )

    @property
    def remaining_uses(self) -> int:
        """Get remaining uses"""
        if self.max_uses is None:
            return float('inf')
        return max(0, self.max_uses - self.current_uses)


class PromoCodeUsage(Base):
    """Track promo code usage by users"""

    __tablename__ = "promo_code_usages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Usage details
    discount_amount = Column(Float, nullable=False)  # Actual discount received
    transaction_amount = Column(Float, nullable=False)  # Original transaction amount

    # Metadata
    used_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    promo_code = relationship("PromoCode", back_populates="usages")
    user = relationship("User", back_populates="promo_code_usages")

    def __repr__(self):
        return f"<PromoCodeUsage(code_id={self.promo_code_id}, user_id={self.user_id})>"
