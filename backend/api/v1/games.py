"""
Games API Endpoints
Handles game catalog, sessions, matchmaking, and gameplay
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime
import uuid

from config.database import get_db
from middleware.auth import get_current_user
from models.user import User
from models.wallet import Wallet, Transaction
from models.game import Game, GameSession, GameParticipant, GameMove, GameResult
from models.referral import UserLevel, RewardTransaction
from schemas.game import (
    GameResponse, GameListResponse, CreateSessionRequest, JoinSessionRequest,
    GameSessionResponse, GameSessionListResponse, ParticipantResponse,
    SessionDetailsResponse, GameStateResponse, MakeMoveRequest, MakeMoveResponse,
    GameResultResponse, PlayerResultResponse, GameHistoryRequest, GameHistoryResponse,
    GameStatsResponse, UserGameStatsResponse, QuickMatchRequest, QuickMatchResponse,
    GameLeaderboardResponse, StartGameRequest, ReadyToggleRequest, LeaveSessionRequest,
    CreateGameRequest, UpdateGameRequest, GameDashboardResponse
)
from utils.game_logic import game_manager, game_state_manager
from utils.rewards import reward_calculator

router = APIRouter()


# ============================================================================
# Game Catalog Endpoints
# ============================================================================

@router.get("/catalog", response_model=GameListResponse)
async def get_game_catalog(
    category: Optional[str] = None,
    is_featured: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get list of available games"""

    query = select(Game).where(Game.is_active == True)

    if category:
        query = query.where(Game.category == category)

    if is_featured:
        query = query.where(Game.is_featured == True)

    query = query.order_by(Game.display_order, Game.name)

    result = await db.execute(query)
    games = result.scalars().all()

    # Get featured games separately
    featured_query = select(Game).where(
        and_(Game.is_active == True, Game.is_featured == True)
    ).order_by(Game.display_order).limit(5)

    featured_result = await db.execute(featured_query)
    featured_games = featured_result.scalars().all()

    game_responses = [
        GameResponse(
            id=str(g.id),
            code=g.code,
            name=g.name,
            description=g.description,
            category=g.category,
            min_players=g.min_players,
            max_players=g.max_players,
            avg_duration_minutes=g.avg_duration_minutes,
            difficulty_level=g.difficulty_level,
            min_entry_fee=g.min_entry_fee / 100,
            max_entry_fee=g.max_entry_fee / 100 if g.max_entry_fee else None,
            default_entry_fee=g.default_entry_fee / 100,
            prize_distribution=g.prize_distribution,
            rules=g.rules,
            icon_url=g.icon_url,
            banner_url=g.banner_url,
            is_active=g.is_active,
            is_featured=g.is_featured,
            is_skill_based=g.is_skill_based,
            total_sessions_played=g.total_sessions_played,
            total_players=g.total_players,
            display_order=g.display_order
        )
        for g in games
    ]

    featured_responses = [
        GameResponse(
            id=str(g.id),
            code=g.code,
            name=g.name,
            description=g.description,
            category=g.category,
            min_players=g.min_players,
            max_players=g.max_players,
            avg_duration_minutes=g.avg_duration_minutes,
            difficulty_level=g.difficulty_level,
            min_entry_fee=g.min_entry_fee / 100,
            max_entry_fee=g.max_entry_fee / 100 if g.max_entry_fee else None,
            default_entry_fee=g.default_entry_fee / 100,
            prize_distribution=g.prize_distribution,
            rules=g.rules,
            icon_url=g.icon_url,
            banner_url=g.banner_url,
            is_active=g.is_active,
            is_featured=g.is_featured,
            is_skill_based=g.is_skill_based,
            total_sessions_played=g.total_sessions_played,
            total_players=g.total_players,
            display_order=g.display_order
        )
        for g in featured_games
    ]

    return GameListResponse(
        games=game_responses,
        total_count=len(games),
        featured_games=featured_responses
    )


