"""
WebSocket Manager for Real-time Game Features
Handles WebSocket connections, game state synchronization, and real-time notifications
"""

from typing import Dict, Set, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from models.game import GameSession
from models.user import User


class ConnectionManager:
    """Manages WebSocket connections for real-time features"""

    def __init__(self):
        # Map of game_session_id -> Set of WebSocket connections
        self.game_connections: Dict[str, Set[WebSocket]] = {}

        # Map of user_id -> WebSocket connection (for user-level notifications)
        self.user_connections: Dict[str, WebSocket] = {}

        # Map of WebSocket -> user_id (for reverse lookup)
        self.websocket_to_user: Dict[WebSocket, str] = {}

        # Active lobbies
        self.lobbies: Dict[str, Set[str]] = {}  # lobby_id -> Set of user_ids

    async def connect_to_game(
        self,
        websocket: WebSocket,
        game_session_id: str,
        user_id: str
    ):
        """Connect a user to a game session via WebSocket"""
        await websocket.accept()

        # Add to game connections
        if game_session_id not in self.game_connections:
            self.game_connections[game_session_id] = set()
        self.game_connections[game_session_id].add(websocket)

        # Add to user connections
        self.user_connections[user_id] = websocket
        self.websocket_to_user[websocket] = user_id

        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": "connection",
                "status": "connected",
                "game_session_id": game_session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def connect_user(self, websocket: WebSocket, user_id: str):
        """Connect a user for general notifications (not game-specific)"""
        await websocket.accept()
        self.user_connections[user_id] = websocket
        self.websocket_to_user[websocket] = user_id

        await self.send_personal_message(
            websocket,
            {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket connection"""
        # Remove from user connections
        if websocket in self.websocket_to_user:
            user_id = self.websocket_to_user[websocket]
            if user_id in self.user_connections:
                del self.user_connections[user_id]
            del self.websocket_to_user[websocket]

        # Remove from game connections
        for game_id, connections in self.game_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if len(connections) == 0:
                    del self.game_connections[game_id]
                break

    async def send_personal_message(
        self,
        websocket: WebSocket,
        message: dict
    ):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect(websocket)

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await self.send_personal_message(websocket, message)

    async def broadcast_to_game(
        self,
        game_session_id: str,
        message: dict,
        exclude: Optional[Set[str]] = None
    ):
        """Broadcast message to all connections in a game session"""
        if game_session_id not in self.game_connections:
            return

        connections = self.game_connections[game_session_id]

        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        disconnected = []

        for websocket in connections:
            # Skip excluded users
            if exclude:
                user_id = self.websocket_to_user.get(websocket)
                if user_id in exclude:
                    continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to game: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        disconnected = []

        for websocket in self.user_connections.values():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to all: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

    async def send_game_state_update(
        self,
        game_session_id: str,
        state: dict
    ):
        """Send game state update to all players in a session"""
        message = {
            "type": "game_state_update",
            "game_session_id": game_session_id,
            "state": state,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_player_joined(
        self,
        game_session_id: str,
        user_id: str,
        username: str
    ):
        """Notify all players that a new player joined"""
        message = {
            "type": "player_joined",
            "game_session_id": game_session_id,
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_player_left(
        self,
        game_session_id: str,
        user_id: str,
        username: str
    ):
        """Notify all players that a player left"""
        message = {
            "type": "player_left",
            "game_session_id": game_session_id,
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_game_started(self, game_session_id: str):
        """Notify all players that the game has started"""
        message = {
            "type": "game_started",
            "game_session_id": game_session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_game_ended(
        self,
        game_session_id: str,
        winner_id: Optional[str] = None,
        results: Optional[dict] = None
    ):
        """Notify all players that the game has ended"""
        message = {
            "type": "game_ended",
            "game_session_id": game_session_id,
            "winner_id": winner_id,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_turn_change(
        self,
        game_session_id: str,
        current_turn_user_id: str,
        next_turn_user_id: Optional[str] = None
    ):
        """Notify players about turn change"""
        message = {
            "type": "turn_change",
            "game_session_id": game_session_id,
            "current_turn_user_id": current_turn_user_id,
            "next_turn_user_id": next_turn_user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_move_made(
        self,
        game_session_id: str,
        user_id: str,
        move_data: dict
    ):
        """Notify players about a move made"""
        message = {
            "type": "move_made",
            "game_session_id": game_session_id,
            "user_id": user_id,
            "move": move_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message)

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None
    ):
        """Send notification to a specific user"""
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_user(user_id, notification)

    def get_connected_players(self, game_session_id: str) -> int:
        """Get number of connected players for a game session"""
        if game_session_id not in self.game_connections:
            return 0
        return len(self.game_connections[game_session_id])

    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user is connected"""
        return user_id in self.user_connections

    async def send_chat_message(
        self,
        game_session_id: str,
        user_id: str,
        username: str,
        message: str
    ):
        """Send chat message to all players in a game"""
        message_data = {
            "type": "chat_message",
            "game_session_id": game_session_id,
            "user_id": user_id,
            "username": username,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_game(game_session_id, message_data)


# Global connection manager instance
manager = ConnectionManager()
