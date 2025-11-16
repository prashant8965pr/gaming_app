"""
Rewards API Endpoints
Handles referrals, achievements, daily bonuses, leaderboards, promo codes, and rewards
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.wallet import Wallet, Transaction
from models.referral import (
    Referral, Achievement, UserAchievement, DailyBonus,
    PromoCode, PromoCodeUsage, Leaderboard, UserLevel, RewardTransaction
)
from schemas.referral import (
    ReferralStatsResponse, ReferralListResponse, ReferralResponse,
    AchievementResponse, UserAchievementResponse, ClaimAchievementRequest,
    AchievementListResponse, DailyBonusResponse, ClaimDailyBonusResponse,
    ValidatePromoCodeRequest, PromoCodeResponse, CreatePromoCodeRequest,
    PromoCodeDetailResponse, LeaderboardRequest, LeaderboardResponse,
    LeaderboardEntryResponse, UserLevelResponse, AddExperienceRequest,
    RewardTransactionResponse, RewardHistoryRequest, RewardHistoryResponse,
    RewardsDashboardResponse
)
from utils.rewards import reward_calculator, leaderboard_calculator

router = APIRouter()


# ============================================================================
# Referral Endpoints
# ============================================================================

@router.get("/referrals/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get referral statistics for current user"""

    # Get all referrals
    query = select(Referral).where(Referral.referrer_id == current_user.id)
    result = await db.execute(query)
    referrals = result.scalars().all()

    # Calculate stats
    total_referrals = len(referrals)
    completed_referrals = sum(1 for r in referrals if r.status == "completed")
    pending_referrals = sum(1 for r in referrals if r.status == "pending")
    total_earnings = sum(r.referrer_reward_amount for r in referrals if r.referrer_reward_given) / 100

    # Generate referral link
    referral_code = current_user.referral_code or str(uuid.uuid4())[:8].upper()
    referral_link = f"https://yourgame.com/signup?ref={referral_code}"

    return ReferralStatsResponse(
        total_referrals=total_referrals,
        completed_referrals=completed_referrals,
        pending_referrals=pending_referrals,
        total_earnings=total_earnings,
        referral_code=referral_code,
        referral_link=referral_link
    )


@router.get("/referrals/list", response_model=ReferralListResponse)
async def get_referral_list(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of referrals for current user"""

    # Get referrals with user details
    query = (
        select(Referral, User)
        .join(User, Referral.referred_id == User.id)
        .where(Referral.referrer_id == current_user.id)
        .order_by(desc(Referral.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    referral_data = result.all()

    # Get total count
    count_query = select(func.count(Referral.id)).where(Referral.referrer_id == current_user.id)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # Build referral responses
    referral_list = []
    for referral, referred_user in referral_data:
        referral_list.append(ReferralResponse(
            id=str(referral.id),
            referred_username=referred_user.username,
            referred_display_name=referred_user.display_name,
            status=referral.status,
            is_kyc_completed=referral.is_kyc_completed,
            is_first_deposit_done=referral.is_first_deposit_done,
            first_deposit_amount=referral.first_deposit_amount / 100,
            referrer_reward_given=referral.referrer_reward_given,
            referrer_reward_amount=referral.referrer_reward_amount / 100,
            created_at=referral.created_at,
            completed_at=referral.completed_at
        ))

    # Get stats
    stats = await get_referral_stats(current_user, db)

    return ReferralListResponse(
        referrals=referral_list,
        total_count=total_count,
        statistics=stats
    )


@router.post("/referrals/check-code")
async def check_referral_code(
    referral_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Check if referral code is valid"""

    # Find user with this referral code
    query = select(User).where(User.referral_code == referral_code.upper())
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid referral code"
        )

    return {
        "valid": True,
        "referrer_username": user.username,
        "referrer_display_name": user.display_name,
        "message": f"Valid referral code from {user.display_name or user.username}"
    }


