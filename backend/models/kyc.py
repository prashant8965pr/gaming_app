"""
KYC Models
SQLAlchemy models for KYC and bank account tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid


class KYCDocument(Base):
    """KYC document verification table"""
    __tablename__ = "kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Document type: aadhaar, pan, voter_id, driving_license, passport
    document_type = Column(String(30), nullable=False)

    # Document details
    document_number = Column(String(50), nullable=False)  # Masked for security
    document_front_url = Column(String(500), nullable=True)  # Front image URL
    document_back_url = Column(String(500), nullable=True)  # Back image URL (if applicable)
    selfie_url = Column(String(500), nullable=True)  # Selfie for verification

    # Personal details from document
    full_name = Column(String(200), nullable=True)
    father_name = Column(String(200), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Verification status
    status = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected, under_review
    verification_method = Column(String(30), nullable=True)  # manual, auto, api

    # Admin review
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)  # Additional data from verification API
    ip_address = Column(String(50), nullable=True)

    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_kyc_user_id', 'user_id'),
        Index('idx_kyc_status', 'status'),
        Index('idx_kyc_document_type', 'document_type'),
        Index('idx_kyc_submitted_at', 'submitted_at'),
    )


class BankAccount(Base):
    """User bank account details"""
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Account details
    account_holder_name = Column(String(200), nullable=False)
    account_number = Column(String(50), nullable=False)  # Encrypted in production
    ifsc_code = Column(String(11), nullable=False)
    bank_name = Column(String(200), nullable=True)
    branch_name = Column(String(200), nullable=True)
    account_type = Column(String(20), default="savings")  # savings, current

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(30), nullable=True)  # penny_drop, manual
    verification_reference = Column(String(100), nullable=True)  # Reference from payment gateway
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_primary = Column(Boolean, default=False)  # Primary account for withdrawals
    status = Column(String(20), default="active")  # active, inactive, suspended

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_bank_accounts_user_id', 'user_id'),
        Index('idx_bank_accounts_is_primary', 'is_primary'),
        Index('idx_bank_accounts_status', 'status'),
    )


class KYCVerificationHistory(Base):
    """History of KYC verification attempts"""
    __tablename__ = "kyc_verification_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kyc_document_id = Column(UUID(as_uuid=True), ForeignKey("kyc_documents.id", ondelete="SET NULL"), nullable=True)

    # Action details
    action = Column(String(30), nullable=False)  # submitted, approved, rejected, updated
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_kyc_history_user_id', 'user_id'),
        Index('idx_kyc_history_document_id', 'kyc_document_id'),
        Index('idx_kyc_history_created_at', 'created_at'),
    )
