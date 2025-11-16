"""
Two-Factor Authentication Models
TOTP-based 2FA for enhanced security
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from config.database import Base


class TwoFactorAuth(Base):
    """Two-Factor Authentication settings for users"""

    __tablename__ = "two_factor_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # TOTP Settings
    secret = Column(String(32), nullable=False)  # Base32 encoded secret
    is_enabled = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Backup codes (encrypted, comma-separated)
    backup_codes = Column(Text, nullable=True)  # Encrypted backup codes
    backup_codes_used = Column(Integer, default=0, nullable=False)

    # Metadata
    enabled_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="two_factor_auth")

    def __repr__(self):
        return f"<TwoFactorAuth(user_id={self.user_id}, enabled={self.is_enabled})>"


class TwoFactorBackupCode(Base):
    """Backup codes for 2FA recovery"""

    __tablename__ = "two_factor_backup_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Code details
    code_hash = Column(String(255), nullable=False)  # Hashed backup code
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="backup_codes")

    def __repr__(self):
        return f"<TwoFactorBackupCode(user_id={self.user_id}, used={self.is_used})>"