# ============================================================================
# Achievement Endpoints
# ============================================================================

@router.get("/achievements/list", response_model=AchievementListResponse)
async def get_achievements_list(
    category: Optional[str] = None,
    show_hidden: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of achievements with user progress"""

    # Build achievement query
    achievement_query = select(Achievement).where(Achievement.is_active == True)

    if category:
        achievement_query = achievement_query.where(Achievement.category == category)

    if not show_hidden:
        achievement_query = achievement_query.where(Achievement.is_hidden == False)

    achievement_query = achievement_query.order_by(Achievement.display_order, Achievement.created_at)

    result = await db.execute(achievement_query)
    achievements = result.scalars().all()

    # Get user progress for each achievement
    user_achievement_list = []
    total_points = 0
    unlocked_count = 0

    for achievement in achievements:
        # Check if user has progress on this achievement
        progress_query = select(UserAchievement).where(
            and_(
                UserAchievement.user_id == current_user.id,
                UserAchievement.achievement_id == achievement.id
            )
        )
        progress_result = await db.execute(progress_query)
        user_achievement = progress_result.scalar_one_or_none()

        if user_achievement:
            if user_achievement.is_unlocked:
                unlocked_count += 1
            if user_achievement.is_claimed:
                total_points += achievement.points

            user_achievement_list.append(UserAchievementResponse(
                id=str(user_achievement.id),
                achievement=AchievementResponse.model_validate(achievement),
                progress=user_achievement.progress,
                target=user_achievement.target,
                progress_percentage=user_achievement.progress_percentage,
                is_unlocked=user_achievement.is_unlocked,
                is_claimed=user_achievement.is_claimed,
                unlocked_at=user_achievement.unlocked_at,
                claimed_at=user_achievement.claimed_at
            ))
        else:
            # Create new progress entry
            criteria = achievement.criteria or {}
            target = criteria.get("count", 100)

            user_achievement_list.append(UserAchievementResponse(
                id=str(uuid.uuid4()),
                achievement=AchievementResponse.model_validate(achievement),
                progress=0,
                target=target,
                progress_percentage=0.0,
                is_unlocked=False,
                is_claimed=False,
                unlocked_at=None,
                claimed_at=None
            ))

    total_achievements = len(achievements)
    locked_count = total_achievements - unlocked_count
    completion_percentage = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0

    return AchievementListResponse(
        achievements=user_achievement_list,
        total_achievements=total_achievements,
        unlocked_count=unlocked_count,
        locked_count=locked_count,
        total_points_earned=total_points,
        completion_percentage=completion_percentage
    )


@router.get("/achievements/progress")
async def get_achievement_progress(
    achievement_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed progress for a specific achievement"""

    # Get achievement
    achievement_query = select(Achievement).where(Achievement.id == uuid.UUID(achievement_id))
    achievement_result = await db.execute(achievement_query)
    achievement = achievement_result.scalar_one_or_none()

    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )

    # Get user progress
    progress_query = select(UserAchievement).where(
        and_(
            UserAchievement.user_id == current_user.id,
            UserAchievement.achievement_id == achievement.id
        )
    )
    progress_result = await db.execute(progress_query)
    user_achievement = progress_result.scalar_one_or_none()

    if not user_achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement progress not found"
        )

    return UserAchievementResponse(
        id=str(user_achievement.id),
        achievement=AchievementResponse.model_validate(achievement),
        progress=user_achievement.progress,
        target=user_achievement.target,
        progress_percentage=user_achievement.progress_percentage,
        is_unlocked=user_achievement.is_unlocked,
        is_claimed=user_achievement.is_claimed,
        unlocked_at=user_achievement.unlocked_at,
        claimed_at=user_achievement.claimed_at
    )


