"""Phase 3: Referral and Rewards System

Revision ID: 002
Revises: 001
Create Date: 2025-11-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create referrals table
    op.create_table(
        'referrals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('referrer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('referred_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('referral_code', sa.String(10), nullable=False, index=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('is_kyc_completed', sa.Boolean, default=False),
        sa.Column('is_first_deposit_done', sa.Boolean, default=False),
        sa.Column('first_deposit_amount', sa.Integer, default=0),
        sa.Column('is_first_game_played', sa.Boolean, default=False),
        sa.Column('referrer_reward_given', sa.Boolean, default=False),
        sa.Column('referred_reward_given', sa.Boolean, default=False),
        sa.Column('referrer_reward_amount', sa.Integer, default=0),
        sa.Column('referred_reward_amount', sa.Integer, default=0),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for referrals
    op.create_index('idx_referrals_referrer_id', 'referrals', ['referrer_id'])
    op.create_index('idx_referrals_referred_id', 'referrals', ['referred_id'])
    op.create_index('idx_referrals_status', 'referrals', ['status'])
    op.create_index('idx_referrals_code', 'referrals', ['referral_code'])

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('badge_color', sa.String(20), nullable=True),
        sa.Column('criteria', postgresql.JSONB, nullable=True),
        sa.Column('reward_type', sa.String(20), nullable=False),
        sa.Column('reward_amount', sa.Integer, default=0),
        sa.Column('reward_coins', sa.Integer, default=0),
        sa.Column('reward_badge', sa.String(50), nullable=True),
        sa.Column('reward_title', sa.String(100), nullable=True),
        sa.Column('difficulty', sa.String(20), default='easy'),
        sa.Column('points', sa.Integer, default=10),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_hidden', sa.Boolean, default=False),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for achievements
    op.create_index('idx_achievements_category', 'achievements', ['category'])
    op.create_index('idx_achievements_active', 'achievements', ['is_active'])

    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('progress', sa.Integer, default=0),
        sa.Column('target', sa.Integer, default=100),
        sa.Column('progress_percentage', sa.Float, default=0.0),
        sa.Column('is_unlocked', sa.Boolean, default=False),
        sa.Column('is_claimed', sa.Boolean, default=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for user_achievements
    op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])
    op.create_index('idx_user_achievements_unlocked', 'user_achievements', ['is_unlocked'])
    op.create_index('idx_user_achievements_user_achievement', 'user_achievements', ['user_id', 'achievement_id'], unique=True)

    # Create daily_bonuses table
    op.create_table(
        'daily_bonuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('current_streak', sa.Integer, default=0),
        sa.Column('longest_streak', sa.Integer, default=0),
        sa.Column('total_claims', sa.Integer, default=0),
        sa.Column('last_claim_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_claim_amount', sa.Integer, default=0),
        sa.Column('next_bonus_day', sa.Integer, default=1),
        sa.Column('next_bonus_amount', sa.Integer, default=0),
        sa.Column('can_claim_today', sa.Boolean, default=True),
        sa.Column('streak_broken', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for daily_bonuses
    op.create_index('idx_daily_bonuses_user_id', 'daily_bonuses', ['user_id'], unique=True)
    op.create_index('idx_daily_bonuses_claim_date', 'daily_bonuses', ['last_claim_date'])

    # Create promo_codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('promo_type', sa.String(20), nullable=False),
        sa.Column('discount_type', sa.String(20), nullable=False),
        sa.Column('discount_value', sa.Float, nullable=False),
        sa.Column('max_discount', sa.Integer, nullable=True),
        sa.Column('min_deposit', sa.Integer, nullable=True),
        sa.Column('max_uses_per_user', sa.Integer, default=1),
        sa.Column('max_total_uses', sa.Integer, nullable=True),
        sa.Column('current_uses', sa.Integer, default=0),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('applicable_to', sa.String(20), default='all'),
        sa.Column('user_segment', sa.String(50), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('metadata', postgresql.JSONB, default={}, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for promo_codes
    op.create_index('idx_promo_codes_active', 'promo_codes', ['is_active'])
    op.create_index('idx_promo_codes_valid_from', 'promo_codes', ['valid_from'])
    op.create_index('idx_promo_codes_valid_until', 'promo_codes', ['valid_until'])

    # Create promo_code_usage table
    op.create_table(
        'promo_code_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('promo_code_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('promo_codes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('promo_code', sa.String(50), nullable=False),
        sa.Column('order_amount', sa.Integer, nullable=False),
        sa.Column('discount_amount', sa.Integer, nullable=False),
        sa.Column('bonus_credited', sa.Integer, default=0),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('payment_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payment_orders.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(20), default='applied'),
        sa.Column('used_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('credited_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Indexes for promo_code_usage
    op.create_index('idx_promo_usage_user_id', 'promo_code_usage', ['user_id'])
    op.create_index('idx_promo_usage_code_id', 'promo_code_usage', ['promo_code_id'])
    op.create_index('idx_promo_usage_used_at', 'promo_code_usage', ['used_at'])

    # Create leaderboards table
    op.create_table(
        'leaderboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('board_type', sa.String(30), nullable=False),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('rank', sa.Integer, nullable=False),
        sa.Column('previous_rank', sa.Integer, nullable=True),
        sa.Column('rank_change', sa.Integer, default=0),
        sa.Column('score', sa.Float, nullable=False),
        sa.Column('games_played', sa.Integer, default=0),
        sa.Column('games_won', sa.Integer, default=0),
        sa.Column('total_winnings', sa.Integer, default=0),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reward_given', sa.Boolean, default=False),
        sa.Column('reward_amount', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for leaderboards
    op.create_index('idx_leaderboards_user_id', 'leaderboards', ['user_id'])
    op.create_index('idx_leaderboards_type', 'leaderboards', ['board_type'])
    op.create_index('idx_leaderboards_category', 'leaderboards', ['category'])
    op.create_index('idx_leaderboards_rank', 'leaderboards', ['rank'])
    op.create_index('idx_leaderboards_period', 'leaderboards', ['board_type', 'category', 'period_start'])

    # Create user_levels table
    op.create_table(
        'user_levels',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('current_level', sa.Integer, default=1),
        sa.Column('experience_points', sa.Integer, default=0),
        sa.Column('points_to_next_level', sa.Integer, default=100),
        sa.Column('level_progress_percentage', sa.Float, default=0.0),
        sa.Column('perks_unlocked', postgresql.JSONB, default=[], nullable=True),
        sa.Column('total_xp_earned', sa.Integer, default=0),
        sa.Column('highest_level_reached', sa.Integer, default=1),
        sa.Column('last_level_up_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create reward_transactions table
    op.create_table(
        'reward_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reward_type', sa.String(30), nullable=False),
        sa.Column('reward_source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reward_source_type', sa.String(30), nullable=True),
        sa.Column('reward_amount', sa.Integer, default=0),
        sa.Column('reward_coins', sa.Integer, default=0),
        sa.Column('reward_description', sa.Text, nullable=True),
        sa.Column('credited_to_wallet', sa.String(20), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('credited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Indexes for reward_transactions
    op.create_index('idx_reward_transactions_user_id', 'reward_transactions', ['user_id'])
    op.create_index('idx_reward_transactions_type', 'reward_transactions', ['reward_type'])
    op.create_index('idx_reward_transactions_status', 'reward_transactions', ['status'])
    op.create_index('idx_reward_transactions_created_at', 'reward_transactions', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('reward_transactions')
    op.drop_table('user_levels')
    op.drop_table('leaderboards')
    op.drop_table('promo_code_usage')
    op.drop_table('promo_codes')
    op.drop_table('daily_bonuses')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('referrals')
