"""
Quiz Game Models
SQLAlchemy models for quiz questions, categories, and game state
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base
import uuid


class QuizCategory(Base):
    """Quiz question categories"""
    __tablename__ = "quiz_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Category details
    code = Column(String(50), unique=True, nullable=False, index=True)  # general, science, history, sports
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)

    # Category settings
    is_active = Column(Boolean, default=True)
    difficulty_multiplier = Column(Float, default=1.0)  # Scoring multiplier for this category

    # Stats
    total_questions = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    questions = relationship("QuizQuestion", back_populates="category")

    # Indexes
    __table_args__ = (
        Index('idx_quiz_categories_code', 'code'),
        Index('idx_quiz_categories_is_active', 'is_active'),
    )


class QuizQuestion(Base):
    """Quiz question bank"""
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("quiz_categories.id", ondelete="CASCADE"), nullable=False)

    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, true_false, text

    # Difficulty: easy, medium, hard
    difficulty = Column(String(20), default="medium", nullable=False)

    # Answers
    correct_answer = Column(String(500), nullable=False)
    incorrect_answers = Column(ARRAY(String), nullable=False)  # Array of wrong answers

    # Additional info
    explanation = Column(Text, nullable=True)  # Explanation after answering
    hint = Column(String(500), nullable=True)  # Optional hint

    # Media
    image_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)

    # Settings
    time_limit_seconds = Column(Integer, default=15)  # Time to answer
    base_points = Column(Integer, default=100)  # Base points for correct answer

    # Metadata
    source = Column(String(100), nullable=True)  # Where question came from (API, manual, etc.)
    tags = Column(ARRAY(String), nullable=True)  # For filtering
    question_metadata = Column(JSONB, default={}, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Admin verified

    # Stats
    times_asked = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("QuizCategory", back_populates="questions")

    # Indexes
    __table_args__ = (
        Index('idx_quiz_questions_category_id', 'category_id'),
        Index('idx_quiz_questions_difficulty', 'difficulty'),
        Index('idx_quiz_questions_is_active', 'is_active'),
    )

    @property
    def accuracy_rate(self) -> float:
        """Calculate question accuracy rate"""
        total = self.times_correct + self.times_incorrect
        if total == 0:
            return 0.0
        return (self.times_correct / total) * 100

    def to_dict(self, include_answer: bool = False):
        """Convert to dictionary (optionally include answer for validation)"""
        data = {
            "id": str(self.id),
            "category_id": str(self.category_id),
            "question_text": self.question_text,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "incorrect_answers": self.incorrect_answers,
            "time_limit_seconds": self.time_limit_seconds,
            "base_points": self.base_points,
            "hint": self.hint,
            "image_url": self.image_url,
            "explanation": self.explanation,
            "tags": self.tags,
        }

        if include_answer:
            data["correct_answer"] = self.correct_answer

        return data


class QuizGameSession(Base):
    """Active quiz game sessions - extends GameSession"""
    __tablename__ = "quiz_game_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Quiz settings
    num_questions = Column(Integer, default=10)
    category_id = Column(UUID(as_uuid=True), ForeignKey("quiz_categories.id"), nullable=True)  # Null = mixed
    difficulty = Column(String(20), nullable=True)  # Null = mixed

    # Game state
    current_question_index = Column(Integer, default=0)
    questions_data = Column(JSONB, nullable=False)  # Array of question IDs and order

    # Timing
    question_started_at = Column(DateTime(timezone=True), nullable=True)
    question_deadline = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_quiz_sessions_game_session_id', 'game_session_id'),
        Index('idx_quiz_sessions_category_id', 'category_id'),
    )


class QuizAnswer(Base):
    """Player answers in quiz games"""
    __tablename__ = "quiz_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_session_id = Column(UUID(as_uuid=True), ForeignKey("quiz_game_sessions.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("game_participants.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id"), nullable=False)

    # Answer details
    question_index = Column(Integer, nullable=False)  # Which question in the quiz (0-9 for 10 questions)
    player_answer = Column(String(500), nullable=True)  # Null if timeout
    is_correct = Column(Boolean, nullable=False)

    # Timing
    time_taken_ms = Column(Integer, nullable=False)  # Milliseconds to answer
    answered_at = Column(DateTime(timezone=True), server_default=func.now())

    # Scoring
    points_earned = Column(Integer, default=0)
    time_bonus = Column(Integer, default=0)
    streak_bonus = Column(Integer, default=0)
    total_points = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_quiz_answers_session_id', 'quiz_session_id'),
        Index('idx_quiz_answers_participant_id', 'participant_id'),
        Index('idx_quiz_answers_question_id', 'question_id'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "question_id": str(self.question_id),
            "question_index": self.question_index,
            "player_answer": self.player_answer,
            "is_correct": self.is_correct,
            "time_taken_ms": self.time_taken_ms,
            "points_earned": self.points_earned,
            "time_bonus": self.time_bonus,
            "streak_bonus": self.streak_bonus,
            "total_points": self.total_points,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }


class QuizLeaderboard(Base):
    """Quiz high scores and rankings"""
    __tablename__ = "quiz_leaderboard"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("quiz_categories.id"), nullable=True)  # Null = overall

    # Leaderboard type: daily, weekly, monthly, all_time
    leaderboard_type = Column(String(20), default="all_time", nullable=False)

    # Stats
    total_games = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    highest_score = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)

    # Rankings
    rank = Column(Integer, nullable=True)

    # Period
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_quiz_leaderboard_user_id', 'user_id'),
        Index('idx_quiz_leaderboard_category_id', 'category_id'),
        Index('idx_quiz_leaderboard_type', 'leaderboard_type'),
        Index('idx_quiz_leaderboard_rank', 'rank'),
        Index('idx_quiz_leaderboard_total_points', 'total_points'),
    )

    @property
    def accuracy_rate(self) -> float:
        """Calculate overall accuracy"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "category_id": str(self.category_id) if self.category_id else None,
            "leaderboard_type": self.leaderboard_type,
            "total_games": self.total_games,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "accuracy_rate": self.accuracy_rate,
            "total_points": self.total_points,
            "highest_score": self.highest_score,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "rank": self.rank,
        }
