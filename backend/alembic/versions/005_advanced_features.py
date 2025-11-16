"""Add advanced features - 2FA, Promo Codes

Revision ID: 005_advanced_features
Revises: 004_phase_8_admin_role
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_advanced_features'
down_revision = '004_phase_8_admin_role'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create two_factor_auth table
    op.create_table(
        'two_factor_auth',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('secret', sa.String(length=32), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enabled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('backup_codes_generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('backup_codes_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_two_factor_auth_user_id'), 'two_factor_auth', ['user_id'], unique=True)

    # Create two_factor_backup_codes table
    op.create_table(
        'two_factor_backup_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_two_factor_backup_codes_user_id'), 'two_factor_backup_codes', ['user_id'], unique=False)

    # Create promo_codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('type', sa.Enum('PERCENTAGE', 'FIXED', 'FREE_ENTRY', name='promocodetype'), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('max_discount', sa.Float(), nullable=True),
        sa.Column('min_transaction_amount', sa.Float(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('max_uses_per_user', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_uses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'EXPIRED', 'DISABLED', name='promocodestatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('target_user_ids', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_promo_codes_code'), 'promo_codes', ['code'], unique=True)
    op.create_index(op.f('ix_promo_codes_status'), 'promo_codes', ['status'], unique=False)

    # Create promo_code_usages table
    op.create_table(
        'promo_code_usages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('promo_code_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discount_amount', sa.Float(), nullable=False),
        sa.Column('transaction_amount', sa.Float(), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['promo_code_id'], ['promo_codes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promo_code_usages_promo_code_id'), 'promo_code_usages', ['promo_code_id'], unique=False)
    op.create_index(op.f('ix_promo_code_usages_user_id'), 'promo_code_usages', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop promo_code_usages table
    op.drop_index(op.f('ix_promo_code_usages_user_id'), table_name='promo_code_usages')
    op.drop_index(op.f('ix_promo_code_usages_promo_code_id'), table_name='promo_code_usages')
    op.drop_table('promo_code_usages')

    # Drop promo_codes table
    op.drop_index(op.f('ix_promo_codes_status'), table_name='promo_codes')
    op.drop_index(op.f('ix_promo_codes_code'), table_name='promo_codes')
    op.drop_table('promo_codes')
    op.execute('DROP TYPE promocodestatus')
    op.execute('DROP TYPE promocodetype')

    # Drop two_factor_backup_codes table
    op.drop_index(op.f('ix_two_factor_backup_codes_user_id'), table_name='two_factor_backup_codes')
    op.drop_table('two_factor_backup_codes')

    # Drop two_factor_auth table
    op.drop_index(op.f('ix_two_factor_auth_user_id'), table_name='two_factor_auth')
    op.drop_table('two_factor_auth')
