"""add tournament, token, and friends system

Revision ID: 006
Revises: 005
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Create tournaments table
    op.create_table(
        'tournaments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('games.id'), nullable=False),
        sa.Column('tournament_type', sa.String(50), default='single_elimination'),
        sa.Column('entry_fee', sa.Integer(), default=0),
        sa.Column('prize_pool', sa.Integer(), default=0),
        sa.Column('prize_distribution', postgresql.JSON()),
        sa.Column('max_participants', sa.Integer(), default=16),
        sa.Column('min_participants', sa.Integer(), default=4),
        sa.Column('current_participants', sa.Integer(), default=0),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime()),
        sa.Column('registration_start', sa.DateTime(), nullable=False),
        sa.Column('registration_end', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), default='upcoming'),
        sa.Column('bracket_data', postgresql.JSON()),
        sa.Column('rules', postgresql.JSON()),
        sa.Column('is_featured', sa.Boolean(), default=False),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create tournament_registrations table
    op.create_table(
        'tournament_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tournaments.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('registration_time', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('seed_number', sa.Integer()),
        sa.Column('status', sa.String(50), default='pending_payment'),
        sa.Column('payment_status', sa.String(50), default='pending'),
        sa.Column('payment_transaction_id', postgresql.UUID(as_uuid=True)),
        sa.Column('final_rank', sa.Integer()),
        sa.Column('prize_won', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint('tournament_id', 'user_id', name='unique_tournament_registration')
    )
    
    # Create tournament_matches table
    op.create_table(
        'tournament_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tournament_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tournaments.id'), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('match_number', sa.Integer(), nullable=False),
        sa.Column('player1_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('player2_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('score_data', postgresql.JSON()),
        sa.Column('game_session_id', postgresql.UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('scheduled_time', sa.DateTime()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('is_finals', sa.Boolean(), default=False),
        sa.Column('is_consolation', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create token_wallets table
    op.create_table(
        'token_wallets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('balance', sa.Integer(), default=0),
        sa.Column('total_earned', sa.Integer(), default=0),
        sa.Column('total_spent', sa.Integer(), default=0),
        sa.Column('last_daily_claim', sa.DateTime()),
        sa.Column('daily_claim_streak', sa.Integer(), default=0),
        sa.Column('ads_watched_today', sa.Integer(), default=0),
        sa.Column('last_ad_watch', sa.DateTime()),
        sa.Column('ads_reset_date', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create token_transactions table
    op.create_table(
        'token_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('wallet_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('token_wallets.id'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('related_id', postgresql.UUID(as_uuid=True)),
        sa.Column('metadata', postgresql.JSON()),
        sa.Column('balance_after', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    
    # Create token_packages table
    op.create_table(
        'token_packages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('tokens', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('bonus_tokens', sa.Integer(), default=0),
        sa.Column('discount_percentage', sa.Integer(), default=0),
        sa.Column('original_price', sa.Integer()),
        sa.Column('is_popular', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create friendships table
    op.create_table(
        'friendships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('friend_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(50), default='accepted'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('accepted_at', sa.DateTime()),
        sa.UniqueConstraint('user_id', 'friend_id', name='unique_friendship')
    )
    
    # Create friend_requests table
    op.create_table(
        'friend_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('responded_at', sa.DateTime()),
        sa.UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request')
    )
    
    # Create game_invitations table
    op.create_table(
        'game_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('game_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('game_sessions.id'), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('message', sa.Text()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('responded_at', sa.DateTime())
    )
    
    # Create indexes
    op.create_index('idx_tournaments_status', 'tournaments', ['status'])
    op.create_index('idx_tournaments_game', 'tournaments', ['game_id'])
    op.create_index('idx_tournaments_start_time', 'tournaments', ['start_time'])
    op.create_index('idx_tournament_registrations_user', 'tournament_registrations', ['user_id'])
    op.create_index('idx_tournament_registrations_tournament', 'tournament_registrations', ['tournament_id'])
    op.create_index('idx_tournament_matches_tournament', 'tournament_matches', ['tournament_id'])
    op.create_index('idx_token_transactions_user', 'token_transactions', ['user_id'])
    op.create_index('idx_token_transactions_wallet', 'token_transactions', ['wallet_id'])
    op.create_index('idx_friendships_user', 'friendships', ['user_id'])
    op.create_index('idx_friendships_friend', 'friendships', ['friend_id'])
    op.create_index('idx_friend_requests_receiver', 'friend_requests', ['receiver_id'])
    op.create_index('idx_friend_requests_sender', 'friend_requests', ['sender_id'])
    op.create_index('idx_game_invitations_receiver', 'game_invitations', ['receiver_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_game_invitations_receiver')
    op.drop_index('idx_friend_requests_sender')
    op.drop_index('idx_friend_requests_receiver')
    op.drop_index('idx_friendships_friend')
    op.drop_index('idx_friendships_user')
    op.drop_index('idx_token_transactions_wallet')
    op.drop_index('idx_token_transactions_user')
    op.drop_index('idx_tournament_matches_tournament')
    op.drop_index('idx_tournament_registrations_tournament')
    op.drop_index('idx_tournament_registrations_user')
    op.drop_index('idx_tournaments_start_time')
    op.drop_index('idx_tournaments_game')
    op.drop_index('idx_tournaments_status')
    
    # Drop tables
    op.drop_table('game_invitations')
    op.drop_table('friend_requests')
    op.drop_table('friendships')
    op.drop_table('token_packages')
    op.drop_table('token_transactions')
    op.drop_table('token_wallets')
    op.drop_table('tournament_matches')
    op.drop_table('tournament_registrations')
    op.drop_table('tournaments')
