"""
Tournament models for gaming platform
Supports single elimination, double elimination, and round-robin tournaments
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from config.database import Base


class Tournament(Base):
    """Tournament model"""
    __tablename__ = "tournaments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False)
    
    # Tournament type: single_elimination, double_elimination, round_robin
    tournament_type = Column(String(50), default="single_elimination")
    
    # Entry and prizes
    entry_fee = Column(Integer, default=0)  # in paise
    prize_pool = Column(Integer, default=0)  # in paise
    prize_distribution = Column(JSON)  # {"1st": 50, "2nd": 30, "3rd": 20}
    
    # Participants
    max_participants = Column(Integer, default=16)
    min_participants = Column(Integer, default=4)
    current_participants = Column(Integer, default=0)
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    registration_start = Column(DateTime, nullable=False)
    registration_end = Column(DateTime, nullable=False)
    
    # Status: upcoming, registration_open, registration_closed, live, completed, cancelled
    status = Column(String(50), default="upcoming")
    
    # Bracket data (generated automatically)
    bracket_data = Column(JSON)  # Stores bracket structure
    
    # Metadata
    rules = Column(JSON)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", backref="tournaments")
    registrations = relationship("TournamentRegistration", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("TournamentMatch", back_populates="tournament", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tournament {self.name}>"
    
    def to_dict(self):
        """Convert tournament to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "game_id": str(self.game_id),
            "tournament_type": self.tournament_type,
            "entry_fee": self.entry_fee,
            "prize_pool": self.prize_pool,
            "prize_distribution": self.prize_distribution,
            "max_participants": self.max_participants,
            "min_participants": self.min_participants,
            "current_participants": self.current_participants,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "registration_start": self.registration_start.isoformat() if self.registration_start else None,
            "registration_end": self.registration_end.isoformat() if self.registration_end else None,
            "status": self.status,
            "bracket_data": self.bracket_data,
            "rules": self.rules,
            "is_featured": self.is_featured,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TournamentRegistration(Base):
    """Tournament registration model"""
    __tablename__ = "tournament_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Registration info
    registration_time = Column(DateTime, default=datetime.utcnow)
    seed_number = Column(Integer)  # Position in bracket
    
    # Status: pending_payment, registered, checked_in, eliminated, winner
    status = Column(String(50), default="pending_payment")
    payment_status = Column(String(50), default="pending")  # pending, completed, refunded
    payment_transaction_id = Column(UUID(as_uuid=True))
    
    # Final results
    final_rank = Column(Integer)
    prize_won = Column(Integer, default=0)  # in paise
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="registrations")
    user = relationship("User", backref="tournament_registrations")
    
    def __repr__(self):
        return f"<TournamentRegistration user_id={self.user_id} tournament_id={self.tournament_id}>"
    
    def to_dict(self):
        """Convert registration to dictionary"""
        return {
            "id": str(self.id),
            "tournament_id": str(self.tournament_id),
            "user_id": str(self.user_id),
            "registration_time": self.registration_time.isoformat() if self.registration_time else None,
            "seed_number": self.seed_number,
            "status": self.status,
            "payment_status": self.payment_status,
            "final_rank": self.final_rank,
            "prize_won": self.prize_won,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TournamentMatch(Base):
    """Individual match within a tournament"""
    __tablename__ = "tournament_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=False)
    
    # Match position in bracket
    round_number = Column(Integer, nullable=False)  # 1, 2, 3 (finals)
    match_number = Column(Integer, nullable=False)  # Position in round
    
    # Players
    player1_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    player2_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Match data
    score_data = Column(JSON)  # {"player1": score, "player2": score}
    game_session_id = Column(UUID(as_uuid=True))  # Reference to actual game played
    
    # Status: pending, ready, in_progress, completed, walkover
    status = Column(String(50), default="pending")
    
    # Scheduling
    scheduled_time = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Metadata
    is_finals = Column(Boolean, default=False)
    is_consolation = Column(Boolean, default=False)  # For 3rd place match
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("User", foreign_keys=[player1_id], backref="tournament_matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], backref="tournament_matches_as_player2")
    winner = relationship("User", foreign_keys=[winner_id], backref="tournament_matches_won")
    
    def __repr__(self):
        return f"<TournamentMatch Round {self.round_number} Match {self.match_number}>"
    
    def to_dict(self):
        """Convert match to dictionary"""
        return {
            "id": str(self.id),
            "tournament_id": str(self.tournament_id),
            "round_number": self.round_number,
            "match_number": self.match_number,
            "player1_id": str(self.player1_id) if self.player1_id else None,
            "player2_id": str(self.player2_id) if self.player2_id else None,
            "winner_id": str(self.winner_id) if self.winner_id else None,
            "score_data": self.score_data,
            "game_session_id": str(self.game_session_id) if self.game_session_id else None,
            "status": self.status,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_finals": self.is_finals,
            "is_consolation": self.is_consolation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
