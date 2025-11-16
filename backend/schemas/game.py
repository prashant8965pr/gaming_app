"""
Game Schemas
Pydantic models for game-related requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# Game Catalog Schemas
# ============================================================================

class GameResponse(BaseModel):
    """Game catalog response"""
    id: str
    code: str
    name: str
    description: Optional[str]
    category: str
    min_players: int
    max_players: int
    avg_duration_minutes: int
    difficulty_level: str
    min_entry_fee: float
    max_entry_fee: Optional[float]
    default_entry_fee: float
    prize_distribution: Dict[str, Any]
    rules: Dict[str, Any]
    icon_url: Optional[str]
    banner_url: Optional[str]
    is_active: bool
    is_featured: bool
    is_skill_based: bool
    total_sessions_played: int
    total_players: int
    display_order: int

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    """List of games response"""
    games: List[GameResponse]
    total_count: int
    featured_games: List[GameResponse]


# ============================================================================
# Game Session Schemas
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request to create a new game session"""
    game_id: str = Field(..., example="uuid")
    entry_fee: float = Field(..., ge=0, example=100.0)
    session_type: str = Field(default="public", example="public")
    max_players: int = Field(default=4, ge=2, le=10, example=4)
    is_private: bool = Field(default=False, example=False)
    password: Optional[str] = Field(None, min_length=4, max_length=20)

    @validator('session_type')
    def validate_session_type(cls, v):
        allowed_types = ['public', 'private', 'tournament']
        if v not in allowed_types:
            raise ValueError(f'Invalid session type. Must be one of: {", ".join(allowed_types)}')
        return v


class JoinSessionRequest(BaseModel):
    """Request to join an existing game session"""
    session_code: str = Field(..., min_length=6, max_length=10, example="ABCD1234")
    password: Optional[str] = Field(None, example="1234")


class GameSessionResponse(BaseModel):
    """Game session details response"""
    id: str
    game_id: str
    game_name: str
    session_code: str
    session_type: str
    entry_fee: float
    total_prize_pool: float
    max_players: int
    current_players: int
    min_players_to_start: int
    status: str
    is_private: bool
    allow_spectators: bool
    platform_fee_percentage: float
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class GameSessionListResponse(BaseModel):
    """List of game sessions"""
    sessions: List[GameSessionResponse]
    total_count: int
    active_sessions: int
    waiting_sessions: int


# ============================================================================
# Game Participant Schemas
# ============================================================================

class ParticipantResponse(BaseModel):
    """Game participant response"""
    id: str
    user_id: str
    player_name: str
    player_position: int
    player_color: Optional[str]
    entry_fee_paid: float
    status: str
    is_ready: bool
    is_spectator: bool
    final_rank: Optional[int]
    final_score: int
    prize_won: float
    xp_earned: int
    joined_at: datetime

    class Config:
        from_attributes = True


class SessionDetailsResponse(BaseModel):
    """Detailed game session with participants"""
    session: GameSessionResponse
    participants: List[ParticipantResponse]
    current_user_participant: Optional[ParticipantResponse]
    can_start: bool
    is_user_turn: bool


# ============================================================================
# Game State Schemas
# ============================================================================

class GameStateResponse(BaseModel):
    """Current game state response"""
    session_id: str
    status: str
    game_state: Dict[str, Any]
    current_turn_player_id: Optional[str]
    turn_number: int
    turn_deadline: Optional[datetime]
    participants: List[ParticipantResponse]
    last_move: Optional[Dict[str, Any]]


class MakeMoveRequest(BaseModel):
    """Request to make a move in the game"""
    session_id: str = Field(..., example="uuid")
    move_type: str = Field(..., example="roll_dice")
    move_data: Dict[str, Any] = Field(..., example={"dice": 6, "piece_id": "red_1"})

    @validator('move_type')
    def validate_move_type(cls, v):
        allowed_types = ['roll_dice', 'move_piece', 'play_card', 'answer_question', 'skip_turn', 'forfeit']
        if v not in allowed_types:
            raise ValueError(f'Invalid move type. Must be one of: {", ".join(allowed_types)}')
        return v


class MakeMoveResponse(BaseModel):
    """Response after making a move"""
    success: bool
    move_id: str
    game_state: Dict[str, Any]
    next_player_id: Optional[str]
    is_game_over: bool
    message: str


# ============================================================================
# Game Result Schemas
# ============================================================================

class PlayerResultResponse(BaseModel):
    """Individual player result"""
    user_id: str
    player_name: str
    rank: int
    score: int
    prize_won: float
    xp_earned: int
    achievements_unlocked: List[str]


class GameResultResponse(BaseModel):
    """Game result response"""
    id: str
    session_id: str
    game_id: str
    game_name: str
    winner_id: Optional[str]
    winner_name: Optional[str]
    winning_prize: float
    final_rankings: List[PlayerResultResponse]
    total_players: int
    total_moves: int
    total_duration_seconds: int
    total_prize_pool: float
    platform_fee_collected: float
    prizes_distributed: bool
    game_started_at: datetime
    game_ended_at: datetime

    class Config:
        from_attributes = True


