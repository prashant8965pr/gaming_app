"""
Referral & Rewards Schemas
Pydantic models for referral system, achievements, and rewards
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# Referral Schemas
# ============================================================================

class ReferralStatsResponse(BaseModel):
    """Referral statistics response"""
    total_referrals: int
    completed_referrals: int
    pending_referrals: int
    total_earnings: float  # in rupees
    referral_code: str
    referral_link: str

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    """Single referral response"""
    id: str
    referred_username: str
    referred_display_name: Optional[str]
    status: str
    is_kyc_completed: bool
    is_first_deposit_done: bool
    first_deposit_amount: float
    referrer_reward_given: bool
    referrer_reward_amount: float
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReferralListResponse(BaseModel):
    """List of referrals response"""
    referrals: List[ReferralResponse]
    total_count: int
    statistics: ReferralStatsResponse


# ============================================================================
# Achievement Schemas
# ============================================================================

class AchievementResponse(BaseModel):
    """Achievement details response"""
    id: str
    code: str
    name: str
    description: Optional[str]
    category: str
    icon_url: Optional[str]
    badge_color: Optional[str]
    difficulty: str
    points: int
    reward_type: str
    reward_amount: float = 0.0
    reward_coins: int = 0
    reward_badge: Optional[str]
    reward_title: Optional[str]
    is_hidden: bool

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    """User achievement progress response"""
    id: str
    achievement: AchievementResponse
    progress: int
    target: int
    progress_percentage: float
    is_unlocked: bool
    is_claimed: bool
    unlocked_at: Optional[datetime]
    claimed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ClaimAchievementRequest(BaseModel):
    """Request to claim achievement reward"""
    achievement_id: str = Field(..., example="uuid")


class AchievementListResponse(BaseModel):
    """List of achievements response"""
    achievements: List[UserAchievementResponse]
    total_achievements: int
    unlocked_count: int
    locked_count: int
    total_points_earned: int
    completion_percentage: float


# ============================================================================
# Daily Bonus Schemas
# ============================================================================

class DailyBonusResponse(BaseModel):
    """Daily bonus status response"""
    can_claim_today: bool
    current_streak: int
    longest_streak: int
    total_claims: int
    last_claim_date: Optional[datetime]
    last_claim_amount: float
    next_bonus_day: int
    next_bonus_amount: float
    streak_broken: bool
    bonus_calendar: List[Dict[str, Any]]  # 7-day calendar with amounts

    class Config:
        from_attributes = True


class ClaimDailyBonusResponse(BaseModel):
    """Response after claiming daily bonus"""
    success: bool
    bonus_amount: float
    new_streak: int
    next_bonus_day: int
    next_bonus_amount: float
    message: str


# ============================================================================
# Promo Code Schemas
# ============================================================================

class ValidatePromoCodeRequest(BaseModel):
    """Request to validate promo code"""
    promo_code: str = Field(..., min_length=1, max_length=50, example="WELCOME100")
    amount: float = Field(..., ge=0, example=500.0)

    @validator('promo_code')
    def validate_promo_code(cls, v):
        return v.upper().strip()


class PromoCodeResponse(BaseModel):
    """Promo code validation response"""
    valid: bool
    promo_code: str
    name: Optional[str]
    description: Optional[str]
    promo_type: Optional[str]
    discount_type: Optional[str]
    discount_value: Optional[float]
    discount_amount: Optional[float]
    max_discount: Optional[float]
    min_deposit: Optional[float]
    uses_remaining: Optional[int]
    message: str


class CreatePromoCodeRequest(BaseModel):
    """Admin request to create promo code"""
    code: str = Field(..., min_length=3, max_length=50, example="NEWYEAR50")
    name: Optional[str] = Field(None, max_length=200, example="New Year Offer")
    description: Optional[str] = Field(None, example="Get 50% bonus on first deposit")
    promo_type: str = Field(..., example="deposit_bonus")
    discount_type: str = Field(..., example="percentage")
    discount_value: float = Field(..., example=50.0)
    max_discount: Optional[float] = Field(None, example=1000.0)
    min_deposit: Optional[float] = Field(None, example=100.0)
    max_uses_per_user: int = Field(default=1, example=1)
    max_total_uses: Optional[int] = Field(None, example=1000)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_to: str = Field(default="all", example="all")

    @validator('code')
    def validate_code(cls, v):
        # Convert to uppercase and remove spaces
        code = v.upper().strip().replace(' ', '')
        if not code.isalnum():
            raise ValueError('Promo code must be alphanumeric')
        return code

    @validator('promo_type')
    def validate_promo_type(cls, v):
        allowed_types = ['deposit_bonus', 'cashback', 'free_entry', 'bonus_cash']
        if v not in allowed_types:
            raise ValueError(f'Invalid promo type. Must be one of: {", ".join(allowed_types)}')
        return v

    @validator('discount_type')
    def validate_discount_type(cls, v):
        allowed_types = ['percentage', 'fixed', 'free']
        if v not in allowed_types:
            raise ValueError(f'Invalid discount type. Must be one of: {", ".join(allowed_types)}')
        return v


class PromoCodeDetailResponse(BaseModel):
    """Detailed promo code response for admin"""
    id: str
    code: str
    name: Optional[str]
    description: Optional[str]
    promo_type: str
    discount_type: str
    discount_value: float
    max_discount: Optional[float]
    min_deposit: Optional[float]
    max_uses_per_user: int
    max_total_uses: Optional[int]
    current_uses: int
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    is_active: bool
    applicable_to: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Leaderboard Schemas
# ============================================================================

class LeaderboardEntryResponse(BaseModel):
    """Single leaderboard entry"""
    rank: int
    user_id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    score: float
    games_played: int
    games_won: int
    total_winnings: float
    rank_change: int
    is_current_user: bool = False

    class Config:
        from_attributes = True


class LeaderboardRequest(BaseModel):
    """Request for leaderboard data"""
    board_type: str = Field(default="weekly", example="weekly")
    category: str = Field(default="winnings", example="winnings")
    limit: int = Field(default=100, ge=1, le=500, example=100)
    offset: int = Field(default=0, ge=0, example=0)

    @validator('board_type')
    def validate_board_type(cls, v):
        allowed_types = ['daily', 'weekly', 'monthly', 'all_time']
        if v not in allowed_types:
            raise ValueError(f'Invalid board type. Must be one of: {", ".join(allowed_types)}')
        return v

    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['winnings', 'games_won', 'win_rate', 'referrals']
        if v not in allowed_categories:
            raise ValueError(f'Invalid category. Must be one of: {", ".join(allowed_categories)}')
        return v


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    board_type: str
    category: str
    period_start: datetime
    period_end: datetime
    entries: List[LeaderboardEntryResponse]
    total_count: int
    current_user_rank: Optional[int]
    current_user_entry: Optional[LeaderboardEntryResponse]


# ============================================================================
# User Level Schemas
# ============================================================================

class UserLevelResponse(BaseModel):
    """User level and progress response"""
    current_level: int
    experience_points: int
    points_to_next_level: int
    level_progress_percentage: float
    total_xp_earned: int
    highest_level_reached: int
    perks_unlocked: List[str]
    last_level_up_at: Optional[datetime]

    class Config:
        from_attributes = True


class AddExperienceRequest(BaseModel):
    """Request to add experience points (for game completion, etc.)"""
    user_id: str = Field(..., example="uuid")
    points: int = Field(..., ge=1, le=10000, example=50)
    source: str = Field(..., example="game_win")


# ============================================================================
# Reward Transaction Schemas
# ============================================================================

class RewardTransactionResponse(BaseModel):
    """Reward transaction response"""
    id: str
    reward_type: str
    reward_amount: float
    reward_coins: int
    reward_description: Optional[str]
    status: str
    credited_to_wallet: Optional[str]
    credited_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RewardHistoryRequest(BaseModel):
    """Request for reward history"""
    reward_type: Optional[str] = Field(None, example="achievement")
    limit: int = Field(default=50, ge=1, le=100, example=50)
    offset: int = Field(default=0, ge=0, example=0)


class RewardHistoryResponse(BaseModel):
    """Reward history response"""
    rewards: List[RewardTransactionResponse]
    total_count: int
    total_amount: float
    total_coins: int


# ============================================================================
# Combined Dashboard Schemas
# ============================================================================

class RewardsDashboardResponse(BaseModel):
    """Combined rewards dashboard data"""
    daily_bonus: DailyBonusResponse
    referral_stats: ReferralStatsResponse
    level: UserLevelResponse
    achievements_summary: Dict[str, Any]
    recent_rewards: List[RewardTransactionResponse]
    leaderboard_rank: Optional[int]
