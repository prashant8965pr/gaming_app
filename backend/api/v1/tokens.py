"""
Token API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from services.token_service import TokenService

router = APIRouter(prefix="/tokens", tags=["Tokens"])


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get token balance"""
    wallet = TokenService.get_or_create_wallet(db, str(current_user.id))
    return {
        "success": True,
        "data": {"wallet": wallet.to_dict()}
    }


@router.post("/daily-bonus")
async def claim_daily_bonus(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim daily login bonus"""
    try:
        result = TokenService.claim_daily_bonus(db, str(current_user.id))
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/earn-from-ad")
async def earn_from_ad(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Earn tokens from watching ad"""
    try:
        result = TokenService.earn_from_ad(db, str(current_user.id))
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