class GameHistoryRequest(BaseModel):
    """Request for game history"""
    game_id: Optional[str] = Field(None, example="uuid")
    status: Optional[str] = Field(None, example="completed")
    limit: int = Field(default=20, ge=1, le=100, example=20)
    offset: int = Field(default=0, ge=0, example=0)


class GameHistoryResponse(BaseModel):
    """User's game history response"""
    games: List[GameResultResponse]
    total_count: int
    total_games_played: int
    total_games_won: int
    total_winnings: float
    total_xp_earned: int
    win_rate: float


# ============================================================================
# Game Statistics Schemas
# ============================================================================

class GameStatsResponse(BaseModel):
    """Game statistics for a user"""
    game_id: str
    game_name: str
    total_games_played: int
    total_games_won: int
    total_winnings: float
    total_losses: float
    win_rate: float
    avg_score: float
    best_rank: int
    total_xp_earned: int
    favorite_game: bool


class UserGameStatsResponse(BaseModel):
    """User's overall game statistics"""
    total_games_played: int
    total_games_won: int
    total_winnings: float
    total_losses: float
    overall_win_rate: float
    total_xp_earned: int
    favorite_game: Optional[GameStatsResponse]
    game_stats: List[GameStatsResponse]


# ============================================================================
# Matchmaking Schemas
# ============================================================================

class QuickMatchRequest(BaseModel):
    """Request for quick match"""
    game_id: str = Field(..., example="uuid")
    entry_fee: float = Field(..., ge=0, example=100.0)
    skill_based: bool = Field(default=True, example=True)


class QuickMatchResponse(BaseModel):
    """Quick match response"""
    matched: bool
    session_id: Optional[str]
    session_code: Optional[str]
    estimated_wait_time_seconds: Optional[int]
    queue_position: Optional[int]
    message: str


# ============================================================================
# Leaderboard Update Schemas
# ============================================================================

class GameLeaderboardEntry(BaseModel):
    """Game leaderboard entry"""
    rank: int
    user_id: str
    username: str
    display_name: Optional[str]
    total_wins: int
    total_games: int
    win_rate: float
    total_winnings: float
    avg_score: float


class GameLeaderboardResponse(BaseModel):
    """Game-specific leaderboard"""
    game_id: str
    game_name: str
    period: str
    entries: List[GameLeaderboardEntry]
    total_count: int
    user_rank: Optional[int]


# ============================================================================
# Action Schemas
# ============================================================================

class StartGameRequest(BaseModel):
    """Request to start a game (host only)"""
    session_id: str = Field(..., example="uuid")


class ReadyToggleRequest(BaseModel):
    """Toggle ready status"""
    session_id: str = Field(..., example="uuid")


class LeaveSessionRequest(BaseModel):
    """Leave a game session"""
    session_id: str = Field(..., example="uuid")
    forfeit: bool = Field(default=False, example=False)


class SpectateSessionRequest(BaseModel):
    """Join as spectator"""
    session_code: str = Field(..., min_length=6, max_length=10, example="ABCD1234")


# ============================================================================
# Admin Schemas
# ============================================================================

class CreateGameRequest(BaseModel):
    """Admin request to create a new game"""
    code: str = Field(..., min_length=3, max_length=50, example="ludo")
    name: str = Field(..., min_length=3, max_length=100, example="Ludo Classic")
    description: Optional[str] = Field(None, example="Classic board game")
    category: str = Field(..., example="board")
    min_players: int = Field(default=2, ge=2, le=10)
    max_players: int = Field(default=4, ge=2, le=10)
    avg_duration_minutes: int = Field(default=10, ge=1, le=120)
    difficulty_level: str = Field(default="medium", example="medium")
    min_entry_fee: float = Field(default=0, ge=0, example=10.0)
    max_entry_fee: Optional[float] = Field(None, example=10000.0)
    default_entry_fee: float = Field(default=100.0, ge=0, example=100.0)
    prize_distribution: Dict[str, Any] = Field(default={"1st": 70, "2nd": 20, "3rd": 10})
    rules: Dict[str, Any] = Field(default={})
    game_config: Dict[str, Any] = Field(default={})
    is_skill_based: bool = Field(default=True)

    @validator('code')
    def validate_code(cls, v):
        code = v.lower().strip().replace(' ', '_')
        if not code.replace('_', '').isalnum():
            raise ValueError('Game code must be alphanumeric')
        return code

    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['board', 'card', 'quiz', 'casual', 'sports', 'puzzle']
        if v not in allowed_categories:
            raise ValueError(f'Invalid category. Must be one of: {", ".join(allowed_categories)}')
        return v

    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        allowed_levels = ['easy', 'medium', 'hard', 'expert']
        if v not in allowed_levels:
            raise ValueError(f'Invalid difficulty. Must be one of: {", ".join(allowed_levels)}')
        return v


class UpdateGameRequest(BaseModel):
    """Admin request to update a game"""
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    default_entry_fee: Optional[float] = None
    prize_distribution: Optional[Dict[str, Any]] = None


# ============================================================================
# Dashboard Schemas
# ============================================================================

class GameDashboardResponse(BaseModel):
    """User's game dashboard"""
    active_sessions: List[GameSessionResponse]
    recent_results: List[GameResultResponse]
    game_stats: UserGameStatsResponse
    available_games: List[GameResponse]
    featured_games: List[GameResponse]
    quick_match_available: bool
