"""
Game Models
SQLAlchemy models for game management, sessions, and results
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from config.database import Base
import uuid


class Game(Base):
    """Game catalog - available games on platform"""
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Game details
    code = Column(String(50), unique=True, nullable=False, index=True)  # ludo, rummy, poker
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(30), nullable=False)  # board, card, quiz, casual

    # Game metadata
    min_players = Column(Integer, default=2)
    max_players = Column(Integer, default=4)
    avg_duration_minutes = Column(Integer, default=10)
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard

    # Entry fees and prizes (in paise)
    min_entry_fee = Column(Integer, default=0)
    max_entry_fee = Column(Integer, nullable=True)
    default_entry_fee = Column(Integer, default=10000)  # Rs.100

    # Prize distribution (JSON)
    prize_distribution = Column(JSONB, default={}, nullable=True)
    # Example: {"1st": 70, "2nd": 20, "3rd": 10}  # Percentages

    # Game rules and configuration
    rules = Column(JSONB, default={}, nullable=True)
    game_config = Column(JSONB, default={}, nullable=True)

    # Visual assets
    icon_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_skill_based = Column(Boolean, default=True)  # For legal compliance

    # Stats
    total_sessions_played = Column(Integer, default=0)
    total_players = Column(Integer, default=0)
    total_prize_distributed = Column(Integer, default=0)  # in paise

    # Display order
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_games_category', 'category'),
        Index('idx_games_active', 'is_active'),
        Index('idx_games_featured', 'is_featured'),
    )


class GameSession(Base):
    """Active game sessions"""
    __tablename__ = "game_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)

    # Session details
    session_code = Column(String(10), unique=True, nullable=False, index=True)  # Public room code
    session_type = Column(String(20), nullable=False)  # public, private, tournament

    # Entry fee
    entry_fee = Column(Integer, nullable=False)  # in paise
    total_prize_pool = Column(Integer, default=0)  # in paise

    # Player configuration
    max_players = Column(Integer, nullable=False)
    current_players = Column(Integer, default=0)
    min_players_to_start = Column(Integer, default=2)

    # Session status
    status = Column(String(20), default="waiting", nullable=False)
    # waiting, ready, in_progress, completed, cancelled, abandoned

    # Game state (JSON - flexible for different game types)
    game_state = Column(JSONB, default={}, nullable=True)
    # Example for Ludo: {"board": [...], "current_player": "user_id", "turn": 5}

    current_turn_player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    turn_number = Column(Integer, default=0)
    turn_deadline = Column(DateTime(timezone=True), nullable=True)  # Auto-skip if exceeded

    # Results
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    winning_amount = Column(Integer, default=0)  # in paise
    result_data = Column(JSONB, default={}, nullable=True)  # Detailed results

    # Settings
    is_private = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=True)  # For private rooms
    auto_start = Column(Boolean, default=True)  # Start when max players joined
    allow_spectators = Column(Boolean, default=True)

    # Platform commission
    platform_fee_percentage = Column(Float, default=5.0)  # 5% platform fee
    platform_fee_amount = Column(Integer, default=0)  # in paise

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_game_sessions_game_id', 'game_id'),
        Index('idx_game_sessions_status', 'status'),
        Index('idx_game_sessions_session_code', 'session_code'),
        Index('idx_game_sessions_created_at', 'created_at'),
    )


class GameParticipant(Base):
    """Players participating in a game session"""
    __tablename__ = "game_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Participant details
    player_position = Column(Integer, nullable=False)  # 1, 2, 3, 4 (for turn order)
    player_color = Column(String(20), nullable=True)  # red, blue, green, yellow
    player_name = Column(String(100), nullable=False)  # Cached display name

    # Entry
    entry_fee_paid = Column(Integer, nullable=False)  # in paise
    entry_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)

    # Status
    status = Column(String(20), default="joined", nullable=False)
    # joined, ready, playing, finished, disconnected, forfeited

    is_ready = Column(Boolean, default=False)
    is_spectator = Column(Boolean, default=False)

    # Results
    final_rank = Column(Integer, nullable=True)  # 1st, 2nd, 3rd, 4th
    final_score = Column(Integer, default=0)
    prize_won = Column(Integer, default=0)  # in paise
    prize_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)

    # XP and rewards earned
    xp_earned = Column(Integer, default=0)
    achievements_unlocked = Column(JSONB, default=[], nullable=True)  # List of achievement IDs

    # Player stats for this game
    moves_made = Column(Integer, default=0)
    total_play_time_seconds = Column(Integer, default=0)

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_game_participants_session_id', 'session_id'),
        Index('idx_game_participants_user_id', 'user_id'),
        Index('idx_game_participants_session_user', 'session_id', 'user_id', unique=True),
        Index('idx_game_participants_status', 'status'),
    )


class GameMove(Base):
    """Individual moves/actions in a game session"""
    __tablename__ = "game_moves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("game_participants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Move details
    move_number = Column(Integer, nullable=False)  # Sequential move number in game
    turn_number = Column(Integer, nullable=False)  # Which turn this move was made

    move_type = Column(String(30), nullable=False)  # roll_dice, move_piece, play_card, answer_question
    move_data = Column(JSONB, nullable=False)  # Flexible JSON for different game types
    # Example: {"dice": 6, "piece_id": "red_1", "from": 0, "to": 6}

    # Validation
    is_valid = Column(Boolean, default=True)
    validation_message = Column(Text, nullable=True)

    # State before/after
    state_before = Column(JSONB, nullable=True)  # Game state before this move
    state_after = Column(JSONB, nullable=True)   # Game state after this move

    # Timing
    time_taken_ms = Column(Integer, default=0)  # Time taken to make this move

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_game_moves_session_id', 'session_id'),
        Index('idx_game_moves_participant_id', 'participant_id'),
        Index('idx_game_moves_user_id', 'user_id'),
        Index('idx_game_moves_created_at', 'created_at'),
    )


class GameResult(Base):
    """Final results and statistics for completed games"""
    __tablename__ = "game_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)

    # Winner
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    winner_name = Column(String(100), nullable=True)
    winning_prize = Column(Integer, default=0)  # in paise

    # All participants and rankings (JSON)
    final_rankings = Column(JSONB, nullable=False)
    # Example: [{"user_id": "...", "rank": 1, "score": 100, "prize": 7000}, ...]

    # Game statistics
    total_players = Column(Integer, nullable=False)
    total_moves = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    total_prize_pool = Column(Integer, default=0)  # in paise
    platform_fee_collected = Column(Integer, default=0)  # in paise

    # Prize distribution status
    prizes_distributed = Column(Boolean, default=False)
    prize_distribution_at = Column(DateTime(timezone=True), nullable=True)

    # XP and achievements
    total_xp_distributed = Column(Integer, default=0)
    achievements_triggered = Column(JSONB, default=[], nullable=True)

    # Leaderboard updates
    leaderboard_updated = Column(Boolean, default=False)

    # Game metadata
    game_data = Column(JSONB, default={}, nullable=True)  # Any additional game-specific data

    # Fair play
    is_verified = Column(Boolean, default=True)
    fairplay_flags = Column(JSONB, default=[], nullable=True)  # Any suspicious activities

    # Timestamps
    game_started_at = Column(DateTime(timezone=True), nullable=False)
    game_ended_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_game_results_session_id', 'session_id'),
        Index('idx_game_results_game_id', 'game_id'),
        Index('idx_game_results_winner_id', 'winner_id'),
        Index('idx_game_results_created_at', 'created_at'),
    )
