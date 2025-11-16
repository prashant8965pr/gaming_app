"""
Referral & Rewards Models
SQLAlchemy models for referral system, achievements, and rewards
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid


class Referral(Base):
    """User referral tracking table"""
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Referral code used
    referral_code = Column(String(10), nullable=False, index=True)

    # Referral status
    status = Column(String(20), default="pending", nullable=False)  # pending, completed, cancelled

    # Completion criteria
    is_kyc_completed = Column(Boolean, default=False)
    is_first_deposit_done = Column(Boolean, default=False)
    first_deposit_amount = Column(Integer, default=0)  # in paise
    is_first_game_played = Column(Boolean, default=False)

    # Rewards
    referrer_reward_given = Column(Boolean, default=False)
    referred_reward_given = Column(Boolean, default=False)
    referrer_reward_amount = Column(Integer, default=0)  # in paise
    referred_reward_amount = Column(Integer, default=0)  # in paise

    # Dates
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_referrals_referrer_id', 'referrer_id'),
        Index('idx_referrals_referred_id', 'referred_id'),
        Index('idx_referrals_status', 'status'),
        Index('idx_referrals_code', 'referral_code'),
    )


class Achievement(Base):
    """Predefined achievements table"""
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Achievement details
    code = Column(String(50), unique=True, nullable=False, index=True)  # FIRST_WIN, WIN_STREAK_5, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(30), nullable=False)  # gaming, social, milestone, special

    # Icon and visuals
    icon_url = Column(String(500), nullable=True)
    badge_color = Column(String(20), nullable=True)

    # Criteria
    criteria = Column(JSONB, nullable=True)  # JSON with achievement criteria
    # Example: {"type": "win_streak", "count": 5}
    # Example: {"type": "total_games", "count": 100}
    # Example: {"type": "referrals", "count": 10}

    # Rewards
    reward_type = Column(String(20), nullable=False)  # coins, bonus, badge, title
    reward_amount = Column(Integer, default=0)  # in paise for bonus
    reward_coins = Column(Integer, default=0)  # XP/coins
    reward_badge = Column(String(50), nullable=True)
    reward_title = Column(String(100), nullable=True)

    # Metadata
    difficulty = Column(String(20), default="easy")  # easy, medium, hard, legendary
    points = Column(Integer, default=10)  # Achievement points
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)  # Hidden achievements
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_achievements_category', 'category'),
        Index('idx_achievements_active', 'is_active'),
    )


class UserAchievement(Base):
    """User achievement progress and unlocks"""
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)

    # Progress
    progress = Column(Integer, default=0)  # Current progress
    target = Column(Integer, default=100)  # Target to complete
    progress_percentage = Column(Float, default=0.0)

    # Status
    is_unlocked = Column(Boolean, default=False)
    is_claimed = Column(Boolean, default=False)  # Reward claimed or not

    # Dates
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_user_achievements_user_id', 'user_id'),
        Index('idx_user_achievements_achievement_id', 'achievement_id'),
        Index('idx_user_achievements_unlocked', 'is_unlocked'),
        Index('idx_user_achievements_user_achievement', 'user_id', 'achievement_id', unique=True),
    )


class DailyBonus(Base):
    """Daily login bonus tracking"""
    __tablename__ = "daily_bonuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_claims = Column(Integer, default=0)

    # Last claim
    last_claim_date = Column(DateTime(timezone=True), nullable=True)
    last_claim_amount = Column(Integer, default=0)  # in paise

    # Next bonus
    next_bonus_day = Column(Integer, default=1)  # Day 1-7 in the cycle
    next_bonus_amount = Column(Integer, default=0)  # in paise

    # Status
    can_claim_today = Column(Boolean, default=True)
    streak_broken = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_daily_bonuses_user_id', 'user_id', unique=True),
        Index('idx_daily_bonuses_claim_date', 'last_claim_date'),
    )


class PromoCode(Base):
    """Promotional codes table"""
    __tablename__ = "promo_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Code details
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    # Type and discount
    promo_type = Column(String(20), nullable=False)  # deposit_bonus, cashback, free_entry, bonus_cash
    discount_type = Column(String(20), nullable=False)  # percentage, fixed, free
    discount_value = Column(Float, nullable=False)  # Percentage (10.0 for 10%) or Fixed amount

    # Limits
    max_discount = Column(Integer, nullable=True)  # Maximum discount in paise
    min_deposit = Column(Integer, nullable=True)  # Minimum deposit required in paise
    max_uses_per_user = Column(Integer, default=1)
    max_total_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)

    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    # Targeting
    applicable_to = Column(String(20), default="all")  # all, new_users, existing_users
    user_segment = Column(String(50), nullable=True)  # vip, regular, dormant, etc.

    # Creator
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Metadata
    metadata = Column(JSONB, default={}, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_promo_codes_active', 'is_active'),
        Index('idx_promo_codes_valid_from', 'valid_from'),
        Index('idx_promo_codes_valid_until', 'valid_until'),
    )


class PromoCodeUsage(Base):
    """Track promo code usage by users"""
    __tablename__ = "promo_code_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False)

    # Usage details
    promo_code = Column(String(50), nullable=False)
    order_amount = Column(Integer, nullable=False)  # Amount on which promo applied
    discount_amount = Column(Integer, nullable=False)  # Actual discount given
    bonus_credited = Column(Integer, default=0)  # Bonus amount credited

    # Transaction reference
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    payment_order_id = Column(UUID(as_uuid=True), ForeignKey("payment_orders.id", ondelete="SET NULL"), nullable=True)

    # Status
    status = Column(String(20), default="applied")  # applied, credited, failed, refunded

    # Timestamps
    used_at = Column(DateTime(timezone=True), server_default=func.now())
    credited_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_promo_usage_user_id', 'user_id'),
        Index('idx_promo_usage_code_id', 'promo_code_id'),
        Index('idx_promo_usage_used_at', 'used_at'),
    )


class Leaderboard(Base):
    """Leaderboard entries for different categories and time periods"""
    __tablename__ = "leaderboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Leaderboard type
    board_type = Column(String(30), nullable=False)  # daily, weekly, monthly, all_time
    category = Column(String(30), nullable=False)  # winnings, games_won, win_rate, referrals

    # Rankings
    rank = Column(Integer, nullable=False)
    previous_rank = Column(Integer, nullable=True)
    rank_change = Column(Integer, default=0)  # +5, -3, etc.

    # Scores
    score = Column(Float, nullable=False)  # The actual metric value
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_winnings = Column(Integer, default=0)  # in paise

    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Rewards
    reward_given = Column(Boolean, default=False)
    reward_amount = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_leaderboards_user_id', 'user_id'),
        Index('idx_leaderboards_type', 'board_type'),
        Index('idx_leaderboards_category', 'category'),
        Index('idx_leaderboards_rank', 'rank'),
        Index('idx_leaderboards_period', 'board_type', 'category', 'period_start'),
    )


class UserLevel(Base):
    """User level and experience points"""
    __tablename__ = "user_levels"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Level details
    current_level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    points_to_next_level = Column(Integer, default=100)

    # Progress
    level_progress_percentage = Column(Float, default=0.0)

    # Rewards unlocked at current level
    perks_unlocked = Column(JSONB, default=[], nullable=True)  # List of perks
    # Example: ["higher_withdrawal_limit", "priority_support", "exclusive_tournaments"]

    # Lifetime stats
    total_xp_earned = Column(Integer, default=0)
    highest_level_reached = Column(Integer, default=1)

    # Timestamps
    last_level_up_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RewardTransaction(Base):
    """Track all reward transactions (achievements, bonuses, referrals)"""
    __tablename__ = "reward_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Reward details
    reward_type = Column(String(30), nullable=False)  # achievement, daily_bonus, referral, level_up, promo
    reward_source_id = Column(UUID(as_uuid=True), nullable=True)  # ID of achievement, referral, etc.
    reward_source_type = Column(String(30), nullable=True)  # achievement, referral, daily_bonus, etc.

    # Amount
    reward_amount = Column(Integer, default=0)  # in paise
    reward_coins = Column(Integer, default=0)  # XP/coins
    reward_description = Column(Text, nullable=True)

    # Wallet type where credited
    credited_to_wallet = Column(String(20), nullable=True)  # cash, bonus, winnings

    # Status
    status = Column(String(20), default="pending")  # pending, credited, failed
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    credited_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_reward_transactions_user_id', 'user_id'),
        Index('idx_reward_transactions_type', 'reward_type'),
        Index('idx_reward_transactions_status', 'status'),
        Index('idx_reward_transactions_created_at', 'created_at'),
    )