@router.post("/achievements/claim")
async def claim_achievement(
    request: ClaimAchievementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Claim reward for completed achievement"""

    # Get user achievement
    user_achievement_query = select(UserAchievement, Achievement).join(
        Achievement, UserAchievement.achievement_id == Achievement.id
    ).where(
        and_(
            UserAchievement.user_id == current_user.id,
            UserAchievement.achievement_id == uuid.UUID(request.achievement_id)
        )
    )
    result = await db.execute(user_achievement_query)
    achievement_data = result.one_or_none()

    if not achievement_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )

    user_achievement, achievement = achievement_data

    # Check if unlocked
    if not user_achievement.is_unlocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Achievement not yet unlocked"
        )

    # Check if already claimed
    if user_achievement.is_claimed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Achievement reward already claimed"
        )

    # Credit reward
    reward_amount = 0
    credited_wallet = None

    if achievement.reward_amount > 0:
        # Get bonus wallet
        wallet_query = select(Wallet).where(
            and_(
                Wallet.user_id == current_user.id,
                Wallet.wallet_type == "bonus"
            )
        )
        wallet_result = await db.execute(wallet_query)
        bonus_wallet = wallet_result.scalar_one_or_none()

        if bonus_wallet:
            bonus_wallet.balance += achievement.reward_amount
            reward_amount = achievement.reward_amount
            credited_wallet = "bonus"

            # Create transaction
            transaction = Transaction(
                user_id=current_user.id,
                wallet_id=bonus_wallet.id,
                transaction_type="credit",
                amount=achievement.reward_amount,
                category="reward",
                status="completed",
                description=f"Achievement reward: {achievement.name}"
            )
            db.add(transaction)

    # Add XP if coins reward
    if achievement.reward_coins > 0:
        level_query = select(UserLevel).where(UserLevel.user_id == current_user.id)
        level_result = await db.execute(level_query)
        user_level = level_result.scalar_one_or_none()

        if user_level:
            user_level.experience_points += achievement.reward_coins
            user_level.total_xp_earned += achievement.reward_coins

            # Recalculate level
            level, xp_current, xp_needed, progress = reward_calculator.calculate_level_from_xp(
                user_level.total_xp_earned
            )
            user_level.current_level = level
            user_level.experience_points = xp_current
            user_level.points_to_next_level = xp_needed
            user_level.level_progress_percentage = progress
            user_level.perks_unlocked = reward_calculator.get_level_perks(level)

            if level > user_level.highest_level_reached:
                user_level.highest_level_reached = level
                user_level.last_level_up_at = datetime.utcnow()

    # Mark as claimed
    user_achievement.is_claimed = True
    user_achievement.claimed_at = datetime.utcnow()

    # Create reward transaction record
    reward_transaction = RewardTransaction(
        user_id=current_user.id,
        reward_type="achievement",
        reward_source_id=achievement.id,
        reward_source_type="achievement",
        reward_amount=achievement.reward_amount,
        reward_coins=achievement.reward_coins,
        reward_description=f"Achievement: {achievement.name}",
        credited_to_wallet=credited_wallet,
        status="credited",
        credited_at=datetime.utcnow()
    )
    db.add(reward_transaction)

    await db.commit()

    return {
        "success": True,
        "achievement_name": achievement.name,
        "reward_amount": reward_amount / 100 if reward_amount > 0 else 0,
        "reward_coins": achievement.reward_coins,
        "reward_badge": achievement.reward_badge,
        "reward_title": achievement.reward_title,
        "message": f"Claimed reward for {achievement.name}!"
    }


@router.get("/achievements/categories")
async def get_achievement_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get list of achievement categories"""

    query = select(Achievement.category, func.count(Achievement.id)).where(
        Achievement.is_active == True
    ).group_by(Achievement.category)

    result = await db.execute(query)
    categories = result.all()

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in categories
        ]
    }


# ============================================================================
# Daily Bonus Endpoints
# ============================================================================