@router.get("/catalog/{game_id}", response_model=GameResponse)
async def get_game_details(
    game_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific game"""

    query = select(Game).where(Game.id == uuid.UUID(game_id))
    result = await db.execute(query)
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    return GameResponse(
        id=str(game.id),
        code=game.code,
        name=game.name,
        description=game.description,
        category=game.category,
        min_players=game.min_players,
        max_players=game.max_players,
        avg_duration_minutes=game.avg_duration_minutes,
        difficulty_level=game.difficulty_level,
        min_entry_fee=game.min_entry_fee / 100,
        max_entry_fee=game.max_entry_fee / 100 if game.max_entry_fee else None,
        default_entry_fee=game.default_entry_fee / 100,
        prize_distribution=game.prize_distribution,
        rules=game.rules,
        icon_url=game.icon_url,
        banner_url=game.banner_url,
        is_active=game.is_active,
        is_featured=game.is_featured,
        is_skill_based=game.is_skill_based,
        total_sessions_played=game.total_sessions_played,
        total_players=game.total_players,
        display_order=game.display_order
    )


# ============================================================================
# Game Session Management Endpoints
# ============================================================================

@router.post("/sessions/create", response_model=SessionDetailsResponse)
async def create_game_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new game session"""

    # Get game details
    game_query = select(Game).where(Game.id == uuid.UUID(request.game_id))
    game_result = await db.execute(game_query)
    game = game_result.scalar_one_or_none()

    if not game or not game.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found or inactive"
        )

    # Validate entry fee
    entry_fee_paise = int(request.entry_fee * 100)
    is_valid, message = game_manager.validate_entry_fee(
        entry_fee_paise,
        game.min_entry_fee,
        game.max_entry_fee
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Check user has sufficient balance
    wallet_query = select(Wallet).where(
        and_(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "cash"
        )
    )
    wallet_result = await db.execute(wallet_query)
    cash_wallet = wallet_result.scalar_one_or_none()

    if not cash_wallet or cash_wallet.balance < entry_fee_paise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient cash balance"
        )

    # Create session
    session_code = game_manager.generate_session_code()
    session = GameSession(
        game_id=game.id,
        session_code=session_code,
        session_type=request.session_type,
        entry_fee=entry_fee_paise,
        max_players=request.max_players,
        current_players=0,
        min_players_to_start=2,
        status="waiting",
        is_private=request.is_private,
        auto_start=True,
        platform_fee_percentage=game_manager.DEFAULT_PLATFORM_FEE_PERCENTAGE
    )

    db.add(session)
    await db.flush()

    # Auto-join creator
    colors = game_manager.assign_player_colors(request.max_players)

    participant = GameParticipant(
        session_id=session.id,
        user_id=current_user.id,
        player_position=1,
        player_color=colors[0],
        player_name=current_user.display_name or current_user.username,
        entry_fee_paid=entry_fee_paise,
        status="joined"
    )

    db.add(participant)

    # Deduct entry fee from wallet
    cash_wallet.balance -= entry_fee_paise

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        wallet_id=cash_wallet.id,
        transaction_type="debit",
        amount=entry_fee_paise,
        category="game_entry",
        status="completed",
        description=f"Entry fee for {game.name} - {session_code}"
    )
    db.add(transaction)

    participant.entry_transaction_id = transaction.id

    session.current_players = 1
    session.total_prize_pool = entry_fee_paise

    await db.commit()
    await db.refresh(session)
    await db.refresh(participant)

    # Build response
    session_response = GameSessionResponse(
        id=str(session.id),
        game_id=str(session.game_id),
        game_name=game.name,
        session_code=session.session_code,
        session_type=session.session_type,
        entry_fee=session.entry_fee / 100,
        total_prize_pool=session.total_prize_pool / 100,
        max_players=session.max_players,
        current_players=session.current_players,
        min_players_to_start=session.min_players_to_start,
        status=session.status,
        is_private=session.is_private,
        allow_spectators=session.allow_spectators,
        platform_fee_percentage=session.platform_fee_percentage,
        created_at=session.created_at,
        started_at=session.started_at,
        ended_at=session.ended_at
    )

    participant_response = ParticipantResponse(
        id=str(participant.id),
        user_id=str(participant.user_id),
        player_name=participant.player_name,
        player_position=participant.player_position,
        player_color=participant.player_color,
        entry_fee_paid=participant.entry_fee_paid / 100,
        status=participant.status,
        is_ready=participant.is_ready,
        is_spectator=participant.is_spectator,
        final_rank=participant.final_rank,
        final_score=participant.final_score,
        prize_won=participant.prize_won / 100,
        xp_earned=participant.xp_earned,
        joined_at=participant.joined_at
    )

    return SessionDetailsResponse(
        session=session_response,
        participants=[participant_response],
        current_user_participant=participant_response,
        can_start=False,
        is_user_turn=False
    )


