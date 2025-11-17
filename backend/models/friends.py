"""
Friends system models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from config.database import Base


class Friendship(Base):
    """Friendship between two users"""
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    friend_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status: pending, accepted, blocked
    status = Column(String(50), default="accepted")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="friendships")
    friend = relationship("User", foreign_keys=[friend_id], backref="friend_of")
    
    def __repr__(self):
        return f"<Friendship user_id={self.user_id} friend_id={self.friend_id}>"
    
    def to_dict(self):
        """Convert friendship to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "friend_id": str(self.friend_id),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
        }


class FriendRequest(Base):
    """Friend request from one user to another"""
    __tablename__ = "friend_requests"
    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status: pending, accepted, rejected, cancelled
    status = Column(String(50), default="pending")
    message = Column(Text)  # Optional message with request
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_friend_requests")
    
    def __repr__(self):
        return f"<FriendRequest from={self.sender_id} to={self.receiver_id}>"
    
    def to_dict(self):
        """Convert friend request to dictionary"""
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }


class GameInvitation(Base):
    """Game invitation from one user to another"""
    __tablename__ = "game_invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"), nullable=False)
    
    # Status: pending, accepted, rejected, expired
    status = Column(String(50), default="pending")
    message = Column(Text)
    
    # Expiry (auto-expire after game starts or 10 minutes)
    expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_game_invitations")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_game_invitations")
    game_session = relationship("GameSession", backref="invitations")
    
    def __repr__(self):
        return f"<GameInvitation from={self.sender_id} to={self.receiver_id}>"
    
    def to_dict(self):
        """Convert invitation to dictionary"""
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "game_session_id": str(self.game_session_id),
            "status": self.status,
            "message": self.message,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }
