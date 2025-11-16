"""Phase 2: Add KYC and wallet tables

Revision ID: 001_phase_2
Revises:
Create Date: 2025-11-16 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_phase_2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('date_of_birth', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('kyc_status', sa.String(length=20), nullable=False),
    sa.Column('is_email_verified', sa.Boolean(), nullable=True),
    sa.Column('is_phone_verified', sa.Boolean(), nullable=True),
    sa.Column('referral_code', sa.String(length=10), nullable=False),
    sa.Column('referred_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['referred_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kyc_status', 'users', ['kyc_status'], unique=False)
    op.create_index('idx_status', 'users', ['status'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create user_sessions table
    op.create_table('user_sessions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('access_token', sa.String(length=500), nullable=False),
    sa.Column('refresh_token', sa.String(length=500), nullable=False),
    sa.Column('device_id', sa.String(length=255), nullable=True),
    sa.Column('device_name', sa.String(length=100), nullable=True),
    sa.Column('device_os', sa.String(length=50), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_access_token'), 'user_sessions', ['access_token'], unique=False)
    op.create_index(op.f('ix_user_sessions_refresh_token'), 'user_sessions', ['refresh_token'], unique=False)

    # Create otp_attempts table
    op.create_table('otp_attempts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('otp_code', sa.String(length=6), nullable=False),
    sa.Column('purpose', sa.String(length=20), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('attempts_count', sa.Integer(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_otp_expires_at', 'otp_attempts', ['expires_at'], unique=False)
    op.create_index('idx_otp_phone_purpose', 'otp_attempts', ['phone', 'purpose'], unique=False)

    # Create social_auth_providers table
    op.create_table('social_auth_providers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('provider_user_id', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('access_token', sa.String(length=1000), nullable=True),
    sa.Column('refresh_token', sa.String(length=1000), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_provider_user', 'social_auth_providers', ['provider', 'provider_user_id'], unique=True)
    op.create_index('idx_social_auth_user_id', 'social_auth_providers', ['user_id'], unique=False)

    # Create user_profiles table
    op.create_table('user_profiles',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('bio', sa.String(length=500), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=True),
    sa.Column('preferred_language', sa.String(length=10), nullable=True),
    sa.Column('notification_preferences', sa.String(length=1000), nullable=True),
    sa.Column('privacy_settings', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )

    # Create user_statistics table
    op.create_table('user_statistics',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('total_games_played', sa.Integer(), nullable=True),
    sa.Column('total_games_won', sa.Integer(), nullable=True),
    sa.Column('total_games_lost', sa.Integer(), nullable=True),
    sa.Column('total_winnings', sa.Integer(), nullable=True),
    sa.Column('total_spent', sa.Integer(), nullable=True),
    sa.Column('current_level', sa.Integer(), nullable=True),
    sa.Column('experience_points', sa.Integer(), nullable=True),
    sa.Column('current_streak', sa.Integer(), nullable=True),
    sa.Column('longest_streak', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )

    # Create kyc_documents table
    op.create_table('kyc_documents',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('document_type', sa.String(length=30), nullable=False),
    sa.Column('document_number', sa.String(length=50), nullable=False),
    sa.Column('document_front_url', sa.String(length=500), nullable=True),
    sa.Column('document_back_url', sa.String(length=500), nullable=True),
    sa.Column('selfie_url', sa.String(length=500), nullable=True),
    sa.Column('full_name', sa.String(length=200), nullable=True),
    sa.Column('father_name', sa.String(length=200), nullable=True),
    sa.Column('date_of_birth', sa.DateTime(), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('verification_method', sa.String(length=30), nullable=True),
    sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('admin_notes', sa.Text(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kyc_document_type', 'kyc_documents', ['document_type'], unique=False)
    op.create_index('idx_kyc_status', 'kyc_documents', ['status'], unique=False)
    op.create_index('idx_kyc_submitted_at', 'kyc_documents', ['submitted_at'], unique=False)
    op.create_index('idx_kyc_user_id', 'kyc_documents', ['user_id'], unique=False)

    # Create bank_accounts table
    op.create_table('bank_accounts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('account_holder_name', sa.String(length=200), nullable=False),
    sa.Column('account_number', sa.String(length=50), nullable=False),
    sa.Column('ifsc_code', sa.String(length=11), nullable=False),
    sa.Column('bank_name', sa.String(length=200), nullable=True),
    sa.Column('branch_name', sa.String(length=200), nullable=True),
    sa.Column('account_type', sa.String(length=20), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('verification_method', sa.String(length=30), nullable=True),
    sa.Column('verification_reference', sa.String(length=100), nullable=True),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_primary', sa.Boolean(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bank_accounts_is_primary', 'bank_accounts', ['is_primary'], unique=False)
    op.create_index('idx_bank_accounts_status', 'bank_accounts', ['status'], unique=False)
    op.create_index('idx_bank_accounts_user_id', 'bank_accounts', ['user_id'], unique=False)

    # Create kyc_verification_history table
    op.create_table('kyc_verification_history',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('kyc_document_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('action', sa.String(length=30), nullable=False),
    sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('old_status', sa.String(length=20), nullable=True),
    sa.Column('new_status', sa.String(length=20), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['kyc_document_id'], ['kyc_documents.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kyc_history_created_at', 'kyc_verification_history', ['created_at'], unique=False)
    op.create_index('idx_kyc_history_document_id', 'kyc_verification_history', ['kyc_document_id'], unique=False)
    op.create_index('idx_kyc_history_user_id', 'kyc_verification_history', ['user_id'], unique=False)

    # Create wallets table
    op.create_table('wallets',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('wallet_type', sa.String(length=20), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('is_locked', sa.Boolean(), nullable=True),
    sa.Column('daily_withdrawal_limit', sa.Integer(), nullable=True),
    sa.Column('max_balance_limit', sa.Integer(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_wallets_type', 'wallets', ['wallet_type'], unique=False)
    op.create_index('idx_wallets_user_id', 'wallets', ['user_id'], unique=False)
    op.create_index('idx_wallets_user_type', 'wallets', ['user_id', 'wallet_type'], unique=True)

    # Create withdrawal_requests table
    op.create_table('withdrawal_requests',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('requested_amount', sa.Integer(), nullable=False),
    sa.Column('tds_amount', sa.Integer(), nullable=True),
    sa.Column('processing_fee', sa.Integer(), nullable=True),
    sa.Column('final_amount', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('account_holder_name', sa.String(length=200), nullable=False),
    sa.Column('account_number', sa.String(length=50), nullable=False),
    sa.Column('ifsc_code', sa.String(length=11), nullable=False),
    sa.Column('bank_name', sa.String(length=200), nullable=True),
    sa.Column('payment_gateway', sa.String(length=30), nullable=True),
    sa.Column('gateway_payout_id', sa.String(length=100), nullable=True),
    sa.Column('utr_number', sa.String(length=50), nullable=True),
    sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('admin_notes', sa.Text(), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('failure_reason', sa.Text(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_withdrawals_bank_account_id', 'withdrawal_requests', ['bank_account_id'], unique=False)
    op.create_index('idx_withdrawals_created_at', 'withdrawal_requests', ['created_at'], unique=False)
    op.create_index('idx_withdrawals_status', 'withdrawal_requests', ['status'], unique=False)
    op.create_index('idx_withdrawals_user_id', 'withdrawal_requests', ['user_id'], unique=False)

    # Create transactions table
    op.create_table('transactions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('transaction_type', sa.String(length=30), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('balance_before', sa.Integer(), nullable=False),
    sa.Column('balance_after', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('payment_gateway', sa.String(length=30), nullable=True),
    sa.Column('gateway_transaction_id', sa.String(length=100), nullable=True),
    sa.Column('gateway_order_id', sa.String(length=100), nullable=True),
    sa.Column('payment_method', sa.String(length=30), nullable=True),
    sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('contest_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('withdrawal_request_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('tds_amount', sa.Integer(), nullable=True),
    sa.Column('tds_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('admin_notes', sa.Text(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('processed_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('failed_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['withdrawal_request_id'], ['withdrawal_requests.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transactions_created_at', 'transactions', ['created_at'], unique=False)
    op.create_index('idx_transactions_gateway_id', 'transactions', ['gateway_transaction_id'], unique=False)
    op.create_index('idx_transactions_status', 'transactions', ['status'], unique=False)
    op.create_index('idx_transactions_type', 'transactions', ['transaction_type'], unique=False)
    op.create_index('idx_transactions_user_id', 'transactions', ['user_id'], unique=False)
    op.create_index('idx_transactions_wallet_id', 'transactions', ['wallet_id'], unique=False)
    op.create_index(op.f('ix_transactions_gateway_order_id'), 'transactions', ['gateway_order_id'], unique=False)

    # Create payment_orders table
    op.create_table('payment_orders',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('order_amount', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('payment_gateway', sa.String(length=30), nullable=False),
    sa.Column('gateway_order_id', sa.String(length=100), nullable=False),
    sa.Column('gateway_payment_id', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('payment_method', sa.String(length=30), nullable=True),
    sa.Column('payment_card_network', sa.String(length=20), nullable=True),
    sa.Column('payment_bank', sa.String(length=100), nullable=True),
    sa.Column('payment_wallet', sa.String(length=30), nullable=True),
    sa.Column('promo_code', sa.String(length=50), nullable=True),
    sa.Column('bonus_amount', sa.Integer(), nullable=True),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_orders_gateway_order_id', 'payment_orders', ['gateway_order_id'], unique=True)
    op.create_index('idx_payment_orders_status', 'payment_orders', ['status'], unique=False)
    op.create_index('idx_payment_orders_user_id', 'payment_orders', ['user_id'], unique=False)
    op.create_index(op.f('ix_payment_orders_gateway_payment_id'), 'payment_orders', ['gateway_payment_id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('payment_orders')
    op.drop_table('transactions')
    op.drop_table('withdrawal_requests')
    op.drop_table('wallets')
    op.drop_table('kyc_verification_history')
    op.drop_table('bank_accounts')
    op.drop_table('kyc_documents')
    op.drop_table('user_statistics')
    op.drop_table('user_profiles')
    op.drop_table('social_auth_providers')
    op.drop_table('otp_attempts')
    op.drop_table('user_sessions')
    op.drop_table('users')
