"""
Integration tests for Games API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.games
class TestGameCatalog:
    """Test game catalog endpoints"""

    async def test_get_game_catalog(self, client: AsyncClient, test_game):
        """Test getting game catalog"""
        response = await client.get("/api/v1/games/catalog")

        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert len(data["games"]) > 0
        assert data["games"][0]["code"] == test_game.code

    async def test_get_game_details(self, client: AsyncClient, test_game):
        """Test getting specific game details"""
        response = await client.get(f"/api/v1/games/catalog/{test_game.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_game.id)
        assert data["name"] == test_game.name

    async def test_get_nonexistent_game(self, client: AsyncClient):
        """Test getting non-existent game"""
        import uuid
        fake_id = str(uuid.uuid4())

        response = await client.get(f"/api/v1/games/catalog/{fake_id}")

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.games
class TestGameSessionCreate:
    """Test game session creation"""

    async def test_create_game_session(
        self,
        client: AsyncClient,
        test_game,
        test_user,
        test_wallets,
        auth_headers
    ):
        """Test creating a new game session"""
        response = await client.post(
            "/api/v1/games/sessions/create",
            headers=auth_headers,
            json={
                "game_id": str(test_game.id),
                "entry_fee": 100.0,
                "session_type": "public",
                "max_players": 4,
                "is_private": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert data["session"]["entry_fee"] == 100.0
        assert data["session"]["current_players"] == 1
        assert len(data["participants"]) == 1

    async def test_create_session_insufficient_balance(
        self,
        client: AsyncClient,
        test_game,
        test_user,
        auth_headers
    ):
        """Test creating session without sufficient balance"""
        response = await client.post(
            "/api/v1/games/sessions/create",
            headers=auth_headers,
            json={
                "game_id": str(test_game.id),
                "entry_fee": 100000.0,  # Very high entry fee
                "session_type": "public",
                "max_players": 4
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "Insufficient" in data["detail"]

    async def test_create_session_unauthorized(self, client: AsyncClient, test_game):
        """Test creating session without auth"""
        response = await client.post(
            "/api/v1/games/sessions/create",
            json={
                "game_id": str(test_game.id),
                "entry_fee": 100.0
            }
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.games
class TestGameSessionJoin:
    """Test joining game sessions"""

    async def test_join_game_session(
        self,
        client: AsyncClient,
        test_game_session,
        test_user_2,
        test_wallets,
        db_session
    ):
        """Test joining an existing game session"""
        # Create wallets for user 2
        from models.wallet import Wallet
        import uuid

        wallet = Wallet(
            id=uuid.uuid4(),
            user_id=test_user_2.id,
            wallet_type="cash",
            balance=100000
        )
        db_session.add(wallet)
        await db_session.commit()

        # Create token for user 2
        from middleware.auth import create_access_token
        token = create_access_token({"sub": str(test_user_2.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/games/sessions/join",
            headers=headers,
            json={
                "session_code": test_game_session.session_code
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session"]["current_players"] == 2
        assert len(data["participants"]) == 2

    async def test_join_nonexistent_session(
        self,
        client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test joining non-existent session"""
        response = await client.post(
            "/api/v1/games/sessions/join",
            headers=auth_headers,
            json={
                "session_code": "INVALID1"
            }
        )

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.games
class TestGameSessionList:
    """Test listing game sessions"""

    async def test_list_game_sessions(
        self,
        client: AsyncClient,
        test_game_session
    ):
        """Test getting list of available sessions"""
        response = await client.get("/api/v1/games/sessions?status=waiting")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert data["total_count"] >= 1

    async def test_get_session_details(
        self,
        client: AsyncClient,
        test_game_session,
        test_user,
        auth_headers
    ):
        """Test getting specific session details"""
        response = await client.get(
            f"/api/v1/games/sessions/{test_game_session.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session"]["id"] == str(test_game_session.id)


@pytest.mark.integration
@pytest.mark.games
class TestGameDashboard:
    """Test game dashboard"""

    async def test_get_game_dashboard(
        self,
        client: AsyncClient,
        test_user,
        test_game,
        auth_headers
    ):
        """Test getting user game dashboard"""
        response = await client.get(
            "/api/v1/games/dashboard",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "available_games" in data
        assert "featured_games" in data
        assert "active_sessions" in data
