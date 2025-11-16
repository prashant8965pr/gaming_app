"""Phase 8: Add role field to users table for admin access

Revision ID: 004_phase_8_admin_role
Revises: 003_phase_4_games
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '004_phase_8_admin_role'
down_revision = '003_phase_4_games'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add role field to users table for role-based access control
    """
    # Add role column with default 'user'
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))

    # Create index on role column
    op.create_index('idx_role', 'users', ['role'], unique=False)


def downgrade():
    """
    Remove role field from users table
    """
    # Drop index
    op.drop_index('idx_role', table_name='users')

    # Drop column
    op.drop_column('users', 'role')