@router.post("/sessions/join", response_model=SessionDetailsResponse)
async def join_game_session(
    request: JoinSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join an existing game session"""

    # Find session
    session_query = select(GameSession, Game).join(
        Game, GameSession.game_id == Game.id
    ).where(GameSession.session_code == request.session_code.upper())

    result = await db.execute(session_query)
    session_data = result.one_or_none()

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )

    session, game = session_data

    # Check session status
    if session.status != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot join game in {session.status} status"
        )

    # Check if session is full
    if session.current_players >= session.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game session is full"
        )

    # Check if user already joined
    existing_query = select(GameParticipant).where(
        and_(
            GameParticipant.session_id == session.id,
            GameParticipant.user_id == current_user.id
        )
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already joined this session"
        )

    # Check user balance
    wallet_query = select(Wallet).where(
        and_(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == "cash"
        )
    )
    wallet_result = await db.execute(wallet_query)
    cash_wallet = wallet_result.scalar_one_or_none()

    if not cash_wallet or cash_wallet.balance < session.entry_fee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient cash balance"
        )

    # Join session
    colors = game_manager.assign_player_colors(session.max_players)
    player_position = session.current_players + 1

    participant = GameParticipant(
        session_id=session.id,
        user_id=current_user.id,
        player_position=player_position,
        player_color=colors[player_position - 1],
        player_name=current_user.display_name or current_user.username,
        entry_fee_paid=session.entry_fee,
        status="joined"
    )

    db.add(participant)

    # Deduct entry fee
    cash_wallet.balance -= session.entry_fee

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        wallet_id=cash_wallet.id,
        transaction_type="debit",
        amount=session.entry_fee,
        category="game_entry",
        status="completed",
        description=f"Entry fee for {game.name} - {session.session_code}"
    )
    db.add(transaction)

    participant.entry_transaction_id = transaction.id

    # Update session
    session.current_players += 1
    session.total_prize_pool += session.entry_fee

    # Auto-start if full and auto_start enabled
    if session.auto_start and session.current_players == session.max_players:
        session.status = "ready"

    await db.commit()

    # Get all participants
    participants_query = select(GameParticipant).where(
        GameParticipant.session_id == session.id
    ).order_by(GameParticipant.player_position)

    participants_result = await db.execute(participants_query)
    all_participants = participants_result.scalars().all()

    # Build response
    session_response = GameSessionResponse(
        id=str(session.id),
        game_id=str(session.game_id),
        game_name=game.name,
        session_code=session.session_code,
        session_type=session.session_type,
        entry_fee=session.entry_fee / 100,
        total_prize_pool=session.total_prize_pool / 100,
        max_players=session.max_players,
        current_players=session.current_players,
        min_players_to_start=session.min_players_to_start,
        status=session.status,
        is_private=session.is_private,
        allow_spectators=session.allow_spectators,
        platform_fee_percentage=session.platform_fee_percentage,
        created_at=session.created_at,
        started_at=session.started_at,
        ended_at=session.ended_at
    )

    participant_responses = [
        ParticipantResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            player_name=p.player_name,
            player_position=p.player_position,
            player_color=p.player_color,
            entry_fee_paid=p.entry_fee_paid / 100,
            status=p.status,
            is_ready=p.is_ready,
            is_spectator=p.is_spectator,
            final_rank=p.final_rank,
            final_score=p.final_score,
            prize_won=p.prize_won / 100,
            xp_earned=p.xp_earned,
            joined_at=p.joined_at
        )
        for p in all_participants
    ]

    current_participant = next((p for p in participant_responses if p.user_id == str(current_user.id)), None)

    can_start = session.current_players >= session.min_players_to_start

    return SessionDetailsResponse(
        session=session_response,
        participants=participant_responses,
        current_user_participant=current_participant,
        can_start=can_start,
        is_user_turn=False
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a game session"""

    session_query = select(GameSession, Game).join(
        Game, GameSession.game_id == Game.id
    ).where(GameSession.id == uuid.UUID(session_id))

    result = await db.execute(session_query)
    session_data = result.one_or_none()

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )

    session, game = session_data

    # Get participants
    participants_query = select(GameParticipant).where(
        GameParticipant.session_id == session.id
    ).order_by(GameParticipant.player_position)

    participants_result = await db.execute(participants_query)
    participants = participants_result.scalars().all()

    # Build response
    session_response = GameSessionResponse(
        id=str(session.id),
        game_id=str(session.game_id),
        game_name=game.name,
        session_code=session.session_code,
        session_type=session.session_type,
        entry_fee=session.entry_fee / 100,
        total_prize_pool=session.total_prize_pool / 100,
        max_players=session.max_players,
        current_players=session.current_players,
        min_players_to_start=session.min_players_to_start,
        status=session.status,
        is_private=session.is_private,
        allow_spectators=session.allow_spectators,
        platform_fee_percentage=session.platform_fee_percentage,
        created_at=session.created_at,
        started_at=session.started_at,
        ended_at=session.ended_at
    )

    participant_responses = [
        ParticipantResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            player_name=p.player_name,
            player_position=p.player_position,
            player_color=p.player_color,
            entry_fee_paid=p.entry_fee_paid / 100,
            status=p.status,
            is_ready=p.is_ready,
            is_spectator=p.is_spectator,
            final_rank=p.final_rank,
            final_score=p.final_score,
            prize_won=p.prize_won / 100,
            xp_earned=p.xp_earned,
            joined_at=p.joined_at
        )
        for p in participants
    ]

    current_participant = next((p for p in participant_responses if p.user_id == str(current_user.id)), None)
    can_start = session.current_players >= session.min_players_to_start and session.status == "waiting"
    is_user_turn = str(session.current_turn_player_id) == str(current_user.id) if session.current_turn_player_id else False

    return SessionDetailsResponse(
        session=session_response,
        participants=participant_responses,
        current_user_participant=current_participant,
        can_start=can_start,
        is_user_turn=is_user_turn
    )


