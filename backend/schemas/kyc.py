"""
KYC Schemas
Pydantic models for KYC and bank account requests/responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
import re


# ============================================================================
# KYC Document Schemas
# ============================================================================

class SubmitKYCRequest(BaseModel):
    """Request schema for submitting KYC document"""
    document_type: str = Field(..., example="aadhaar")
    document_number: str = Field(..., min_length=1, max_length=50, example="XXXX-XXXX-1234")
    full_name: str = Field(..., min_length=1, max_length=200, example="John Doe")
    father_name: Optional[str] = Field(None, max_length=200, example="Robert Doe")
    date_of_birth: date = Field(..., example="1995-01-15")
    gender: Optional[str] = Field(None, example="Male")
    address: Optional[str] = Field(None, example="123, Main Street, Mumbai, Maharashtra - 400001")

    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['aadhaar', 'pan', 'voter_id', 'driving_license', 'passport']
        if v.lower() not in allowed_types:
            raise ValueError(f'Document type must be one of: {", ".join(allowed_types)}')
        return v.lower()

    @validator('document_number')
    def validate_document_number(cls, v, values):
        """Validate document number format based on type"""
        if 'document_type' in values:
            doc_type = values['document_type']

            # Remove spaces and hyphens
            cleaned = v.replace(' ', '').replace('-', '')

            if doc_type == 'aadhaar':
                # Aadhaar: 12 digits
                if not re.match(r'^\d{12}$', cleaned):
                    raise ValueError('Aadhaar number must be 12 digits')
            elif doc_type == 'pan':
                # PAN: 10 characters (5 letters, 4 digits, 1 letter)
                if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v.upper()):
                    raise ValueError('Invalid PAN format. Example: ABCDE1234F')
            elif doc_type == 'voter_id':
                # Voter ID: 3 letters followed by 7 digits
                if not re.match(r'^[A-Z]{3}[0-9]{7}$', v.upper()):
                    raise ValueError('Invalid Voter ID format')
            elif doc_type == 'driving_license':
                # DL: State code + 13 digits or letters
                if len(cleaned) < 10:
                    raise ValueError('Invalid Driving License format')

        return v

    @validator('date_of_birth')
    def validate_age(cls, v):
        """Ensure user is at least 18 years old"""
        if v:
            today = datetime.now().date()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError('User must be at least 18 years old for KYC')
            if age > 120:
                raise ValueError('Invalid date of birth')
        return v


class UploadKYCDocumentRequest(BaseModel):
    """Request schema for uploading KYC document images"""
    kyc_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    document_side: str = Field(..., example="front")  # front, back, selfie

    @validator('document_side')
    def validate_document_side(cls, v):
        allowed_sides = ['front', 'back', 'selfie']
        if v.lower() not in allowed_sides:
            raise ValueError(f'Document side must be one of: {", ".join(allowed_sides)}')
        return v.lower()


class KYCDocumentResponse(BaseModel):
    """Response schema for KYC document"""
    id: str
    user_id: str
    document_type: str
    document_number: str  # Masked
    full_name: str
    date_of_birth: Optional[datetime]
    status: str
    document_front_url: Optional[str]
    document_back_url: Optional[str]
    selfie_url: Optional[str]
    rejection_reason: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class KYCStatusResponse(BaseModel):
    """Response schema for KYC status"""
    kyc_completed: bool
    kyc_status: str
    kyc_documents: list[KYCDocumentResponse]
    pending_actions: list[str]  # List of what's needed: ["Upload Aadhaar front", "Upload selfie"]


# ============================================================================
# Admin KYC Review Schemas
# ============================================================================

class ReviewKYCRequest(BaseModel):
    """Admin request schema for reviewing KYC"""
    kyc_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    action: str = Field(..., example="approve")  # approve, reject, request_resubmit
    rejection_reason: Optional[str] = Field(None, example="Document image is blurry")
    admin_notes: Optional[str] = Field(None, example="Verified with government database")

    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['approve', 'reject', 'request_resubmit']
        if v.lower() not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v.lower()


class KYCReviewResponse(BaseModel):
    """Response schema for KYC review"""
    message: str
    kyc_document: KYCDocumentResponse


# ============================================================================
# Bank Account Schemas
# ============================================================================

class AddBankAccountRequest(BaseModel):
    """Request schema for adding bank account"""
    account_holder_name: str = Field(..., min_length=1, max_length=200, example="John Doe")
    account_number: str = Field(..., min_length=8, max_length=20, example="1234567890")
    confirm_account_number: str = Field(..., min_length=8, max_length=20, example="1234567890")
    ifsc_code: str = Field(..., min_length=11, max_length=11, example="SBIN0001234")
    account_type: str = Field(default="savings", example="savings")

    @validator('confirm_account_number')
    def validate_account_numbers_match(cls, v, values):
        """Ensure account numbers match"""
        if 'account_number' in values and v != values['account_number']:
            raise ValueError('Account numbers do not match')
        return v

    @validator('ifsc_code')
    def validate_ifsc(cls, v):
        """Validate IFSC code format"""
        # IFSC format: 4 letters (bank code) + 0 + 6 characters (branch code)
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v.upper()):
            raise ValueError('Invalid IFSC code format. Example: SBIN0001234')
        return v.upper()

    @validator('account_type')
    def validate_account_type(cls, v):
        allowed_types = ['savings', 'current']
        if v.lower() not in allowed_types:
            raise ValueError(f'Account type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class BankAccountResponse(BaseModel):
    """Response schema for bank account"""
    id: str
    account_holder_name: str
    account_number: str  # Last 4 digits only for security
    ifsc_code: str
    bank_name: Optional[str]
    branch_name: Optional[str]
    account_type: str
    is_verified: bool
    is_primary: bool
    status: str
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SetPrimaryBankAccountRequest(BaseModel):
    """Request schema for setting primary bank account"""
    bank_account_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")


class BankAccountListResponse(BaseModel):
    """Response schema for list of bank accounts"""
    bank_accounts: list[BankAccountResponse]
    primary_account_id: Optional[str]


class VerifyBankAccountRequest(BaseModel):
    """Request schema for penny drop verification"""
    bank_account_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")


class VerifyBankAccountResponse(BaseModel):
    """Response schema for bank account verification"""
    message: str
    bank_account: BankAccountResponse
    verification_status: str  # initiated, verified, failed
