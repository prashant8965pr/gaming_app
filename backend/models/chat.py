"""
Chat and messaging models
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from config.database import Base


class Conversation(Base):
    """Conversation between users"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_type = Column(String(50), default="direct")  # direct, group

    # For direct messages (1-on-1)
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # For group chats (future expansion)
    name = Column(String(255))
    avatar = Column(Text)

    # Metadata
    last_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    last_message_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", foreign_keys="Message.conversation_id")

    # Indexes
    __table_args__ = (
        Index('idx_conversation_users', 'user1_id', 'user2_id'),
        Index('idx_conversation_last_message', 'last_message_at'),
    )

    def to_dict(self, current_user_id=None):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "conversation_type": self.conversation_type,
            "user1_id": str(self.user1_id) if self.user1_id else None,
            "user2_id": str(self.user2_id) if self.user2_id else None,
            "name": self.name,
            "avatar": self.avatar,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Message(Base):
    """Message in a conversation"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Message content
    message_type = Column(String(50), default="text")  # text, image, game_invite, system
    content = Column(Text)
    metadata = Column(JSONB)  # For images, game invites, etc.

    # Status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    edited_at = Column(DateTime)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages", foreign_keys=[conversation_id])
    read_receipts = relationship("MessageReadReceipt", back_populates="message")

    # Indexes
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id', 'sent_at'),
        Index('idx_message_sender', 'sender_id'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "sender_id": str(self.sender_id),
            "message_type": self.message_type,
            "content": self.content,
            "metadata": self.metadata,
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted,
            "sent_at": self.sent_at.isoformat(),
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
        }


class MessageReadReceipt(Base):
    """Track when users read messages"""
    __tablename__ = "message_read_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("Message", back_populates="read_receipts")

    # Indexes
    __table_args__ = (
        Index('idx_read_receipt_message', 'message_id'),
        Index('idx_read_receipt_user', 'user_id'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "message_id": str(self.message_id),
            "user_id": str(self.user_id),
            "read_at": self.read_at.isoformat(),
        }


class TypingIndicator(Base):
    """Track typing indicators (ephemeral, can be cached in Redis)"""
    __tablename__ = "typing_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Auto-expire after 5 seconds

    # Indexes
    __table_args__ = (
        Index('idx_typing_conversation', 'conversation_id'),
        Index('idx_typing_expires', 'expires_at'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "user_id": str(self.user_id),
            "started_at": self.started_at.isoformat(),
        }
