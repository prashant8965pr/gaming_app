"""Add live streaming and push notifications tables

Revision ID: 008
Revises: 007
Create Date: 2025-11-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================================================
    # Live Streaming Tables
    # ========================================================================

    # Create live_streams table
    op.create_table(
        'live_streams',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('streamer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('game_id', UUID(as_uuid=True), sa.ForeignKey('games.id', ondelete='SET NULL')),
        sa.Column('game_session_id', UUID(as_uuid=True), sa.ForeignKey('game_sessions.id', ondelete='SET NULL')),

        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('thumbnail_url', sa.String(500)),

        sa.Column('status', sa.String(20), default='scheduled', nullable=False),
        sa.Column('stream_key', sa.String(100), unique=True, nullable=False),
        sa.Column('stream_url', sa.String(500)),
        sa.Column('playback_url', sa.String(500)),

        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('allow_chat', sa.Boolean(), default=True),
        sa.Column('is_monetized', sa.Boolean(), default=False),
        sa.Column('entry_fee', sa.Integer(), default=0),

        sa.Column('viewer_count', sa.Integer(), default=0),
        sa.Column('peak_viewers', sa.Integer(), default=0),
        sa.Column('total_views', sa.Integer(), default=0),
        sa.Column('like_count', sa.Integer(), default=0),
        sa.Column('share_count', sa.Integer(), default=0),
        sa.Column('revenue_generated', sa.Integer(), default=0),

        sa.Column('scheduled_start_time', sa.DateTime(timezone=True)),
        sa.Column('actual_start_time', sa.DateTime(timezone=True)),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('duration_seconds', sa.Integer(), default=0),

        sa.Column('is_recorded', sa.Boolean(), default=True),
        sa.Column('recording_url', sa.String(500)),

        sa.Column('tags', JSONB(), default=[]),
        sa.Column('metadata', JSONB(), default={}),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )

    # Create stream_viewers table
    op.create_table(
        'stream_viewers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('stream_id', UUID(as_uuid=True), sa.ForeignKey('live_streams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('left_at', sa.DateTime(timezone=True)),
        sa.Column('watch_duration_seconds', sa.Integer(), default=0),

        sa.Column('paid_entry_fee', sa.Boolean(), default=False),
        sa.Column('payment_amount', sa.Integer(), default=0),
        sa.Column('payment_transaction_id', UUID(as_uuid=True)),

        sa.Column('liked', sa.Boolean(), default=False),
        sa.Column('shared', sa.Boolean(), default=False),
        sa.Column('messages_sent', sa.Integer(), default=0),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.UniqueConstraint('stream_id', 'user_id', name='unique_stream_viewer')
    )

    # Create stream_chat table
    op.create_table(
        'stream_chat',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('stream_id', UUID(as_uuid=True), sa.ForeignKey('live_streams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(20), default='text'),

        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('is_pinned', sa.Boolean(), default=False),

        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create stream_donations table
    op.create_table(
        'stream_donations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('stream_id', UUID(as_uuid=True), sa.ForeignKey('live_streams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('donor_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('streamer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text()),
        sa.Column('is_anonymous', sa.Boolean(), default=False),

        sa.Column('transaction_id', UUID(as_uuid=True)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('was_highlighted', sa.Boolean(), default=False),

        sa.Column('donated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # ========================================================================
    # Push Notifications Tables
    # ========================================================================

    # Create device_tokens table
    op.create_table(
        'device_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        sa.Column('device_token', sa.String(500), unique=True, nullable=False),
        sa.Column('device_type', sa.String(20), nullable=False),
        sa.Column('device_name', sa.String(100)),
        sa.Column('device_model', sa.String(100)),

        sa.Column('app_version', sa.String(20)),
        sa.Column('os_version', sa.String(20)),

        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )

    # Create push_notifications table
    op.create_table(
        'push_notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),

        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(500)),
        sa.Column('image', sa.String(500)),

        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(30), default='general', nullable=False),

        sa.Column('action_url', sa.String(500)),
        sa.Column('action_data', JSONB(), default={}),

        sa.Column('priority', sa.String(20), default='normal'),

        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
        sa.Column('delivered_at', sa.DateTime(timezone=True)),
        sa.Column('clicked_at', sa.DateTime(timezone=True)),
        sa.Column('failed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text()),

        sa.Column('fcm_message_id', sa.String(200)),
        sa.Column('apns_message_id', sa.String(200)),

        sa.Column('scheduled_for', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('group_key', sa.String(100)),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )

    # Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),

        sa.Column('push_enabled', sa.Boolean(), default=True),
        sa.Column('email_enabled', sa.Boolean(), default=True),
        sa.Column('sms_enabled', sa.Boolean(), default=False),

        sa.Column('social_notifications', sa.Boolean(), default=True),
        sa.Column('gaming_notifications', sa.Boolean(), default=True),
        sa.Column('financial_notifications', sa.Boolean(), default=True),
        sa.Column('promotional_notifications', sa.Boolean(), default=True),
        sa.Column('system_notifications', sa.Boolean(), default=True),

        sa.Column('quiet_hours_enabled', sa.Boolean(), default=False),
        sa.Column('quiet_hours_start', sa.String(5)),
        sa.Column('quiet_hours_end', sa.String(5)),

        sa.Column('sound_enabled', sa.Boolean(), default=True),
        sa.Column('vibration_enabled', sa.Boolean(), default=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )

    # Create notification_templates table
    op.create_table(
        'notification_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        sa.Column('template_code', sa.String(100), unique=True, nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(30), nullable=False),

        sa.Column('title_template', sa.String(200), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),

        sa.Column('default_action_url', sa.String(500)),
        sa.Column('icon_url', sa.String(500)),
        sa.Column('image_url', sa.String(500)),

        sa.Column('default_priority', sa.String(20), default='normal'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('language', sa.String(10), default='en'),

        sa.Column('description', sa.Text()),
        sa.Column('tags', JSONB(), default=[]),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )

    # ========================================================================
    # Create Indexes
    # ========================================================================

    # Live streaming indexes
    op.create_index('idx_live_streams_streamer', 'live_streams', ['streamer_id'])
    op.create_index('idx_live_streams_status', 'live_streams', ['status'])
    op.create_index('idx_live_streams_game', 'live_streams', ['game_id'])
    op.create_index('idx_live_streams_start_time', 'live_streams', ['actual_start_time'])

    op.create_index('idx_stream_viewers_stream', 'stream_viewers', ['stream_id'])
    op.create_index('idx_stream_viewers_user', 'stream_viewers', ['user_id'])

    op.create_index('idx_stream_chat_stream', 'stream_chat', ['stream_id', 'sent_at'])
    op.create_index('idx_stream_chat_user', 'stream_chat', ['user_id'])

    op.create_index('idx_stream_donations_stream', 'stream_donations', ['stream_id'])
    op.create_index('idx_stream_donations_donor', 'stream_donations', ['donor_id'])
    op.create_index('idx_stream_donations_streamer', 'stream_donations', ['streamer_id'])

    # Push notification indexes
    op.create_index('idx_device_tokens_user', 'device_tokens', ['user_id'])
    op.create_index('idx_device_tokens_active', 'device_tokens', ['is_active'])
    op.create_index('idx_device_tokens_token', 'device_tokens', ['device_token'])

    op.create_index('idx_push_notifications_user', 'push_notifications', ['user_id'])
    op.create_index('idx_push_notifications_type', 'push_notifications', ['notification_type'])
    op.create_index('idx_push_notifications_status', 'push_notifications', ['status'])
    op.create_index('idx_push_notifications_scheduled', 'push_notifications', ['scheduled_for'])
    op.create_index('idx_push_notifications_group', 'push_notifications', ['group_key'])

    op.create_index('idx_notification_templates_code', 'notification_templates', ['template_code'])
    op.create_index('idx_notification_templates_type', 'notification_templates', ['notification_type'])
    op.create_index('idx_notification_templates_active', 'notification_templates', ['is_active'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_notification_templates_active', 'notification_templates')
    op.drop_index('idx_notification_templates_type', 'notification_templates')
    op.drop_index('idx_notification_templates_code', 'notification_templates')

    op.drop_index('idx_push_notifications_group', 'push_notifications')
    op.drop_index('idx_push_notifications_scheduled', 'push_notifications')
    op.drop_index('idx_push_notifications_status', 'push_notifications')
    op.drop_index('idx_push_notifications_type', 'push_notifications')
    op.drop_index('idx_push_notifications_user', 'push_notifications')

    op.drop_index('idx_device_tokens_token', 'device_tokens')
    op.drop_index('idx_device_tokens_active', 'device_tokens')
    op.drop_index('idx_device_tokens_user', 'device_tokens')

    op.drop_index('idx_stream_donations_streamer', 'stream_donations')
    op.drop_index('idx_stream_donations_donor', 'stream_donations')
    op.drop_index('idx_stream_donations_stream', 'stream_donations')

    op.drop_index('idx_stream_chat_user', 'stream_chat')
    op.drop_index('idx_stream_chat_stream', 'stream_chat')

    op.drop_index('idx_stream_viewers_user', 'stream_viewers')
    op.drop_index('idx_stream_viewers_stream', 'stream_viewers')

    op.drop_index('idx_live_streams_start_time', 'live_streams')
    op.drop_index('idx_live_streams_game', 'live_streams')
    op.drop_index('idx_live_streams_status', 'live_streams')
    op.drop_index('idx_live_streams_streamer', 'live_streams')

    # Drop tables
    op.drop_table('notification_templates')
    op.drop_table('notification_preferences')
    op.drop_table('push_notifications')
    op.drop_table('device_tokens')

    op.drop_table('stream_donations')
    op.drop_table('stream_chat')
    op.drop_table('stream_viewers')
    op.drop_table('live_streams')