@router.get("/sessions", response_model=GameSessionListResponse)
async def list_game_sessions(
    game_id: Optional[str] = None,
    status: str = "waiting",
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List available game sessions"""

    query = select(GameSession, Game).join(
        Game, GameSession.game_id == Game.id
    )

    if game_id:
        query = query.where(GameSession.game_id == uuid.UUID(game_id))

    if status:
        query = query.where(GameSession.status == status)

    query = query.where(GameSession.is_private == False)
    query = query.order_by(desc(GameSession.created_at))
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    session_data = result.all()

    # Get counts
    count_query = select(func.count(GameSession.id)).where(
        GameSession.status == status
    )
    if game_id:
        count_query = count_query.where(GameSession.game_id == uuid.UUID(game_id))

    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    active_count_query = select(func.count(GameSession.id)).where(
        GameSession.status == "in_progress"
    )
    active_count_result = await db.execute(active_count_query)
    active_count = active_count_result.scalar()

    waiting_count_query = select(func.count(GameSession.id)).where(
        GameSession.status == "waiting"
    )
    waiting_count_result = await db.execute(waiting_count_query)
    waiting_count = waiting_count_result.scalar()

    session_responses = [
        GameSessionResponse(
            id=str(s.id),
            game_id=str(s.game_id),
            game_name=g.name,
            session_code=s.session_code,
            session_type=s.session_type,
            entry_fee=s.entry_fee / 100,
            total_prize_pool=s.total_prize_pool / 100,
            max_players=s.max_players,
            current_players=s.current_players,
            min_players_to_start=s.min_players_to_start,
            status=s.status,
            is_private=s.is_private,
            allow_spectators=s.allow_spectators,
            platform_fee_percentage=s.platform_fee_percentage,
            created_at=s.created_at,
            started_at=s.started_at,
            ended_at=s.ended_at
        )
        for s, g in session_data
    ]

    return GameSessionListResponse(
        sessions=session_responses,
        total_count=total_count,
        active_sessions=active_count,
        waiting_sessions=waiting_count
    )


# ============================================================================
# Gameplay Endpoints
# ============================================================================

@router.post("/sessions/{session_id}/start")
async def start_game(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a game session (host/ready players)"""

    session_query = select(GameSession, Game).join(
        Game, GameSession.game_id == Game.id
    ).where(GameSession.id == uuid.UUID(session_id))

    result = await db.execute(session_query)
    session_data = result.one_or_none()

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session, game = session_data

    if session.status not in ["waiting", "ready"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start game in {session.status} status"
        )

    if session.current_players < session.min_players_to_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Need at least {session.min_players_to_start} players to start"
        )

    # Initialize game state
    game_state = game_state_manager.initialize_game_state(
        game.code,
        session.current_players,
        game.game_config
    )

    session.status = "in_progress"
    session.started_at = datetime.utcnow()
    session.game_state = game_state
    session.turn_number = 1

    # Set first player
    first_participant_query = select(GameParticipant).where(
        and_(
            GameParticipant.session_id == session.id,
            GameParticipant.player_position == 1
        )
    )
    first_participant_result = await db.execute(first_participant_query)
    first_participant = first_participant_result.scalar_one_or_none()

    if first_participant:
        session.current_turn_player_id = first_participant.user_id
        session.turn_deadline = game_manager.calculate_turn_deadline()

    # Update all participants to playing
    update_participants_query = select(GameParticipant).where(
        GameParticipant.session_id == session.id
    )
    update_participants_result = await db.execute(update_participants_query)
    participants = update_participants_result.scalars().all()

    for p in participants:
        p.status = "playing"

    await db.commit()

    return {
        "success": True,
        "session_id": str(session.id),
        "status": session.status,
        "game_state": session.game_state,
        "current_turn_player_id": str(session.current_turn_player_id),
        "message": "Game started successfully!"
    }