@router.get("/daily-bonus/status", response_model=DailyBonusResponse)
async def get_daily_bonus_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily bonus status for current user"""

    # Get or create daily bonus record
    query = select(DailyBonus).where(DailyBonus.user_id == current_user.id)
    result = await db.execute(query)
    daily_bonus = result.scalar_one_or_none()

    if not daily_bonus:
        daily_bonus = DailyBonus(
            user_id=current_user.id,
            current_streak=0,
            longest_streak=0,
            total_claims=0,
            next_bonus_day=1,
            can_claim_today=True,
            streak_broken=False
        )
        db.add(daily_bonus)
        await db.commit()
        await db.refresh(daily_bonus)

    # Calculate if can claim today
    can_claim, amount_paise, next_day = reward_calculator.calculate_daily_bonus(
        daily_bonus.current_streak,
        daily_bonus.last_claim_date
    )

    # Get bonus calendar
    bonus_calendar = reward_calculator.get_daily_bonus_calendar(daily_bonus.current_streak)

    return DailyBonusResponse(
        can_claim_today=can_claim,
        current_streak=daily_bonus.current_streak,
        longest_streak=daily_bonus.longest_streak,
        total_claims=daily_bonus.total_claims,
        last_claim_date=daily_bonus.last_claim_date,
        last_claim_amount=daily_bonus.last_claim_amount / 100 if daily_bonus.last_claim_amount > 0 else 0,
        next_bonus_day=next_day,
        next_bonus_amount=amount_paise / 100,
        streak_broken=daily_bonus.streak_broken,
        bonus_calendar=bonus_calendar
    )


@router.post("/daily-bonus/claim", response_model=ClaimDailyBonusResponse)
async def claim_daily_bonus(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Claim daily bonus"""

    # Get daily bonus record
    query = select(DailyBonus).where(DailyBonus.user_id == current_user.id)
    result = await db.execute(query)
    daily_bonus = result.scalar_one_or_none()

    if not daily_bonus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily bonus record not found"
        )

    # Check if can claim
    can_claim, amount_paise, next_day = reward_calculator.calculate_daily_bonus(
        daily_bonus.current_streak,
        daily_bonus.last_claim_date
    )

    if not can_claim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daily bonus already claimed today"
        )

    # Get bonus wallet
    wallet_query = select(Wallet).where(
        and_(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "bonus"
        )
    )
    wallet_result = await db.execute(wallet_query)
    bonus_wallet = wallet_result.scalar_one_or_none()

    if not bonus_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bonus wallet not found"
        )

    # Credit bonus
    bonus_wallet.balance += amount_paise

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        wallet_id=bonus_wallet.id,
        transaction_type="credit",
        amount=amount_paise,
        category="reward",
        status="completed",
        description=f"Daily bonus - Day {next_day}"
    )
    db.add(transaction)

    # Update daily bonus record
    daily_bonus.current_streak += 1
    daily_bonus.total_claims += 1
    daily_bonus.last_claim_date = datetime.utcnow()
    daily_bonus.last_claim_amount = amount_paise
    daily_bonus.next_bonus_day = (next_day % 7) + 1
    daily_bonus.can_claim_today = False
    daily_bonus.streak_broken = False

    if daily_bonus.current_streak > daily_bonus.longest_streak:
        daily_bonus.longest_streak = daily_bonus.current_streak

    # Get next bonus info
    _, next_amount_paise, next_bonus_day = reward_calculator.calculate_daily_bonus(
        daily_bonus.current_streak,
        datetime.utcnow()
    )

    # Create reward transaction record
    reward_transaction = RewardTransaction(
        user_id=current_user.id,
        reward_type="daily_bonus",
        reward_source_type="daily_bonus",
        reward_amount=amount_paise,
        reward_description=f"Daily bonus - Day {next_day}",
        credited_to_wallet="bonus",
        status="credited",
        credited_at=datetime.utcnow()
    )
    db.add(reward_transaction)

    await db.commit()

    return ClaimDailyBonusResponse(
        success=True,
        bonus_amount=amount_paise / 100,
        new_streak=daily_bonus.current_streak,
        next_bonus_day=next_bonus_day,
        next_bonus_amount=next_amount_paise / 100,
        message=f"Claimed Rs.{amount_paise / 100} daily bonus! Streak: {daily_bonus.current_streak} days"
    )


