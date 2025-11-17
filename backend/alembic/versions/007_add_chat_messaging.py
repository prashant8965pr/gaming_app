"""Add chat and messaging tables

Revision ID: 007
Revises: 006
Create Date: 2025-01-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_type', sa.String(50), default='direct'),
        sa.Column('user1_id', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('user2_id', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(255)),
        sa.Column('avatar', sa.Text()),
        sa.Column('last_message_id', UUID(as_uuid=True)),
        sa.Column('last_message_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('sender_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('message_type', sa.String(50), default='text'),
        sa.Column('content', sa.Text()),
        sa.Column('metadata', JSONB()),
        sa.Column('is_edited', sa.Boolean(), default=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('edited_at', sa.DateTime()),
    )

    # Create message_read_receipts table
    op.create_table(
        'message_read_receipts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', UUID(as_uuid=True), sa.ForeignKey('messages.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('read_at', sa.DateTime()),
    )

    # Create typing_indicators table
    op.create_table(
        'typing_indicators',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('expires_at', sa.DateTime()),
    )

    # Add foreign key for last_message_id after messages table is created
    op.create_foreign_key(
        'fk_conversations_last_message',
        'conversations',
        'messages',
        ['last_message_id'],
        ['id']
    )

    # Create indexes for conversations
    op.create_index('idx_conversation_users', 'conversations', ['user1_id', 'user2_id'])
    op.create_index('idx_conversation_last_message', 'conversations', ['last_message_at'])

    # Create indexes for messages
    op.create_index('idx_message_conversation', 'messages', ['conversation_id', 'sent_at'])
    op.create_index('idx_message_sender', 'messages', ['sender_id'])

    # Create indexes for read receipts
    op.create_index('idx_read_receipt_message', 'message_read_receipts', ['message_id'])
    op.create_index('idx_read_receipt_user', 'message_read_receipts', ['user_id'])

    # Create indexes for typing indicators
    op.create_index('idx_typing_conversation', 'typing_indicators', ['conversation_id'])
    op.create_index('idx_typing_expires', 'typing_indicators', ['expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_typing_expires', 'typing_indicators')
    op.drop_index('idx_typing_conversation', 'typing_indicators')
    op.drop_index('idx_read_receipt_user', 'message_read_receipts')
    op.drop_index('idx_read_receipt_message', 'message_read_receipts')
    op.drop_index('idx_message_sender', 'messages')
    op.drop_index('idx_message_conversation', 'messages')
    op.drop_index('idx_conversation_last_message', 'conversations')
    op.drop_index('idx_conversation_users', 'conversations')

    # Drop foreign key
    op.drop_constraint('fk_conversations_last_message', 'conversations', type_='foreignkey')

    # Drop tables
    op.drop_table('typing_indicators')
    op.drop_table('message_read_receipts')
    op.drop_table('messages')
    op.drop_table('conversations')
