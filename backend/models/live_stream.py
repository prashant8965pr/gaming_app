"""
Live Streaming Models
SQLAlchemy models for live streaming functionality
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid
from datetime import datetime


class LiveStream(Base):
    """Live streams table"""
    __tablename__ = "live_streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    streamer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="SET NULL"), nullable=True)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="SET NULL"), nullable=True)

    # Stream details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    # Stream status
    status = Column(String(20), default="scheduled", nullable=False)  # scheduled, live, ended, cancelled

    # Stream URLs and keys
    stream_key = Column(String(100), unique=True, nullable=False)  # For RTMP
    stream_url = Column(String(500), nullable=True)  # HLS/RTMP URL
    playback_url = Column(String(500), nullable=True)  # Viewer URL

    # Stream settings
    is_public = Column(Boolean, default=True)
    allow_chat = Column(Boolean, default=True)
    is_monetized = Column(Boolean, default=False)
    entry_fee = Column(Integer, default=0)  # in paise

    # Statistics
    viewer_count = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    # Revenue (if monetized)
    revenue_generated = Column(Integer, default=0)  # in paise

    # Timestamps
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, default=0)

    # Recording
    is_recorded = Column(Boolean, default=True)
    recording_url = Column(String(500), nullable=True)

    # Metadata
    tags = Column(JSONB, default=[], nullable=True)  # ["ludo", "tournament", "pro"]
    metadata = Column(JSONB, default={}, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_live_streams_streamer', 'streamer_id'),
        Index('idx_live_streams_status', 'status'),
        Index('idx_live_streams_game', 'game_id'),
        Index('idx_live_streams_start_time', 'actual_start_time'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "streamer_id": str(self.streamer_id),
            "game_id": str(self.game_id) if self.game_id else None,
            "title": self.title,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "status": self.status,
            "playback_url": self.playback_url,
            "is_public": self.is_public,
            "allow_chat": self.allow_chat,
            "is_monetized": self.is_monetized,
            "entry_fee": self.entry_fee,
            "viewer_count": self.viewer_count,
            "peak_viewers": self.peak_viewers,
            "total_views": self.total_views,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "scheduled_start_time": self.scheduled_start_time.isoformat() if self.scheduled_start_time else None,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "is_recorded": self.is_recorded,
            "recording_url": self.recording_url,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class StreamViewer(Base):
    """Track stream viewers"""
    __tablename__ = "stream_viewers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_id = Column(UUID(as_uuid=True), ForeignKey("live_streams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Viewing details
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    watch_duration_seconds = Column(Integer, default=0)

    # Payment (if monetized stream)
    paid_entry_fee = Column(Boolean, default=False)
    payment_amount = Column(Integer, default=0)  # in paise
    payment_transaction_id = Column(UUID(as_uuid=True), nullable=True)

    # Engagement
    liked = Column(Boolean, default=False)
    shared = Column(Boolean, default=False)
    messages_sent = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_stream_viewers_stream', 'stream_id'),
        Index('idx_stream_viewers_user', 'user_id'),
        Index('idx_stream_viewers_unique', 'stream_id', 'user_id', unique=True),
    )


class StreamChat(Base):
    """Live stream chat messages"""
    __tablename__ = "stream_chat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_id = Column(UUID(as_uuid=True), ForeignKey("live_streams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message
    message = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, emoji, sticker, system

    # Moderation
    is_deleted = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)

    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_stream_chat_stream', 'stream_id', 'sent_at'),
        Index('idx_stream_chat_user', 'user_id'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "stream_id": str(self.stream_id),
            "user_id": str(self.user_id),
            "message": self.message,
            "message_type": self.message_type,
            "is_deleted": self.is_deleted,
            "is_pinned": self.is_pinned,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }


class StreamDonation(Base):
    """Donations/tips during live streams"""
    __tablename__ = "stream_donations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_id = Column(UUID(as_uuid=True), ForeignKey("live_streams.id", ondelete="CASCADE"), nullable=False)
    donor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    streamer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Donation details
    amount = Column(Integer, nullable=False)  # in paise
    message = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)

    # Transaction
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, failed

    # Display
    was_highlighted = Column(Boolean, default=False)  # Show prominently in stream

    # Timestamps
    donated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_stream_donations_stream', 'stream_id'),
        Index('idx_stream_donations_donor', 'donor_id'),
        Index('idx_stream_donations_streamer', 'streamer_id'),
    )