# ============================================================================
# Leaderboard Endpoints
# ============================================================================

@router.post("/leaderboards/query", response_model=LeaderboardResponse)
async def query_leaderboard(
    request: LeaderboardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Query leaderboard with filters"""

    # Get period dates
    period_start, period_end = leaderboard_calculator.get_period_dates(request.board_type)

    # Build query
    query = (
        select(Leaderboard, User)
        .join(User, Leaderboard.user_id == User.id)
        .where(
            and_(
                Leaderboard.board_type == request.board_type,
                Leaderboard.category == request.category,
                Leaderboard.period_start == period_start
            )
        )
        .order_by(Leaderboard.rank)
        .limit(request.limit)
        .offset(request.offset)
    )

    result = await db.execute(query)
    leaderboard_data = result.all()

    # Get total count
    count_query = select(func.count(Leaderboard.id)).where(
        and_(
            Leaderboard.board_type == request.board_type,
            Leaderboard.category == request.category,
            Leaderboard.period_start == period_start
        )
    )
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # Build response
    entries = []
    current_user_rank = None
    current_user_entry = None

    for leaderboard, user in leaderboard_data:
        is_current = user.id == current_user.id

        entry = LeaderboardEntryResponse(
            rank=leaderboard.rank,
            user_id=str(user.id),
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            score=leaderboard.score,
            games_played=leaderboard.games_played,
            games_won=leaderboard.games_won,
            total_winnings=leaderboard.total_winnings / 100,
            rank_change=leaderboard.rank_change,
            is_current_user=is_current
        )

        entries.append(entry)

        if is_current:
            current_user_rank = leaderboard.rank
            current_user_entry = entry

    # If current user not in results, find their rank
    if not current_user_rank:
        user_rank_query = select(Leaderboard).where(
            and_(
                Leaderboard.user_id == current_user.id,
                Leaderboard.board_type == request.board_type,
                Leaderboard.category == request.category,
                Leaderboard.period_start == period_start
            )
        )
        user_rank_result = await db.execute(user_rank_query)
        user_leaderboard = user_rank_result.scalar_one_or_none()

        if user_leaderboard:
            current_user_rank = user_leaderboard.rank
            current_user_entry = LeaderboardEntryResponse(
                rank=user_leaderboard.rank,
                user_id=str(current_user.id),
                username=current_user.username,
                display_name=current_user.display_name,
                avatar_url=current_user.avatar_url,
                score=user_leaderboard.score,
                games_played=user_leaderboard.games_played,
                games_won=user_leaderboard.games_won,
                total_winnings=user_leaderboard.total_winnings / 100,
                rank_change=user_leaderboard.rank_change,
                is_current_user=True
            )

    return LeaderboardResponse(
        board_type=request.board_type,
        category=request.category,
        period_start=period_start,
        period_end=period_end,
        entries=entries,
        total_count=total_count,
        current_user_rank=current_user_rank,
        current_user_entry=current_user_entry
    )


@router.get("/leaderboards/my-rank")
async def get_my_rank(
    board_type: str = "weekly",
    category: str = "winnings",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's rank in leaderboard"""

    # Get period dates
    period_start, period_end = leaderboard_calculator.get_period_dates(board_type)

    # Find user's leaderboard entry
    query = select(Leaderboard).where(
        and_(
            Leaderboard.user_id == current_user.id,
            Leaderboard.board_type == board_type,
            Leaderboard.category == category,
            Leaderboard.period_start == period_start
        )
    )
    result = await db.execute(query)
    leaderboard = result.scalar_one_or_none()

    if not leaderboard:
        return {
            "rank": None,
            "message": "Not ranked yet in this leaderboard"
        }

    return {
        "rank": leaderboard.rank,
        "previous_rank": leaderboard.previous_rank,
        "rank_change": leaderboard.rank_change,
        "score": leaderboard.score,
        "games_played": leaderboard.games_played,
        "games_won": leaderboard.games_won,
        "total_winnings": leaderboard.total_winnings / 100,
        "period_start": period_start,
        "period_end": period_end
    }


@router.get("/leaderboards/top")
async def get_top_players(
    board_type: str = "weekly",
    category: str = "winnings",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get top players in leaderboard"""

    # Get period dates
    period_start, period_end = leaderboard_calculator.get_period_dates(board_type)

    # Query top players
    query = (
        select(Leaderboard, User)
        .join(User, Leaderboard.user_id == User.id)
        .where(
            and_(
                Leaderboard.board_type == board_type,
                Leaderboard.category == category,
                Leaderboard.period_start == period_start
            )
        )
        .order_by(Leaderboard.rank)
        .limit(limit)
    )

    result = await db.execute(query)
    leaderboard_data = result.all()

    # Build response
    top_players = []
    for leaderboard, user in leaderboard_data:
        top_players.append({
            "rank": leaderboard.rank,
            "username": user.username,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "score": leaderboard.score,
            "rank_change": leaderboard.rank_change
        })

    return {
        "board_type": board_type,
        "category": category,
        "period_start": period_start,
        "period_end": period_end,
        "top_players": top_players
    }


# ============================================================================
# Level/XP Endpoints
# ============================================================================

@router.get("/level/status", response_model=UserLevelResponse)
async def get_level_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user level and XP status"""

    # Get or create user level
    query = select(UserLevel).where(UserLevel.user_id == current_user.id)
    result = await db.execute(query)
    user_level = result.scalar_one_or_none()

    if not user_level:
        user_level = UserLevel(
            user_id=current_user.id,
            current_level=1,
            experience_points=0,
            points_to_next_level=100,
            level_progress_percentage=0.0,
            perks_unlocked=[],
            total_xp_earned=0,
            highest_level_reached=1
        )
        db.add(user_level)
        await db.commit()
        await db.refresh(user_level)

    return UserLevelResponse.model_validate(user_level)


@router.post("/level/add-xp")
async def add_experience(
    request: AddExperienceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add experience points (internal endpoint for game completion)"""

    # Verify user_id matches current user (or is admin)
    if str(current_user.id) != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only add XP to your own account"
        )

    # Get user level
    query = select(UserLevel).where(UserLevel.user_id == current_user.id)
    result = await db.execute(query)
    user_level = result.scalar_one_or_none()

    if not user_level:
        user_level = UserLevel(
            user_id=current_user.id,
            current_level=1,
            experience_points=0,
            points_to_next_level=100,
            total_xp_earned=0,
            highest_level_reached=1
        )
        db.add(user_level)

    # Add XP
    old_level = user_level.current_level
    user_level.total_xp_earned += request.points

    # Recalculate level
    level, xp_current, xp_needed, progress = reward_calculator.calculate_level_from_xp(
        user_level.total_xp_earned
    )

    user_level.current_level = level
    user_level.experience_points = xp_current
    user_level.points_to_next_level = xp_needed
    user_level.level_progress_percentage = progress
    user_level.perks_unlocked = reward_calculator.get_level_perks(level)

    leveled_up = level > old_level

    if leveled_up:
        user_level.highest_level_reached = max(level, user_level.highest_level_reached)
        user_level.last_level_up_at = datetime.utcnow()

    await db.commit()

    return {
        "success": True,
        "points_added": request.points,
        "current_level": level,
        "leveled_up": leveled_up,
        "new_perks": user_level.perks_unlocked if leveled_up else [],
        "progress_percentage": progress,
        "message": f"Level up to {level}!" if leveled_up else f"Added {request.points} XP"
    }


# ============================================================================
# Promo Code Endpoints
# ============================================================================

@router.post("/promo/validate", response_model=PromoCodeResponse)
async def validate_promo_code(
    request: ValidatePromoCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate promo code for user"""

    # Find promo code
    query = select(PromoCode).where(
        and_(
            PromoCode.code == request.promo_code,
            PromoCode.is_active == True
        )
    )
    result = await db.execute(query)
    promo = result.scalar_one_or_none()

    if not promo:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message="Invalid promo code"
        )

    # Check validity dates
    now = datetime.utcnow()
    if promo.valid_from and now < promo.valid_from:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message="Promo code not yet valid"
        )

    if promo.valid_until and now > promo.valid_until:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message="Promo code expired"
        )

    # Check total uses
    if promo.max_total_uses and promo.current_uses >= promo.max_total_uses:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message="Promo code usage limit reached"
        )

    # Check user usage
    usage_query = select(func.count(PromoCodeUsage.id)).where(
        and_(
            PromoCodeUsage.user_id == current_user.id,
            PromoCodeUsage.promo_code_id == promo.id
        )
    )
    usage_result = await db.execute(usage_query)
    user_usage_count = usage_result.scalar()

    if user_usage_count >= promo.max_uses_per_user:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message="You have already used this promo code"
        )

    # Calculate discount
    is_valid, discount_amount, message = reward_calculator.calculate_promo_discount(
        promo.promo_type,
        promo.discount_type,
        promo.discount_value,
        request.amount,
        promo.max_discount / 100 if promo.max_discount else None,
        promo.min_deposit / 100 if promo.min_deposit else None
    )

    if not is_valid:
        return PromoCodeResponse(
            valid=False,
            promo_code=request.promo_code,
            message=message
        )

    uses_remaining = None
    if promo.max_total_uses:
        uses_remaining = promo.max_total_uses - promo.current_uses

    return PromoCodeResponse(
        valid=True,
        promo_code=promo.code,
        name=promo.name,
        description=promo.description,
        promo_type=promo.promo_type,
        discount_type=promo.discount_type,
        discount_value=promo.discount_value,
        discount_amount=discount_amount,
        max_discount=promo.max_discount / 100 if promo.max_discount else None,
        min_deposit=promo.min_deposit / 100 if promo.min_deposit else None,
        uses_remaining=uses_remaining,
        message=message
    )


