"""
Token system models for practice games and rewards
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from config.database import Base


class TokenWallet(Base):
    """User token wallet for practice games"""
    __tablename__ = "token_wallets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Balance
    balance = Column(Integer, default=0)  # Current token balance
    total_earned = Column(Integer, default=0)  # Lifetime earned
    total_spent = Column(Integer, default=0)  # Lifetime spent
    
    # Daily reward tracking
    last_daily_claim = Column(DateTime)
    daily_claim_streak = Column(Integer, default=0)
    
    # Ad watch tracking (max 5 per day)
    ads_watched_today = Column(Integer, default=0)
    last_ad_watch = Column(DateTime)
    ads_reset_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="token_wallet")
    transactions = relationship("TokenTransaction", back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TokenWallet user_id={self.user_id} balance={self.balance}>"
    
    def to_dict(self):
        """Convert token wallet to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "balance": self.balance,
            "total_earned": self.total_earned,
            "total_spent": self.total_spent,
            "daily_claim_streak": self.daily_claim_streak,
            "last_daily_claim": self.last_daily_claim.isoformat() if self.last_daily_claim else None,
            "ads_watched_today": self.ads_watched_today,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TokenTransaction(Base):
    """Token transaction history"""
    __tablename__ = "token_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("token_wallets.id"), nullable=False)
    
    # Transaction details
    amount = Column(Integer, nullable=False)  # Positive for earn, negative for spend
    transaction_type = Column(String(50), nullable=False)  # earn, spend
    
    # Source: daily_login, ad_watch, achievement, purchase, practice_game, bonus, refund
    source = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Related entities
    related_id = Column(UUID(as_uuid=True))  # Achievement ID, game session ID, etc.
    transaction_metadata = Column(JSON)  # Additional data
    
    # Balance after transaction
    balance_after = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallet = relationship("TokenWallet", back_populates="transactions")
    user = relationship("User", backref="token_transactions")
    
    def __repr__(self):
        return f"<TokenTransaction {self.source} amount={self.amount}>"
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "source": self.source,
            "description": self.description,
            "related_id": str(self.related_id) if self.related_id else None,
            "metadata": self.transaction_metadata,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TokenPackage(Base):
    """Token packages available for purchase with real money"""
    __tablename__ = "token_packages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Package details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    tokens = Column(Integer, nullable=False)  # Number of tokens
    price = Column(Integer, nullable=False)  # Price in paise
    bonus_tokens = Column(Integer, default=0)  # Extra tokens
    
    # Discount
    discount_percentage = Column(Integer, default=0)
    original_price = Column(Integer)
    
    # Metadata
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TokenPackage {self.name} - {self.tokens} tokens>"
    
    def to_dict(self):
        """Convert package to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "tokens": self.tokens,
            "price": self.price,
            "bonus_tokens": self.bonus_tokens,
            "total_tokens": self.tokens + self.bonus_tokens,
            "discount_percentage": self.discount_percentage,
            "original_price": self.original_price,
            "is_popular": self.is_popular,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
