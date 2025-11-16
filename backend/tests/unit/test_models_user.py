"""
Unit tests for User models
"""
import pytest
from datetime import datetime
import uuid

from models.user import User, UserProfile, UserStatistics


@pytest.mark.unit
@pytest.mark.auth
class TestUserModel:
    """Test User model"""

    async def test_create_user(self, db_session):
        """Test creating a new user"""
        user = User(
            id=uuid.uuid4(),
            username="newuser",
            email="newuser@example.com",
            phone="+919999999999",
            password_hash="hashed_password",
            is_active=True
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active == True
        assert user.created_at is not None

    async def test_user_referral_code_unique(self, db_session, test_user):
        """Test referral code uniqueness"""
        # Try to create user with same referral code
        duplicate_user = User(
            id=uuid.uuid4(),
            username="duplicate",
            email="dup@example.com",
            phone="+919999999998",
            password_hash="hashed",
            referral_code=test_user.referral_code
        )

        db_session.add(duplicate_user)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_session.commit()

    async def test_user_statistics_relationship(self, db_session, test_user):
        """Test user statistics creation"""
        stats = UserStatistics(
            user_id=test_user.id,
            total_games_played=10,
            total_games_won=5,
            total_winnings=50000,  # Rs.500
            win_rate=50.0
        )

        db_session.add(stats)
        await db_session.commit()
        await db_session.refresh(stats)

        assert stats.user_id == test_user.id
        assert stats.total_games_played == 10
        assert stats.win_rate == 50.0


@pytest.mark.unit
@pytest.mark.auth
class TestUserProfile:
    """Test UserProfile model"""

    async def test_create_user_profile(self, db_session, test_user):
        """Test creating user profile"""
        profile = UserProfile(
            user_id=test_user.id,
            full_name="Test Full Name",
            date_of_birth=datetime(1990, 1, 1).date(),
            gender="male",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            country="India",
            pincode="123456"
        )

        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(profile)

        assert profile.user_id == test_user.id
        assert profile.full_name == "Test Full Name"
        assert profile.city == "Test City"


@pytest.mark.unit
@pytest.mark.auth
class TestUserStatistics:
    """Test UserStatistics model"""

    async def test_update_statistics(self, db_session, test_user):
        """Test updating user statistics"""
        stats = UserStatistics(
            user_id=test_user.id,
            total_games_played=0,
            total_games_won=0
        )

        db_session.add(stats)
        await db_session.commit()

        # Update stats
        stats.total_games_played = 5
        stats.total_games_won = 3
        stats.win_rate = (3 / 5) * 100

        await db_session.commit()
        await db_session.refresh(stats)

        assert stats.total_games_played == 5
        assert stats.total_games_won == 3
        assert stats.win_rate == 60.0
