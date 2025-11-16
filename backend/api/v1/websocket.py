"""
WebSocket API Endpoints for Real-time Features
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
from datetime import datetime

from database import get_db
from models.user import User
from models.game import GameSession, GameSessionPlayer
from websocket_manager import manager
from api.v1.auth import get_current_user_ws

router = APIRouter()


@router.websocket("/ws/game/{game_session_id}")
async def game_websocket(
    websocket: WebSocket,
    game_session_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time game updates

    Usage:
    ws://localhost:8000/api/v1/ws/game/{game_session_id}?token=<jwt_token>
    """

    # Authenticate user
    try:
        user = await get_current_user_ws(token, db)
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return

    # Verify game session exists
    result = await db.execute(
        select(GameSession).where(GameSession.id == game_session_id)
    )
    game_session = result.scalar_one_or_none()

    if not game_session:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Game session not found")
        return

    # Verify user is a player in this game
    result = await db.execute(
        select(GameSessionPlayer).where(
            GameSessionPlayer.game_session_id == game_session_id,
            GameSessionPlayer.user_id == user.id
        )
    )
    player = result.scalar_one_or_none()

    if not player:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not a player in this game")
        return

    # Connect to game
    await manager.connect_to_game(websocket, game_session_id, user.id)

    # Notify other players
    await manager.send_player_joined(game_session_id, user.id, user.username)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            # Handle different message types
            if message_type == "move":
                # Handle game move
                move_data = message.get("move")
                await handle_game_move(
                    game_session_id,
                    user.id,
                    move_data,
                    db
                )

                # Broadcast move to other players
                await manager.send_move_made(
                    game_session_id,
                    user.id,
                    move_data
                )

            elif message_type == "chat":
                # Handle chat message
                chat_message = message.get("message", "")
                if chat_message.strip():
                    await manager.send_chat_message(
                        game_session_id,
                        user.id,
                        user.username,
                        chat_message
                    )

            elif message_type == "game_state_request":
                # Send current game state
                await send_game_state(game_session_id, websocket, db)

            elif message_type == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    websocket,
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket)
        await manager.send_player_left(game_session_id, user.id, user.username)

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        await manager.send_player_left(game_session_id, user.id, user.username)


@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications

    Usage:
    ws://localhost:8000/api/v1/ws/notifications?token=<jwt_token>
    """

    # Authenticate user
    try:
        user = await get_current_user_ws(token, db)
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return

    # Connect user
    await manager.connect_user(websocket, user.id)

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await manager.send_personal_message(
                    websocket,
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_game_move(
    game_session_id: str,
    user_id: str,
    move_data: dict,
    db: AsyncSession
):
    """Handle a game move and update game state"""

    # Get game session
    result = await db.execute(
        select(GameSession).where(GameSession.id == game_session_id)
    )
    game_session = result.scalar_one_or_none()

    if not game_session:
        return

    # Validate move (game-specific logic would go here)
    # For now, just update the game state

    # Update game state
    current_state = game_session.game_state or {}

    # Add move to history
    if "moves" not in current_state:
        current_state["moves"] = []

    current_state["moves"].append({
        "user_id": user_id,
        "move": move_data,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Update last move
    current_state["last_move"] = {
        "user_id": user_id,
        "move": move_data,
        "timestamp": datetime.utcnow().isoformat()
    }

    game_session.game_state = current_state
    game_session.updated_at = datetime.utcnow()

    await db.commit()

    # Broadcast updated state to all players
    await manager.send_game_state_update(game_session_id, current_state)


async def send_game_state(
    game_session_id: str,
    websocket: WebSocket,
    db: AsyncSession
):
    """Send current game state to a specific connection"""

    # Get game session
    result = await db.execute(
        select(GameSession).where(GameSession.id == game_session_id)
    )
    game_session = result.scalar_one_or_none()

    if not game_session:
        return

    # Get all players
    result = await db.execute(
        select(GameSessionPlayer, User)
        .join(User, GameSessionPlayer.user_id == User.id)
        .where(GameSessionPlayer.game_session_id == game_session_id)
    )
    players = result.all()

    # Build game state response
    state = {
        "type": "game_state",
        "game_session_id": game_session_id,
        "status": game_session.status,
        "game_state": game_session.game_state or {},
        "players": [
            {
                "user_id": player.GameSessionPlayer.user_id,
                "username": user.username,
                "position": player.GameSessionPlayer.position,
                "score": player.GameSessionPlayer.score,
                "status": player.GameSessionPlayer.status
            }
            for player, user in players
        ],
        "started_at": game_session.started_at.isoformat() if game_session.started_at else None,
        "ended_at": game_session.ended_at.isoformat() if game_session.ended_at else None,
        "timestamp": datetime.utcnow().isoformat()
    }

    await manager.send_personal_message(websocket, state)