@router.get("/sessions/{session_id}/state", response_model=GameStateResponse)
async def get_game_state(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current game state"""

    session_query = select(GameSession).where(GameSession.id == uuid.UUID(session_id))
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get participants
    participants_query = select(GameParticipant).where(
        GameParticipant.session_id == session.id
    ).order_by(GameParticipant.player_position)

    participants_result = await db.execute(participants_query)
    participants = participants_result.scalars().all()

    # Get last move
    last_move_query = select(GameMove).where(
        GameMove.session_id == session.id
    ).order_by(desc(GameMove.created_at)).limit(1)

    last_move_result = await db.execute(last_move_query)
    last_move = last_move_result.scalar_one_or_none()

    participant_responses = [
        ParticipantResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            player_name=p.player_name,
            player_position=p.player_position,
            player_color=p.player_color,
            entry_fee_paid=p.entry_fee_paid / 100,
            status=p.status,
            is_ready=p.is_ready,
            is_spectator=p.is_spectator,
            final_rank=p.final_rank,
            final_score=p.final_score,
            prize_won=p.prize_won / 100,
            xp_earned=p.xp_earned,
            joined_at=p.joined_at
        )
        for p in participants
    ]

    return GameStateResponse(
        session_id=str(session.id),
        status=session.status,
        game_state=session.game_state or {},
        current_turn_player_id=str(session.current_turn_player_id) if session.current_turn_player_id else None,
        turn_number=session.turn_number,
        turn_deadline=session.turn_deadline,
        participants=participant_responses,
        last_move=last_move.move_data if last_move else None
    )


@router.post("/sessions/{session_id}/move", response_model=MakeMoveResponse)
async def make_move(
    session_id: str,
    move_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Make a move in the game"""

    # Get session and participant
    session_query = select(GameSession).where(GameSession.id == uuid.UUID(session_id))
    result = await db.execute(session_query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress"
        )

    # Get current user's participant
    participant_query = select(GameParticipant).where(
        and_(
            GameParticipant.session_id == session.id,
            GameParticipant.user_id == current_user.id
        )
    )
    participant_result = await db.execute(participant_query)
    participant = participant_result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this game"
        )

    # Validate it's player's turn
    if session.current_turn_player_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not your turn"
        )

    # Validate move
    is_valid, message = game_state_manager.validate_move(
        session.game_state,
        move_data,
        participant.player_position
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Apply move
    old_state = session.game_state.copy()
    new_state = game_state_manager.apply_move(
        session.game_state,
        move_data,
        participant.player_position
    )

    # Save move
    game_move = GameMove(
        session_id=session.id,
        participant_id=participant.id,
        user_id=current_user.id,
        move_number=participant.moves_made + 1,
        turn_number=session.turn_number,
        move_type=move_data.get("type", "unknown"),
        move_data=move_data,
        is_valid=True,
        state_before=old_state,
        state_after=new_state
    )

    db.add(game_move)

    # Update session
    session.game_state = new_state
    session.turn_number += 1
    participant.moves_made += 1

    # Get next player
    all_participants_query = select(GameParticipant).where(
        GameParticipant.session_id == session.id
    ).order_by(GameParticipant.player_position)

    all_participants_result = await db.execute(all_participants_query)
    all_participants = all_participants_result.scalars().all()

    current_index = next((i for i, p in enumerate(all_participants) if p.id == participant.id), 0)
    next_index = (current_index + 1) % len(all_participants)
    next_participant = all_participants[next_index]

    session.current_turn_player_id = next_participant.user_id
    session.turn_deadline = game_manager.calculate_turn_deadline()

    # Check if game is over
    is_over, winner_position = game_state_manager.check_game_over(new_state)

    await db.commit()

    return MakeMoveResponse(
        success=True,
        move_id=str(game_move.id),
        game_state=new_state,
        next_player_id=str(next_participant.user_id) if not is_over else None,
        is_game_over=is_over,
        message="Move successful" if not is_over else "Game Over!"
    )


# ============================================================================
# Game Results Endpoints
# ============================================================================

@router.post("/history", response_model=GameHistoryResponse)
async def get_game_history(
    request: GameHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's game history"""

    # Get user's participations
    query = (
        select(GameResult, Game, GameParticipant)
        .join(Game, GameResult.game_id == Game.id)
        .join(GameParticipant, GameResult.session_id == GameParticipant.session_id)
        .where(GameParticipant.user_id == current_user.id)
    )

    if request.game_id:
        query = query.where(GameResult.game_id == uuid.UUID(request.game_id))

    query = query.order_by(desc(GameResult.created_at))
    query = query.limit(request.limit).offset(request.offset)

    result = await db.execute(query)
    history_data = result.all()

    # Get stats
    stats_query = select(
        func.count(GameParticipant.id),
        func.sum(func.case((GameParticipant.final_rank == 1, 1), else_=0)),
        func.sum(GameParticipant.prize_won),
        func.sum(GameParticipant.xp_earned)
    ).where(GameParticipant.user_id == current_user.id)

    stats_result = await db.execute(stats_query)
    total_games, total_wins, total_winnings, total_xp = stats_result.one()

    game_results = []
    for game_result, game, participant in history_data:
        player_results = [
            PlayerResultResponse(
                user_id=r["user_id"],
                player_name=r["player_name"],
                rank=r["rank"],
                score=r.get("score", 0),
                prize_won=r.get("prize", 0) / 100,
                xp_earned=r.get("xp_earned", 0),
                achievements_unlocked=r.get("achievements", [])
            )
            for r in game_result.final_rankings
        ]

        game_results.append(GameResultResponse(
            id=str(game_result.id),
            session_id=str(game_result.session_id),
            game_id=str(game_result.game_id),
            game_name=game.name,
            winner_id=str(game_result.winner_id) if game_result.winner_id else None,
            winner_name=game_result.winner_name,
            winning_prize=game_result.winning_prize / 100,
            final_rankings=player_results,
            total_players=game_result.total_players,
            total_moves=game_result.total_moves,
            total_duration_seconds=game_result.total_duration_seconds,
            total_prize_pool=game_result.total_prize_pool / 100,
            platform_fee_collected=game_result.platform_fee_collected / 100,
            prizes_distributed=game_result.prizes_distributed,
            game_started_at=game_result.game_started_at,
            game_ended_at=game_result.game_ended_at
        ))

    win_rate = (total_wins / total_games * 100) if total_games and total_wins else 0.0

    return GameHistoryResponse(
        games=game_results,
        total_count=len(game_results),
        total_games_played=total_games or 0,
        total_games_won=total_wins or 0,
        total_winnings=(total_winnings or 0) / 100,
        total_xp_earned=total_xp or 0,
        win_rate=win_rate
    )


# ============================================================================
# Dashboard Endpoint
# ============================================================================

@router.get("/dashboard", response_model=GameDashboardResponse)
async def get_game_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's game dashboard with all relevant info"""

    # Get active sessions
    active_query = (
        select(GameSession, Game)
        .join(Game, GameSession.game_id == Game.id)
        .join(GameParticipant, GameSession.id == GameParticipant.session_id)
        .where(
            and_(
                GameParticipant.user_id == current_user.id,
                GameSession.status.in_(["waiting", "ready", "in_progress"])
            )
        )
    )

    active_result = await db.execute(active_query)
    active_data = active_result.all()

    active_sessions = [
        GameSessionResponse(
            id=str(s.id),
            game_id=str(s.game_id),
            game_name=g.name,
            session_code=s.session_code,
            session_type=s.session_type,
            entry_fee=s.entry_fee / 100,
            total_prize_pool=s.total_prize_pool / 100,
            max_players=s.max_players,
            current_players=s.current_players,
            min_players_to_start=s.min_players_to_start,
            status=s.status,
            is_private=s.is_private,
            allow_spectators=s.allow_spectators,
            platform_fee_percentage=s.platform_fee_percentage,
            created_at=s.created_at,
            started_at=s.started_at,
            ended_at=s.ended_at
        )
        for s, g in active_data
    ]

    # Get featured games
    featured_games_query = select(Game).where(
        and_(Game.is_active == True, Game.is_featured == True)
    ).limit(5)

    featured_result = await db.execute(featured_games_query)
    featured_games_data = featured_result.scalars().all()

    # Get all available games
    available_games_query = select(Game).where(Game.is_active == True).limit(10)
    available_result = await db.execute(available_games_query)
    available_games_data = available_result.scalars().all()

    # Build stats (simplified version)
    stats = UserGameStatsResponse(
        total_games_played=0,
        total_games_won=0,
        total_winnings=0.0,
        total_losses=0.0,
        overall_win_rate=0.0,
        total_xp_earned=0,
        favorite_game=None,
        game_stats=[]
    )

    featured_games = [
        GameResponse(
            id=str(g.id),
            code=g.code,
            name=g.name,
            description=g.description,
            category=g.category,
            min_players=g.min_players,
            max_players=g.max_players,
            avg_duration_minutes=g.avg_duration_minutes,
            difficulty_level=g.difficulty_level,
            min_entry_fee=g.min_entry_fee / 100,
            max_entry_fee=g.max_entry_fee / 100 if g.max_entry_fee else None,
            default_entry_fee=g.default_entry_fee / 100,
            prize_distribution=g.prize_distribution,
            rules=g.rules,
            icon_url=g.icon_url,
            banner_url=g.banner_url,
            is_active=g.is_active,
            is_featured=g.is_featured,
            is_skill_based=g.is_skill_based,
            total_sessions_played=g.total_sessions_played,
            total_players=g.total_players,
            display_order=g.display_order
        )
        for g in featured_games_data
    ]

    available_games = [
        GameResponse(
            id=str(g.id),
            code=g.code,
            name=g.name,
            description=g.description,
            category=g.category,
            min_players=g.min_players,
            max_players=g.max_players,
            avg_duration_minutes=g.avg_duration_minutes,
            difficulty_level=g.difficulty_level,
            min_entry_fee=g.min_entry_fee / 100,
            max_entry_fee=g.max_entry_fee / 100 if g.max_entry_fee else None,
            default_entry_fee=g.default_entry_fee / 100,
            prize_distribution=g.prize_distribution,
            rules=g.rules,
            icon_url=g.icon_url,
            banner_url=g.banner_url,
            is_active=g.is_active,
            is_featured=g.is_featured,
            is_skill_based=g.is_skill_based,
            total_sessions_played=g.total_sessions_played,
            total_players=g.total_players,
            display_order=g.display_order
        )
        for g in available_games_data
    ]

    return GameDashboardResponse(
        active_sessions=active_sessions,
        recent_results=[],
        game_stats=stats,
        available_games=available_games,
        featured_games=featured_games,
        quick_match_available=True
    )
