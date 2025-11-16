"""
Authentication API Endpoints
Handles user authentication: OTP, login, token refresh, logout
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import Dict, Any

from config.database import get_db, get_redis
from config.settings import settings
from models.user import User, UserSession, OTPAttempt, UserProfile, UserStatistics
from schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    LoginResponse,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest
)
from core.security import (
    generate_otp,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_referral_code
)
from core.exceptions import (
    InvalidOTPError,
    OTPExpiredError,
    UserNotFoundError,
    InvalidTokenError,
    RateLimitExceededError
)

router = APIRouter()


async def check_rate_limit(redis, key: str, limit: int, window: int) -> bool:
    """
    Check if rate limit is exceeded

    Args:
        redis: Redis client
        key: Rate limit key
        limit: Max requests allowed
        window: Time window in seconds

    Returns:
        True if rate limit not exceeded, False otherwise
    """
    current = await redis.get(key)
    if current is None:
        await redis.setex(key, window, 1)
        return True

    current = int(current)
    if current >= limit:
        return False

    await redis.incr(key)
    return True


async def send_sms_otp(phone: str, otp: str) -> bool:
    """
    Send OTP via SMS using Twilio

    Args:
        phone: Phone number
        otp: OTP code

    Returns:
        True if sent successfully
    """
    # TODO: Integrate Twilio SMS API
    # For now, just print the OTP (development mode)
    print(f"📱 SMS OTP for {phone}: {otp}")
    print(f"   (In production, this will be sent via Twilio)")
    return True


@router.post("/send-otp", response_model=Dict[str, Any])
async def send_otp(
    request_data: SendOTPRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Send OTP to phone number

    - **phone**: Phone number with country code (+919876543210)
    - **purpose**: login, registration, or verification

    Returns OTP expiry time and confirmation message
    """
    # Rate limiting: Max 3 OTPs per hour per phone number
    rate_limit_key = f"otp_rate_limit:{request_data.phone}"
    if not await check_rate_limit(redis, rate_limit_key, limit=3, window=3600):
        raise RateLimitExceededError("Too many OTP requests. Please try again after 1 hour.")

    # Generate OTP
    otp = generate_otp()

    # Calculate expiry
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    # Save OTP to database
    otp_attempt = OTPAttempt(
        phone=request_data.phone,
        otp_code=otp,
        purpose=request_data.purpose,
        expires_at=expires_at
    )
    db.add(otp_attempt)
    await db.commit()

    # Send OTP via SMS
    await send_sms_otp(request_data.phone, otp)

    return {
        "success": True,
        "data": SendOTPResponse(
            otp_sent=True,
            expires_in=settings.OTP_EXPIRY_MINUTES * 60,
            message=f"OTP sent to {request_data.phone}"
        )
    }


@router.post("/verify-otp", response_model=Dict[str, Any])
async def verify_otp(
    request_data: VerifyOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and login/register user

    - **phone**: Phone number
    - **otp**: 6-digit OTP
    - **device_id**: Unique device identifier
    - **device_name**: Device name (optional)
    - **device_os**: Device OS (optional)

    Returns user information and JWT tokens
    """
    # Find latest OTP attempt for this phone
    query = select(OTPAttempt).where(
        and_(
            OTPAttempt.phone == request_data.phone,
            OTPAttempt.is_verified == False
        )
    ).order_by(OTPAttempt.created_at.desc())

    result = await db.execute(query)
    otp_attempt = result.scalars().first()

    if not otp_attempt:
        raise InvalidOTPError("No OTP found for this phone number")

    # Check if OTP expired
    if datetime.utcnow() > otp_attempt.expires_at:
        raise OTPExpiredError("OTP has expired. Please request a new one.")

    # Check if max attempts exceeded
    if otp_attempt.attempts_count >= settings.MAX_OTP_ATTEMPTS:
        raise InvalidOTPError("Maximum OTP attempts exceeded. Please request a new OTP.")

    # Verify OTP
    if otp_attempt.otp_code != request_data.otp:
        # Increment attempts
        otp_attempt.attempts_count += 1
        await db.commit()
        raise InvalidOTPError(f"Invalid OTP. {settings.MAX_OTP_ATTEMPTS - otp_attempt.attempts_count} attempts remaining.")

    # Mark OTP as verified
    otp_attempt.is_verified = True
    otp_attempt.verified_at = datetime.utcnow()

    # Check if user exists
    user_query = select(User).where(User.phone == request_data.phone)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()

    is_new_user = False

    if not user:
        # Create new user
        is_new_user = True

        # Generate username from phone (can be changed later)
        username = f"user_{request_data.phone[-6:]}"

        # Generate unique referral code
        referral_code = generate_referral_code(username)

        user = User(
            username=username,
            phone=request_data.phone,
            is_phone_verified=True,
            referral_code=referral_code,
            last_login_at=datetime.utcnow()
        )
        db.add(user)
        await db.flush()  # Get user.id

        # Create user profile
        user_profile = UserProfile(user_id=user.id)
        db.add(user_profile)

        # Create user statistics
        user_stats = UserStatistics(user_id=user.id)
        db.add(user_stats)

    else:
        # Update last login
        user.last_login_at = datetime.utcnow()

    # Generate tokens
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Calculate token expiry
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create session
    user_session = UserSession(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        device_id=request_data.device_id,
        device_name=request_data.device_name,
        device_os=request_data.device_os,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at
    )
    db.add(user_session)

    await db.commit()

    # Prepare response
    user_response = UserResponse(
        id=str(user.id),
        username=user.username,
        phone=user.phone,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        kyc_status=user.kyc_status,
        referral_code=user.referral_code,
        created_at=user.created_at
    )

    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {
        "success": True,
        "data": LoginResponse(
            user=user_response,
            tokens=token_response,
            is_new_user=is_new_user
        )
    }


@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_access_token(
    request_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token

    Returns new access token
    """
    # Decode refresh token
    payload = decode_token(request_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")

    # Verify session exists and is active
    session_query = select(UserSession).where(
        and_(
            UserSession.refresh_token == request_data.refresh_token,
            UserSession.is_active == True
        )
    )
    session_result = await db.execute(session_query)
    session = session_result.scalars().first()

    if not session:
        raise InvalidTokenError("Session not found or expired")

    # Get user
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()

    if not user:
        raise UserNotFoundError()

    # Generate new access token
    token_data = {"sub": str(user.id), "username": user.username}
    new_access_token = create_access_token(token_data)

    # Update session
    session.access_token = new_access_token
    session.last_activity_at = datetime.utcnow()
    await db.commit()

    return {
        "success": True,
        "data": RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    }


@router.post("/logout", response_model=Dict[str, Any])
async def logout(
    request_data: LogoutRequest,
    # TODO: Add authentication dependency to get current user
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user

    - **all_devices**: If true, logout from all devices

    Invalidates the current session or all sessions
    """
    # TODO: Get current user from token
    # For now, this is a placeholder
    # In next iteration, we'll add authentication dependency

    return {
        "success": True,
        "message": "Logged out successfully"
    }


async def get_current_user_ws(token: str, db: AsyncSession) -> User:
    """
    Get current user from WebSocket token
    Used for WebSocket authentication

    Args:
        token: JWT access token
        db: Database session

    Returns:
        User object

    Raises:
        Exception: If token is invalid or user not found
    """
    try:
        # Decode token
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenError("Invalid token payload")

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundError("User not found")

        if user.status != "active":
            raise Exception(f"User account is {user.status}")

        return user

    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")
