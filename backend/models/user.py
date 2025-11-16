"""
User Models
SQLAlchemy models for user-related tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from config.database import Base
import uuid


class User(Base):
    """Main user table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL if only social/OTP login
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(String(20), default="user", nullable=False)  # user, admin, superadmin
    status = Column(String(20), default="active", nullable=False)  # active, suspended, banned
    kyc_status = Column(String(20), default="pending", nullable=False)  # pending, verified, rejected
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=True)
    referral_code = Column(String(10), unique=True, nullable=False, index=True)
    referred_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_role', 'role'),
        Index('idx_status', 'status'),
        Index('idx_kyc_status', 'kyc_status'),
    )

    # Relationships
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False, cascade="all, delete-orphan")
    backup_codes = relationship("TwoFactorBackupCode", back_populates="user", cascade="all, delete-orphan")
    promo_code_usages = relationship("PromoCodeUsage", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in ['admin', 'superadmin']

    @property
    def is_superadmin(self) -> bool:
        """Check if user is a superadmin"""
        return self.role == 'superadmin'


class UserSession(Base):
    """User session table for JWT tokens"""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_token = Column(String(500), nullable=False, index=True)
    refresh_token = Column(String(500), nullable=False, index=True)
    device_id = Column(String(255), nullable=True)
    device_name = Column(String(100), nullable=True)
    device_os = Column(String(50), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_expires_at', 'expires_at'),
    )


class OTPAttempt(Base):
    """OTP attempts table"""
    __tablename__ = "otp_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(15), nullable=False)
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False)  # login, registration, verification
    is_verified = Column(Boolean, default=False)
    attempts_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_otp_phone_purpose', 'phone', 'purpose'),
        Index('idx_otp_expires_at', 'expires_at'),
    )


class SocialAuthProvider(Base):
    """Social authentication providers (Google, Facebook, Apple)"""
    __tablename__ = "social_auth_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False)  # google, facebook, apple
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    access_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Unique constraint
    __table_args__ = (
        Index('idx_provider_user', 'provider', 'provider_user_id', unique=True),
        Index('idx_social_auth_user_id', 'user_id'),
    )


class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bio = Column(String(500), nullable=True)
    state = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    preferred_language = Column(String(10), default="en")
    notification_preferences = Column(String(1000), default='{"push": true, "email": true, "sms": true}')
    privacy_settings = Column(String(1000), default='{"show_profile": true, "show_stats": true}')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserStatistics(Base):
    """User gaming statistics"""
    __tablename__ = "user_statistics"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_games_played = Column(Integer, default=0)
    total_games_won = Column(Integer, default=0)
    total_games_lost = Column(Integer, default=0)
    total_winnings = Column(Integer, default=0)  # Store in smallest currency unit (paise)
    total_spent = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
