"""Phase 4: Games System

Revision ID: 003
Revises: 002
Create Date: 2025-11-16 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create games table
    op.create_table(
        'games',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('min_players', sa.Integer, default=2),
        sa.Column('max_players', sa.Integer, default=4),
        sa.Column('avg_duration_minutes', sa.Integer, default=10),
        sa.Column('difficulty_level', sa.String(20), default='medium'),
        sa.Column('min_entry_fee', sa.Integer, default=0),
        sa.Column('max_entry_fee', sa.Integer, nullable=True),
        sa.Column('default_entry_fee', sa.Integer, default=10000),
        sa.Column('prize_distribution', postgresql.JSONB, default={}, nullable=True),
        sa.Column('rules', postgresql.JSONB, default={}, nullable=True),
        sa.Column('game_config', postgresql.JSONB, default={}, nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('banner_url', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_featured', sa.Boolean, default=False),
        sa.Column('is_skill_based', sa.Boolean, default=True),
        sa.Column('total_sessions_played', sa.Integer, default=0),
        sa.Column('total_players', sa.Integer, default=0),
        sa.Column('total_prize_distributed', sa.Integer, default=0),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for games
    op.create_index('idx_games_category', 'games', ['category'])
    op.create_index('idx_games_active', 'games', ['is_active'])
    op.create_index('idx_games_featured', 'games', ['is_featured'])

    # Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_code', sa.String(10), unique=True, nullable=False, index=True),
        sa.Column('session_type', sa.String(20), nullable=False),
        sa.Column('entry_fee', sa.Integer, nullable=False),
        sa.Column('total_prize_pool', sa.Integer, default=0),
        sa.Column('max_players', sa.Integer, nullable=False),
        sa.Column('current_players', sa.Integer, default=0),
        sa.Column('min_players_to_start', sa.Integer, default=2),
        sa.Column('status', sa.String(20), default='waiting', nullable=False),
        sa.Column('game_state', postgresql.JSONB, default={}, nullable=True),
        sa.Column('current_turn_player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('turn_number', sa.Integer, default=0),
        sa.Column('turn_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('winning_amount', sa.Integer, default=0),
        sa.Column('result_data', postgresql.JSONB, default={}, nullable=True),
        sa.Column('is_private', sa.Boolean, default=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('auto_start', sa.Boolean, default=True),
        sa.Column('allow_spectators', sa.Boolean, default=True),
        sa.Column('platform_fee_percentage', sa.Float, default=5.0),
        sa.Column('platform_fee_amount', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for game_sessions
    op.create_index('idx_game_sessions_game_id', 'game_sessions', ['game_id'])
    op.create_index('idx_game_sessions_status', 'game_sessions', ['status'])
    op.create_index('idx_game_sessions_session_code', 'game_sessions', ['session_code'])
    op.create_index('idx_game_sessions_created_at', 'game_sessions', ['created_at'])

    # Create game_participants table
    op.create_table(
        'game_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_position', sa.Integer, nullable=False),
        sa.Column('player_color', sa.String(20), nullable=True),
        sa.Column('player_name', sa.String(100), nullable=False),
        sa.Column('entry_fee_paid', sa.Integer, nullable=False),
        sa.Column('entry_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id'), nullable=True),
        sa.Column('status', sa.String(20), default='joined', nullable=False),
        sa.Column('is_ready', sa.Boolean, default=False),
        sa.Column('is_spectator', sa.Boolean, default=False),
        sa.Column('final_rank', sa.Integer, nullable=True),
        sa.Column('final_score', sa.Integer, default=0),
        sa.Column('prize_won', sa.Integer, default=0),
        sa.Column('prize_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id'), nullable=True),
        sa.Column('xp_earned', sa.Integer, default=0),
        sa.Column('achievements_unlocked', postgresql.JSONB, default=[], nullable=True),
        sa.Column('moves_made', sa.Integer, default=0),
        sa.Column('total_play_time_seconds', sa.Integer, default=0),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Indexes for game_participants
    op.create_index('idx_game_participants_session_id', 'game_participants', ['session_id'])
    op.create_index('idx_game_participants_user_id', 'game_participants', ['user_id'])
    op.create_index('idx_game_participants_session_user', 'game_participants', ['session_id', 'user_id'], unique=True)
    op.create_index('idx_game_participants_status', 'game_participants', ['status'])

    # Create game_moves table
    op.create_table(
        'game_moves',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_participants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('move_number', sa.Integer, nullable=False),
        sa.Column('turn_number', sa.Integer, nullable=False),
        sa.Column('move_type', sa.String(30), nullable=False),
        sa.Column('move_data', postgresql.JSONB, nullable=False),
        sa.Column('is_valid', sa.Boolean, default=True),
        sa.Column('validation_message', sa.Text, nullable=True),
        sa.Column('state_before', postgresql.JSONB, nullable=True),
        sa.Column('state_after', postgresql.JSONB, nullable=True),
        sa.Column('time_taken_ms', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Indexes for game_moves
    op.create_index('idx_game_moves_session_id', 'game_moves', ['session_id'])
    op.create_index('idx_game_moves_participant_id', 'game_moves', ['participant_id'])
    op.create_index('idx_game_moves_user_id', 'game_moves', ['user_id'])
    op.create_index('idx_game_moves_created_at', 'game_moves', ['created_at'])

    # Create game_results table
    op.create_table(
        'game_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('winner_name', sa.String(100), nullable=True),
        sa.Column('winning_prize', sa.Integer, default=0),
        sa.Column('final_rankings', postgresql.JSONB, nullable=False),
        sa.Column('total_players', sa.Integer, nullable=False),
        sa.Column('total_moves', sa.Integer, default=0),
        sa.Column('total_duration_seconds', sa.Integer, default=0),
        sa.Column('total_prize_pool', sa.Integer, default=0),
        sa.Column('platform_fee_collected', sa.Integer, default=0),
        sa.Column('prizes_distributed', sa.Boolean, default=False),
        sa.Column('prize_distribution_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_xp_distributed', sa.Integer, default=0),
        sa.Column('achievements_triggered', postgresql.JSONB, default=[], nullable=True),
        sa.Column('leaderboard_updated', sa.Boolean, default=False),
        sa.Column('game_data', postgresql.JSONB, default={}, nullable=True),
        sa.Column('is_verified', sa.Boolean, default=True),
        sa.Column('fairplay_flags', postgresql.JSONB, default=[], nullable=True),
        sa.Column('game_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('game_ended_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Indexes for game_results
    op.create_index('idx_game_results_session_id', 'game_results', ['session_id'])
    op.create_index('idx_game_results_game_id', 'game_results', ['game_id'])
    op.create_index('idx_game_results_winner_id', 'game_results', ['winner_id'])
    op.create_index('idx_game_results_created_at', 'game_results', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('game_results')
    op.drop_table('game_moves')
    op.drop_table('game_participants')
    op.drop_table('game_sessions')
    op.drop_table('games')
