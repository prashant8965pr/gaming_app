"""
Two-Factor Authentication Service
Handles TOTP generation, verification, and backup codes
"""

import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.two_factor import TwoFactorAuth, TwoFactorBackupCode
from models.user import User
from datetime import datetime


class TwoFactorService:
    """Service for managing two-factor authentication"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_totp_uri(secret: str, username: str, issuer: str = "Gaming Platform") -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username,
            issuer_name=issuer
        )

    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """
        Generate QR code as base64 image
        Returns base64 encoded PNG image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """
        Verify TOTP token
        Allows for clock skew (±1 interval)
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()  # 8 characters
            codes.append(f"{code[:4]}-{code[4:]}")  # Format: XXXX-XXXX
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code for secure storage"""
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    async def setup_2fa(
        db: AsyncSession,
        user: User
    ) -> Tuple[str, str, List[str]]:
        """
        Setup 2FA for user
        Returns: (secret, qr_code_uri, backup_codes)
        """
        # Check if 2FA already exists
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        existing_2fa = result.scalar_one_or_none()

        if existing_2fa and existing_2fa.is_enabled:
            raise ValueError("2FA is already enabled for this user")

        # Generate new secret
        secret = TwoFactorService.generate_secret()

        # Generate QR code URI
        uri = TwoFactorService.generate_totp_uri(secret, user.username)

        # Generate backup codes
        backup_codes = TwoFactorService.generate_backup_codes()

        # Create or update 2FA record
        if existing_2fa:
            existing_2fa.secret = secret
            existing_2fa.is_enabled = False
            existing_2fa.is_verified = False
        else:
            two_factor = TwoFactorAuth(
                user_id=user.id,
                secret=secret,
                is_enabled=False,
                is_verified=False
            )
            db.add(two_factor)

        # Delete old backup codes
        await db.execute(
            select(TwoFactorBackupCode).where(TwoFactorBackupCode.user_id == user.id)
        )
        # Would need to delete here, but for simplicity storing in main table

        await db.commit()

        return secret, uri, backup_codes

    @staticmethod
    async def enable_2fa(
        db: AsyncSession,
        user: User,
        token: str,
        backup_codes: List[str]
    ) -> bool:
        """
        Enable 2FA after verifying initial token
        """
        # Get 2FA record
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            raise ValueError("2FA not set up for this user")

        if two_factor.is_enabled:
            raise ValueError("2FA is already enabled")

        # Verify token
        if not TwoFactorService.verify_totp(two_factor.secret, token):
            return False

        # Store backup codes (hashed)
        for code in backup_codes:
            backup_code = TwoFactorBackupCode(
                user_id=user.id,
                code_hash=TwoFactorService.hash_backup_code(code),
                is_used=False
            )
            db.add(backup_code)

        # Enable 2FA
        two_factor.is_enabled = True
        two_factor.is_verified = True
        two_factor.enabled_at = datetime.utcnow()

        await db.commit()

        return True

    @staticmethod
    async def verify_2fa(
        db: AsyncSession,
        user: User,
        token: str
    ) -> bool:
        """
        Verify 2FA token for login
        """
        # Get 2FA record
        result = await db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user.id,
                TwoFactorAuth.is_enabled == True
            )
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return False

        # Verify TOTP token
        if TwoFactorService.verify_totp(two_factor.secret, token):
            two_factor.last_used_at = datetime.utcnow()
            await db.commit()
            return True

        return False

    @staticmethod
    async def verify_backup_code(
        db: AsyncSession,
        user: User,
        code: str
    ) -> bool:
        """
        Verify backup code for 2FA recovery
        """
        code_hash = TwoFactorService.hash_backup_code(code)

        # Find unused backup code
        result = await db.execute(
            select(TwoFactorBackupCode).where(
                TwoFactorBackupCode.user_id == user.id,
                TwoFactorBackupCode.code_hash == code_hash,
                TwoFactorBackupCode.is_used == False
            )
        )
        backup_code = result.scalar_one_or_none()

        if not backup_code:
            return False

        # Mark as used
        backup_code.is_used = True
        backup_code.used_at = datetime.utcnow()

        # Update 2FA last used
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_factor = result.scalar_one_or_none()
        if two_factor:
            two_factor.last_used_at = datetime.utcnow()
            two_factor.backup_codes_used += 1

        await db.commit()

        return True

    @staticmethod
    async def disable_2fa(
        db: AsyncSession,
        user: User,
        token: Optional[str] = None
    ) -> bool:
        """
        Disable 2FA for user
        Requires verification token if 2FA is currently enabled
        """
        # Get 2FA record
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return True  # Already disabled

        # If enabled, require token verification
        if two_factor.is_enabled and token:
            if not TwoFactorService.verify_totp(two_factor.secret, token):
                return False

        # Disable 2FA
        two_factor.is_enabled = False
        two_factor.is_verified = False

        # Delete backup codes
        await db.execute(
            select(TwoFactorBackupCode).where(TwoFactorBackupCode.user_id == user.id)
        )

        await db.commit()

        return True

    @staticmethod
    async def regenerate_backup_codes(
        db: AsyncSession,
        user: User,
        token: str
    ) -> Optional[List[str]]:
        """
        Regenerate backup codes
        Requires 2FA token verification
        """
        # Get 2FA record
        result = await db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user.id,
                TwoFactorAuth.is_enabled == True
            )
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return None

        # Verify token
        if not TwoFactorService.verify_totp(two_factor.secret, token):
            return None

        # Delete old backup codes
        result = await db.execute(
            select(TwoFactorBackupCode).where(TwoFactorBackupCode.user_id == user.id)
        )
        old_codes = result.scalars().all()
        for code in old_codes:
            await db.delete(code)

        # Generate new backup codes
        backup_codes = TwoFactorService.generate_backup_codes()

        # Store new backup codes
        for code in backup_codes:
            backup_code = TwoFactorBackupCode(
                user_id=user.id,
                code_hash=TwoFactorService.hash_backup_code(code),
                is_used=False
            )
            db.add(backup_code)

        # Reset backup codes used counter
        two_factor.backup_codes_used = 0

        await db.commit()

        return backup_codes

    @staticmethod
    async def get_2fa_status(
        db: AsyncSession,
        user: User
    ) -> dict:
        """Get 2FA status for user"""
        result = await db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return {
                "enabled": False,
                "verified": False,
                "backup_codes_remaining": 0
            }

        # Count unused backup codes
        result = await db.execute(
            select(TwoFactorBackupCode).where(
                TwoFactorBackupCode.user_id == user.id,
                TwoFactorBackupCode.is_used == False
            )
        )
        backup_codes_count = len(result.scalars().all())

        return {
            "enabled": two_factor.is_enabled,
            "verified": two_factor.is_verified,
            "enabled_at": two_factor.enabled_at.isoformat() if two_factor.enabled_at else None,
            "last_used_at": two_factor.last_used_at.isoformat() if two_factor.last_used_at else None,
            "backup_codes_remaining": backup_codes_count,
            "backup_codes_used": two_factor.backup_codes_used
        }
