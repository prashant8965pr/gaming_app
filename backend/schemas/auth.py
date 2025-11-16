"""
Authentication Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


# Request Schemas
class SendOTPRequest(BaseModel):
    """Request schema for sending OTP"""
    phone: str = Field(..., description="Phone number with country code", example="+919876543210")
    purpose: str = Field(..., description="OTP purpose", example="login")

    @validator('phone')
    def validate_phone(cls, v):
        # Remove spaces and dashes
        phone = v.replace(" ", "").replace("-", "")
        # Basic validation for Indian phone numbers
        if not re.match(r'^\+91[6-9]\d{9}$', phone):
            raise ValueError('Invalid Indian phone number format. Use +91XXXXXXXXXX')
        return phone

    @validator('purpose')
    def validate_purpose(cls, v):
        if v not in ['login', 'registration', 'verification']:
            raise ValueError('Purpose must be login, registration, or verification')
        return v


class VerifyOTPRequest(BaseModel):
    """Request schema for verifying OTP and login"""
    phone: str = Field(..., example="+919876543210")
    otp: str = Field(..., min_length=6, max_length=6, example="123456")
    device_id: Optional[str] = Field(None, example="unique-device-id")
    device_name: Optional[str] = Field(None, example="Samsung Galaxy S21")
    device_os: Optional[str] = Field(None, example="Android 12")

    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Request schema for logout"""
    all_devices: bool = Field(default=False, description="Logout from all devices")


# Response Schemas
class UserResponse(BaseModel):
    """User information in response"""
    id: str
    username: str
    phone: str
    email: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    kyc_status: str
    referral_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token information in response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginResponse(BaseModel):
    """Response schema for successful login"""
    user: UserResponse
    tokens: TokenResponse
    is_new_user: bool


class SendOTPResponse(BaseModel):
    """Response schema for send OTP"""
    otp_sent: bool
    expires_in: int  # seconds
    message: str


class RefreshTokenResponse(BaseModel):
    """Response schema for refresh token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