@router.post("/admin/promo/create", response_model=PromoCodeDetailResponse)
async def create_promo_code(
    request: CreatePromoCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new promo code (admin only)"""

    # TODO: Add admin role check
    # For now, any authenticated user can create (should be restricted in production)

    # Check if code already exists
    existing_query = select(PromoCode).where(PromoCode.code == request.code)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo code already exists"
        )

    # Create promo code
    promo = PromoCode(
        code=request.code,
        name=request.name,
        description=request.description,
        promo_type=request.promo_type,
        discount_type=request.discount_type,
        discount_value=request.discount_value,
        max_discount=int(request.max_discount * 100) if request.max_discount else None,
        min_deposit=int(request.min_deposit * 100) if request.min_deposit else None,
        max_uses_per_user=request.max_uses_per_user,
        max_total_uses=request.max_total_uses,
        current_uses=0,
        valid_from=request.valid_from,
        valid_until=request.valid_until,
        is_active=True,
        applicable_to=request.applicable_to,
        created_by=current_user.id
    )

    db.add(promo)
    await db.commit()
    await db.refresh(promo)

    return PromoCodeDetailResponse.model_validate(promo)


@router.get("/admin/promo/list")
async def list_promo_codes(
    active_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all promo codes (admin only)"""

    # TODO: Add admin role check

    query = select(PromoCode)

    if active_only:
        query = query.where(PromoCode.is_active == True)

    query = query.order_by(desc(PromoCode.created_at)).limit(limit).offset(offset)

    result = await db.execute(query)
    promos = result.scalars().all()

    return {
        "promo_codes": [PromoCodeDetailResponse.model_validate(p) for p in promos],
        "total_count": len(promos)
    }


@router.put("/admin/promo/update/{promo_id}")
async def update_promo_code(
    promo_id: str,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update promo code (admin only)"""

    # TODO: Add admin role check

    query = select(PromoCode).where(PromoCode.id == uuid.UUID(promo_id))
    result = await db.execute(query)
    promo = result.scalar_one_or_none()

    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )

    if is_active is not None:
        promo.is_active = is_active

    await db.commit()

    return {"success": True, "message": "Promo code updated"}


# ============================================================================
# Reward History Endpoints
# ============================================================================

@router.post("/history", response_model=RewardHistoryResponse)
async def get_reward_history(
    request: RewardHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reward transaction history"""

    query = select(RewardTransaction).where(
        RewardTransaction.user_id == current_user.id
    )

    if request.reward_type:
        query = query.where(RewardTransaction.reward_type == request.reward_type)

    query = query.order_by(desc(RewardTransaction.created_at))
    query = query.limit(request.limit).offset(request.offset)

    result = await db.execute(query)
    rewards = result.scalars().all()

    # Get totals
    total_query = select(
        func.count(RewardTransaction.id),
        func.sum(RewardTransaction.reward_amount),
        func.sum(RewardTransaction.reward_coins)
    ).where(RewardTransaction.user_id == current_user.id)

    if request.reward_type:
        total_query = total_query.where(RewardTransaction.reward_type == request.reward_type)

    total_result = await db.execute(total_query)
    total_count, total_amount, total_coins = total_result.one()

    return RewardHistoryResponse(
        rewards=[RewardTransactionResponse.model_validate(r) for r in rewards],
        total_count=total_count or 0,
        total_amount=(total_amount or 0) / 100,
        total_coins=total_coins or 0
    )


@router.get("/dashboard", response_model=RewardsDashboardResponse)
async def get_rewards_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get combined rewards dashboard data"""

    # Get daily bonus
    daily_bonus_data = await get_daily_bonus_status(current_user, db)

    # Get referral stats
    referral_stats = await get_referral_stats(current_user, db)

    # Get level
    level_data = await get_level_status(current_user, db)

    # Get achievement summary
    achievements = await get_achievements_list(current_user=current_user, db=db)
    achievements_summary = {
        "total": achievements.total_achievements,
        "unlocked": achievements.unlocked_count,
        "completion_percentage": achievements.completion_percentage,
        "total_points": achievements.total_points_earned
    }

    # Get recent rewards
    recent_query = select(RewardTransaction).where(
        RewardTransaction.user_id == current_user.id
    ).order_by(desc(RewardTransaction.created_at)).limit(5)

    recent_result = await db.execute(recent_query)
    recent_rewards_data = recent_result.scalars().all()
    recent_rewards = [RewardTransactionResponse.model_validate(r) for r in recent_rewards_data]

    # Get leaderboard rank
    leaderboard_query = select(Leaderboard).where(
        and_(
            Leaderboard.user_id == current_user.id,
            Leaderboard.board_type == "weekly",
            Leaderboard.category == "winnings"
        )
    ).order_by(desc(Leaderboard.period_start)).limit(1)

    leaderboard_result = await db.execute(leaderboard_query)
    leaderboard = leaderboard_result.scalar_one_or_none()
    leaderboard_rank = leaderboard.rank if leaderboard else None

    return RewardsDashboardResponse(
        daily_bonus=daily_bonus_data,
        referral_stats=referral_stats,
        level=level_data,
        achievements_summary=achievements_summary,
        recent_rewards=recent_rewards,
        leaderboard_rank=leaderboard_rank
    )
