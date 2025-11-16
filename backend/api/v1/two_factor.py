"""
Two-Factor Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional

from config.database import get_db
from models.user import User
from services.two_factor_service import TwoFactorService
from middleware.auth import get_current_user

router = APIRouter()


# Request/Response Models
class Setup2FAResponse(BaseModel):
    """Response for 2FA setup"""
    secret: str
    qr_code: str
    backup_codes: List[str]
    manual_entry_key: str


class Enable2FARequest(BaseModel):
    """Request to enable 2FA"""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token")
    backup_codes: List[str] = Field(..., min_length=10, max_length=10, description="10 backup codes to store")


class Verify2FARequest(BaseModel):
    """Request to verify 2FA token"""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token")


class VerifyBackupCodeRequest(BaseModel):
    """Request to verify backup code"""
    code: str = Field(..., description="Backup code (format: XXXX-XXXX)")


class Disable2FARequest(BaseModel):
    """Request to disable 2FA"""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token for verification")


class Regenerate2FACodesRequest(BaseModel):
    """Request to regenerate backup codes"""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP token for verification")


class TwoFactorStatusResponse(BaseModel):
    """2FA status response"""
    enabled: bool
    verified: bool
    enabled_at: Optional[str]
    last_used_at: Optional[str]
    backup_codes_remaining: int
    backup_codes_used: int


@router.post("/setup", response_model=dict)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Setup 2FA for the current user

    Returns QR code, secret, and backup codes
    User must verify with a token to enable 2FA
    """
    try:
        secret, uri, backup_codes = await TwoFactorService.setup_2fa(db, current_user)

        # Generate QR code
        qr_code = TwoFactorService.generate_qr_code(uri)

        return {
            "success": True,
            "data": {
                "secret": secret,
                "qr_code": qr_code,
                "backup_codes": backup_codes,
                "manual_entry_key": secret,
                "message": "Scan the QR code with your authenticator app and verify with a token to enable 2FA"
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup 2FA: {str(e)}"
        )


@router.post("/enable", response_model=dict)
async def enable_2fa(
    request: Enable2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable 2FA after verifying initial token

    This confirms the user has successfully set up their authenticator app
    """
    try:
        success = await TwoFactorService.enable_2fa(
            db,
            current_user,
            request.token,
            request.backup_codes
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token. Please check your authenticator app and try again."
            )

        return {
            "success": True,
            "message": "2FA has been enabled successfully. Keep your backup codes in a safe place."
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable 2FA: {str(e)}"
        )


@router.post("/verify", response_model=dict)
async def verify_2fa(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify 2FA token

    Used during login or for sensitive operations
    """
    try:
        success = await TwoFactorService.verify_2fa(
            db,
            current_user,
            request.token
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA token"
            )

        return {
            "success": True,
            "message": "2FA verification successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify 2FA: {str(e)}"
        )


@router.post("/verify-backup-code", response_model=dict)
async def verify_backup_code(
    request: VerifyBackupCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify backup code for 2FA recovery

    Each backup code can only be used once
    """
    try:
        success = await TwoFactorService.verify_backup_code(
            db,
            current_user,
            request.code
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or already used backup code"
            )

        return {
            "success": True,
            "message": "Backup code verified successfully. This code has been marked as used."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify backup code: {str(e)}"
        )


@router.post("/disable", response_model=dict)
async def disable_2fa(
    request: Disable2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable 2FA for the current user

    Requires 2FA token verification
    """
    try:
        success = await TwoFactorService.disable_2fa(
            db,
            current_user,
            request.token
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token. Cannot disable 2FA without verification."
            )

        return {
            "success": True,
            "message": "2FA has been disabled successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable 2FA: {str(e)}"
        )


@router.post("/regenerate-backup-codes", response_model=dict)
async def regenerate_backup_codes(
    request: Regenerate2FACodesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate backup codes

    All old backup codes will be invalidated
    Requires 2FA token verification
    """
    try:
        backup_codes = await TwoFactorService.regenerate_backup_codes(
            db,
            current_user,
            request.token
        )

        if backup_codes is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token or 2FA not enabled"
            )

        return {
            "success": True,
            "data": {
                "backup_codes": backup_codes,
                "message": "New backup codes generated. All old backup codes have been invalidated."
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate backup codes: {str(e)}"
        )


@router.get("/status", response_model=dict)
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get 2FA status for the current user
    """
    try:
        status_data = await TwoFactorService.get_2fa_status(db, current_user)

        return {
            "success": True,
            "data": status_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get 2FA status: {str(e)}"
        )
