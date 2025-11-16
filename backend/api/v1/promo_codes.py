"""
Promo Code API Endpoints
Manages promo codes for marketing campaigns
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from config.database import get_db
from models.user import User
from models.promo_code import PromoCode, PromoCodeUsage, PromoCodeType, PromoCodeStatus
from services.promo_code_service import PromoCodeService
from core.security import get_current_user, require_admin

router = APIRouter()


# ===========================
# Pydantic Models
# ===========================

class CreatePromoCodeRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, description="Promo code (uppercase)")
    description: Optional[str] = Field(None, max_length=500)
    type: PromoCodeType
    value: float = Field(..., gt=0, description="Percentage or fixed amount")
    max_discount: Optional[float] = Field(None, gt=0, description="Max discount for percentage type")
    max_uses: Optional[int] = Field(None, gt=0, description="Total uses allowed")
    max_uses_per_user: int = Field(1, ge=1, description="Max uses per user")
    min_transaction_amount: Optional[float] = Field(None, ge=0)
    valid_from: datetime
    valid_until: datetime
    is_public: bool = Field(True, description="Public or invite-only")
    target_user_ids: Optional[str] = Field(None, description="Comma-separated user IDs")


class UpdatePromoCodeRequest(BaseModel):
    description: Optional[str] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    valid_until: Optional[datetime] = None
    status: Optional[PromoCodeStatus] = None


class ApplyPromoCodeRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    transaction_amount: float = Field(..., gt=0)


class PromoCodeResponse(BaseModel):
    id: str
    code: str
    description: Optional[str]
    type: PromoCodeType
    value: float
    max_discount: Optional[float]
    max_uses: Optional[int]
    max_uses_per_user: int
    current_uses: int
    remaining_uses: float
    min_transaction_amount: Optional[float]
    valid_from: datetime
    valid_until: datetime
    status: PromoCodeStatus
    is_public: bool
    is_valid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PromoCodeStatsResponse(BaseModel):
    code: str
    total_uses: int
    unique_users: int
    total_discount_given: float
    remaining_uses: float
    is_active: bool
    is_valid: bool


# ===========================
# Admin Endpoints
# ===========================

@router.post("/admin/promo-codes", status_code=status.HTTP_201_CREATED)
async def create_promo_code(
    request: CreatePromoCodeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new promo code (Admin only)

    - **code**: Unique promo code (will be converted to uppercase)
    - **type**: PERCENTAGE, FIXED, or FREE_ENTRY
    - **value**: Percentage or fixed amount
    - **max_discount**: Maximum discount for percentage type
    - **max_uses**: Total usage limit (null = unlimited)
    - **max_uses_per_user**: Per-user usage limit
    - **valid_from/valid_until**: Validity period
    - **is_public**: Public or targeted campaign
    """
    # Check if code already exists
    result = await db.execute(
        select(PromoCode).where(PromoCode.code == request.code.upper())
    )
    existing_code = result.scalar_one_or_none()

    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code already exists"
        )

    # Validate dates
    if request.valid_from >= request.valid_until:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="valid_until must be after valid_from"
        )

    # Validate percentage
    if request.type == PromoCodeType.PERCENTAGE and (request.value <= 0 or request.value > 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentage value must be between 0 and 100"
        )

    # Create promo code
    promo_code = PromoCode(
        code=request.code.upper(),
        description=request.description,
        type=request.type,
        value=request.value,
        max_discount=request.max_discount,
        max_uses=request.max_uses,
        max_uses_per_user=request.max_uses_per_user,
        min_transaction_amount=request.min_transaction_amount,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        is_public=request.is_public,
        target_user_ids=request.target_user_ids,
        created_by=current_user.id
    )

    db.add(promo_code)
    await db.commit()
    await db.refresh(promo_code)

    return {
        "success": True,
        "message": "Promo code created successfully",
        "data": PromoCodeResponse.from_orm(promo_code)
    }


