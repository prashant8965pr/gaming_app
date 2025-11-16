"""
User Profile API Endpoints
Handles user profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from config.database import get_db
from models.user import User, UserProfile, UserStatistics
from schemas.user import (
    UpdateProfileRequest,
    UserProfileResponse,
    UserStatisticsResponse,
    UpdateProfileResponse
)
from core.exceptions import UserNotFoundError

router = APIRouter()


async def get_current_user(
    # TODO: Extract user from JWT token
    # This is a placeholder - will be implemented with auth dependency
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    This is a placeholder function. In the complete implementation,
    this will decode the JWT token and return the user.
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise UserNotFoundError()

    return user


@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile

    Returns complete user profile with statistics

    **Note**: Authentication required (will be added in next iteration)
    """
    # TODO: Use current_user from authentication
    # For now, return a placeholder response

    return {
        "success": True,
        "message": "Authentication required. This endpoint will be protected in the next iteration.",
        "data": {
            "note": "Use POST /api/v1/auth/verify-otp to login and get tokens first"
        }
    }


@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    request_data: UpdateProfileRequest,
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile

    - **display_name**: User's display name
    - **bio**: User biography (max 500 chars)
    - **email**: Email address
    - **date_of_birth**: Date of birth (must be 18+)
    - **state**: State
    - **city**: City
    - **pincode**: PIN code

    Returns updated profile

    **Note**: Authentication required (will be added in next iteration)
    """
    # TODO: Implement with current_user

    return {
        "success": True,
        "message": "Authentication required. This endpoint will be protected in the next iteration.",
        "data": request_data.dict(exclude_none=True)
    }


@router.get("/statistics", response_model=Dict[str, Any])
async def get_user_statistics(
    # TODO: Add authentication dependency
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's gaming statistics

    Returns:
    - Total games played/won/lost
    - Win percentage
    - Total winnings and spending
    - Current and longest streak
    - Game-wise statistics

    **Note**: Authentication required (will be added in next iteration)
    """
    return {
        "success": True,
        "message": "Authentication required. This endpoint will be protected in the next iteration.",
        "data": {
            "note": "Statistics will be available after playing games"
        }
    }
