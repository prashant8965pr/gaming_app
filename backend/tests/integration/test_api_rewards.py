"""
Integration tests for Rewards API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.rewards
class TestDailyBonus:
    """Test daily bonus endpoints"""

    async def test_check_daily_bonus(self, client: AsyncClient, test_user, test_daily_bonus, auth_headers):
        """Test checking daily bonus status"""
        response = await client.get(
            "/api/v1/rewards/daily-bonus/status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "can_claim" in data["data"]
        assert "current_streak" in data["data"]

    async def test_claim_daily_bonus(self, client: AsyncClient, test_user, test_daily_bonus, auth_headers):
        """Test claiming daily bonus"""
        response = await client.post(
            "/api/v1/rewards/daily-bonus/claim",
            headers=auth_headers
        )

        # Should succeed on first claim
        assert response.status_code in [200, 400]  # 400 if already claimed

    async def test_claim_daily_bonus_twice(self, client: AsyncClient, test_user, test_daily_bonus, auth_headers):
        """Test claiming daily bonus twice in same day"""
        # First claim
        await client.post("/api/v1/rewards/daily-bonus/claim", headers=auth_headers)

        # Second claim should fail
        response = await client.post(
            "/api/v1/rewards/daily-bonus/claim",
            headers=auth_headers
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.rewards
class TestAchievements:
    """Test achievements endpoints"""

    async def test_get_achievements(self, client: AsyncClient, test_achievement, auth_headers):
        """Test getting all achievements"""
        response = await client.get(
            "/api/v1/rewards/achievements",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "achievements" in data["data"]
        assert isinstance(data["data"]["achievements"], list)

    async def test_get_user_achievements(self, client: AsyncClient, test_user, auth_headers):
        """Test getting user's unlocked achievements"""
        response = await client.get(
            "/api/v1/rewards/achievements/my",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "unlocked" in data["data"]
        assert "in_progress" in data["data"]

    async def test_get_achievement_detail(self, client: AsyncClient, test_achievement, auth_headers):
        """Test getting achievement detail"""
        response = await client.get(
            f"/api/v1/rewards/achievements/{test_achievement.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["achievement"]["name"] == "First Victory"


@pytest.mark.integration
@pytest.mark.rewards
class TestLeaderboard:
    """Test leaderboard endpoints"""

    async def test_get_global_leaderboard(self, client: AsyncClient, auth_headers):
        """Test getting global leaderboard"""
        response = await client.get(
            "/api/v1/rewards/leaderboard/global",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "leaderboard" in data["data"]

    async def test_get_game_leaderboard(self, client: AsyncClient, test_game, auth_headers):
        """Test getting game-specific leaderboard"""
        response = await client.get(
            f"/api/v1/rewards/leaderboard/game/{test_game.code}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    async def test_get_weekly_leaderboard(self, client: AsyncClient, auth_headers):
        """Test getting weekly leaderboard"""
        response = await client.get(
            "/api/v1/rewards/leaderboard/weekly",
            headers=auth_headers
        )

        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.rewards
class TestReferrals:
    """Test referral endpoints"""

    async def test_get_referral_code(self, client: AsyncClient, test_user, auth_headers):
        """Test getting user's referral code"""
        response = await client.get(
            "/api/v1/rewards/referral/my-code",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "referral_code" in data["data"]
        assert data["data"]["referral_code"] == test_user.referral_code

    async def test_get_referral_stats(self, client: AsyncClient, auth_headers):
        """Test getting referral statistics"""
        response = await client.get(
            "/api/v1/rewards/referral/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "total_referrals" in data["data"]
        assert "total_earnings" in data["data"]

    async def test_get_referred_users(self, client: AsyncClient, auth_headers):
        """Test getting list of referred users"""
        response = await client.get(
            "/api/v1/rewards/referral/my-referrals",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "referrals" in data["data"]

    async def test_apply_referral_code(self, client: AsyncClient, test_user_2, auth_headers):
        """Test applying referral code"""
        response = await client.post(
            "/api/v1/rewards/referral/apply",
            headers=auth_headers,
            json={"referral_code": "TEST1234"}
        )

        # May succeed or fail depending on if already applied
        assert response.status_code in [200, 400]
