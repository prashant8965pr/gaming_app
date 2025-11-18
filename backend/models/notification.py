"""
Push Notification Models
SQLAlchemy models for push notifications and device management
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid
from datetime import datetime


class DeviceToken(Base):
    """User device tokens for push notifications"""
    __tablename__ = "device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Device information
    device_token = Column(String(500), unique=True, nullable=False, index=True)
    device_type = Column(String(20), nullable=False)  # ios, android, web
    device_name = Column(String(100), nullable=True)
    device_model = Column(String(100), nullable=True)

    # App version
    app_version = Column(String(20), nullable=True)
    os_version = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())

    # Notification preferences
    enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_device_tokens_user', 'user_id'),
        Index('idx_device_tokens_active', 'is_active'),
    )


class PushNotification(Base):
    """Push notification records"""
    __tablename__ = "push_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Notification content
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    icon = Column(String(500), nullable=True)
    image = Column(String(500), nullable=True)

    # Notification type and category
    notification_type = Column(String(50), nullable=False)
    # Types: tournament_start, friend_request, message, game_invite, achievement,
    # daily_bonus, stream_live, withdrawal_approved, etc.

    category = Column(String(30), nullable=False, default="general")
    # Categories: social, gaming, financial, promotional, system

    # Action data
    action_url = Column(String(500), nullable=True)  # Deep link
    action_data = Column(JSONB, default={}, nullable=True)  # Additional data

    # Priority
    priority = Column(String(20), default="normal")  # low, normal, high, urgent

    # Delivery status
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed, clicked
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # FCM/APNs response
    fcm_message_id = Column(String(200), nullable=True)
    apns_message_id = Column(String(200), nullable=True)

    # Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Grouping (for notification grouping/bundling)
    group_key = Column(String(100), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_push_notifications_user', 'user_id'),
        Index('idx_push_notifications_type', 'notification_type'),
        Index('idx_push_notifications_status', 'status'),
        Index('idx_push_notifications_scheduled', 'scheduled_for'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "body": self.body,
            "icon": self.icon,
            "image": self.image,
            "notification_type": self.notification_type,
            "category": self.category,
            "action_url": self.action_url,
            "action_data": self.action_data,
            "priority": self.priority,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Channel preferences
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)

    # Category preferences
    social_notifications = Column(Boolean, default=True)  # Friend requests, messages
    gaming_notifications = Column(Boolean, default=True)  # Game invites, tournament updates
    financial_notifications = Column(Boolean, default=True)  # Withdrawals, deposits
    promotional_notifications = Column(Boolean, default=True)  # Offers, bonuses
    system_notifications = Column(Boolean, default=True)  # Account updates, security

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # "22:00"
    quiet_hours_end = Column(String(5), nullable=True)  # "08:00"

    # Notification sounds
    sound_enabled = Column(Boolean, default=True)
    vibration_enabled = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationTemplate(Base):
    """Notification templates for different events"""
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template identification
    template_code = Column(String(100), unique=True, nullable=False, index=True)
    notification_type = Column(String(50), nullable=False)
    category = Column(String(30), nullable=False)

    # Template content (supports variables like {username}, {amount}, etc.)
    title_template = Column(String(200), nullable=False)
    body_template = Column(Text, nullable=False)

    # Default action
    default_action_url = Column(String(500), nullable=True)

    # Icon and image URLs
    icon_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Default priority
    default_priority = Column(String(20), default="normal")

    # Status
    is_active = Column(Boolean, default=True)

    # Localization
    language = Column(String(10), default="en")

    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSONB, default=[], nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_notification_templates_type', 'notification_type'),
        Index('idx_notification_templates_active', 'is_active'),
    )