@router.get("/admin/promo-codes")
async def list_promo_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[PromoCodeStatus] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all promo codes (Admin only)

    Supports pagination and filtering by status.
    """
    query = select(PromoCode)

    if status_filter:
        query = query.where(PromoCode.status == status_filter)

    query = query.order_by(PromoCode.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    promo_codes = result.scalars().all()

    # Get total count
    count_query = select(func.count(PromoCode.id))
    if status_filter:
        count_query = count_query.where(PromoCode.status == status_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    return {
        "success": True,
        "data": {
            "promo_codes": [PromoCodeResponse.from_orm(pc) for pc in promo_codes],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    }


@router.get("/admin/promo-codes/{promo_code_id}")
async def get_promo_code(
    promo_code_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get promo code details (Admin only)
    """
    result = await db.execute(
        select(PromoCode).where(PromoCode.id == promo_code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    return {
        "success": True,
        "data": PromoCodeResponse.from_orm(promo_code)
    }


@router.patch("/admin/promo-codes/{promo_code_id}")
async def update_promo_code(
    promo_code_id: str,
    request: UpdatePromoCodeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update promo code (Admin only)

    Can update: description, max_uses, max_uses_per_user, valid_until, status
    """
    result = await db.execute(
        select(PromoCode).where(PromoCode.id == promo_code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    # Update fields
    if request.description is not None:
        promo_code.description = request.description
    if request.max_uses is not None:
        promo_code.max_uses = request.max_uses
    if request.max_uses_per_user is not None:
        promo_code.max_uses_per_user = request.max_uses_per_user
    if request.valid_until is not None:
        promo_code.valid_until = request.valid_until
    if request.status is not None:
        promo_code.status = request.status

    await db.commit()
    await db.refresh(promo_code)

    return {
        "success": True,
        "message": "Promo code updated successfully",
        "data": PromoCodeResponse.from_orm(promo_code)
    }


@router.delete("/admin/promo-codes/{promo_code_id}")
async def delete_promo_code(
    promo_code_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete promo code (Admin only)

    Note: This will also delete all usage records (CASCADE).
    """
    result = await db.execute(
        select(PromoCode).where(PromoCode.id == promo_code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    await db.delete(promo_code)
    await db.commit()

    return {
        "success": True,
        "message": "Promo code deleted successfully"
    }


@router.get("/admin/promo-codes/{promo_code_id}/stats")
async def get_promo_code_stats(
    promo_code_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get promo code statistics (Admin only)

    Returns usage stats, unique users, total discount given, etc.
    """
    stats = await PromoCodeService.get_promo_code_stats(db, promo_code_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    return {
        "success": True,
        "data": stats
    }


@router.get("/admin/promo-codes/{promo_code_id}/usages")
async def get_promo_code_usages(
    promo_code_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get promo code usage history (Admin only)
    """
    result = await db.execute(
        select(PromoCode).where(PromoCode.id == promo_code_id)
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    # Get usages
    result = await db.execute(
        select(PromoCodeUsage)
        .where(PromoCodeUsage.promo_code_id == promo_code_id)
        .order_by(PromoCodeUsage.used_at.desc())
        .offset(skip)
        .limit(limit)
    )
    usages = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(func.count(PromoCodeUsage.id))
        .where(PromoCodeUsage.promo_code_id == promo_code_id)
    )
    total = count_result.scalar()

    return {
        "success": True,
        "data": {
            "usages": [
                {
                    "id": str(usage.id),
                    "user_id": str(usage.user_id),
                    "discount_amount": usage.discount_amount,
                    "transaction_amount": usage.transaction_amount,
                    "used_at": usage.used_at
                }
                for usage in usages
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    }


# ===========================
# User Endpoints
# ===========================

@router.get("/promo-codes")
async def get_available_promo_codes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available promo codes for current user

    Returns only public, active, and valid promo codes that the user hasn't exhausted.
    """
    promo_codes = await PromoCodeService.get_user_promo_codes(db, current_user)

    return {
        "success": True,
        "data": {
            "promo_codes": [
                {
                    "code": pc.code,
                    "description": pc.description,
                    "type": pc.type,
                    "value": pc.value,
                    "max_discount": pc.max_discount,
                    "min_transaction_amount": pc.min_transaction_amount,
                    "valid_until": pc.valid_until,
                }
                for pc in promo_codes
            ]
        }
    }


@router.post("/promo-codes/validate")
async def validate_promo_code(
    code: str = Query(..., min_length=3, max_length=50),
    transaction_amount: Optional[float] = Query(None, gt=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a promo code

    Checks if the code is valid for the current user and transaction amount.
    Returns discount amount if valid.
    """
    is_valid, error_msg, promo_code = await PromoCodeService.validate_promo_code(
        db, code, current_user, transaction_amount
    )

    if not is_valid:
        return {
            "success": False,
            "error": {
                "code": "INVALID_PROMO_CODE",
                "message": error_msg
            }
        }

    # Calculate discount
    discount = 0.0
    if transaction_amount:
        discount = PromoCodeService.calculate_discount(promo_code, transaction_amount)

    return {
        "success": True,
        "data": {
            "valid": True,
            "code": promo_code.code,
            "type": promo_code.type,
            "value": promo_code.value,
            "discount_amount": discount,
            "final_amount": transaction_amount - discount if transaction_amount else None
        }
    }


@router.post("/promo-codes/apply")
async def apply_promo_code(
    request: ApplyPromoCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply a promo code to a transaction

    Records the usage and returns the discount amount.
    Note: This should be called during payment processing.
    """
    success, error_msg, discount_amount = await PromoCodeService.apply_promo_code(
        db, request.code, current_user, request.transaction_amount
    )

    if not success:
        return {
            "success": False,
            "error": {
                "code": "PROMO_CODE_APPLICATION_FAILED",
                "message": error_msg
            }
        }

    return {
        "success": True,
        "message": "Promo code applied successfully",
        "data": {
            "code": request.code.upper(),
            "discount_amount": discount_amount,
            "original_amount": request.transaction_amount,
            "final_amount": request.transaction_amount - discount_amount
        }
    }


@router.get("/promo-codes/my-usages")
async def get_my_promo_code_usages(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's promo code usage history
    """
    result = await db.execute(
        select(PromoCodeUsage)
        .where(PromoCodeUsage.user_id == current_user.id)
        .order_by(PromoCodeUsage.used_at.desc())
        .offset(skip)
        .limit(limit)
    )
    usages = result.scalars().all()

    # Get promo codes for each usage
    usage_data = []
    for usage in usages:
        promo_result = await db.execute(
            select(PromoCode).where(PromoCode.id == usage.promo_code_id)
        )
        promo_code = promo_result.scalar_one_or_none()

        usage_data.append({
            "id": str(usage.id),
            "code": promo_code.code if promo_code else "N/A",
            "discount_amount": usage.discount_amount,
            "transaction_amount": usage.transaction_amount,
            "used_at": usage.used_at
        })

    # Get total count
    count_result = await db.execute(
        select(func.count(PromoCodeUsage.id))
        .where(PromoCodeUsage.user_id == current_user.id)
    )
    total = count_result.scalar()

    return {
        "success": True,
        "data": {
            "usages": usage_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    }
