"""
Pytest configuration and fixtures
Shared fixtures for all tests
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
import uuid
from datetime import datetime, timedelta

from config.database import Base
from config.settings import settings
from main import app
from middleware.auth import create_access_token


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""

    # Override get_db dependency
    from config.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    from models.user import User
    from services.auth_service import hash_password

    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        phone="+919876543210",
        password_hash=hash_password("TestPass123!"),
        display_name="Test User",
        is_active=True,
        is_verified=True,
        is_email_verified=True,
        is_phone_verified=True,
        referral_code="TEST1234"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_user_2(db_session):
    """Create a second test user"""
    from models.user import User
    from services.auth_service import hash_password

    user = User(
        id=uuid.uuid4(),
        username="testuser2",
        email="test2@example.com",
        phone="+919876543211",
        password_hash=hash_password("TestPass123!"),
        display_name="Test User 2",
        is_active=True,
        is_verified=True,
        is_email_verified=True,
        is_phone_verified=True,
        referral_code="TEST5678"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def admin_user(db_session):
    """Create an admin user"""
    from models.user import User
    from services.auth_service import hash_password

    user = User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@example.com",
        phone="+919876543200",
        password_hash=hash_password("AdminPass123!"),
        display_name="Admin User",
        is_active=True,
        is_verified=True,
        is_email_verified=True,
        is_phone_verified=True,
        referral_code="ADMIN123"
        # Note: Add role/admin flag when implemented
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
def auth_token(test_user):
    """Create auth token for test user"""
    return create_access_token({"sub": str(test_user.id)})


@pytest.fixture
def admin_token(admin_user):
    """Create auth token for admin user"""
    return create_access_token({"sub": str(admin_user.id)})


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Create admin authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# Wallet Fixtures
# ============================================================================

@pytest.fixture
async def test_wallets(db_session, test_user):
    """Create test wallets for user"""
    from models.wallet import Wallet

    wallets = []
    for wallet_type in ["cash", "bonus", "winnings"]:
        wallet = Wallet(
            id=uuid.uuid4(),
            user_id=test_user.id,
            wallet_type=wallet_type,
            balance=100000 if wallet_type == "cash" else 0  # Rs.1000 in cash
        )
        db_session.add(wallet)
        wallets.append(wallet)

    await db_session.commit()

    for wallet in wallets:
        await db_session.refresh(wallet)

    return wallets


# ============================================================================
# Game Fixtures
# ============================================================================

@pytest.fixture
async def test_game(db_session):
    """Create a test game"""
    from models.game import Game

    game = Game(
        id=uuid.uuid4(),
        code="ludo_test",
        name="Test Ludo",
        description="Test game for automated testing",
        category="board",
        min_players=2,
        max_players=4,
        avg_duration_minutes=10,
        difficulty_level="medium",
        min_entry_fee=1000,  # Rs.10
        max_entry_fee=1000000,  # Rs.10000
        default_entry_fee=10000,  # Rs.100
        prize_distribution={"1st": 70, "2nd": 20, "3rd": 10},
        rules={},
        game_config={},
        is_active=True,
        is_featured=True,
        is_skill_based=True
    )

    db_session.add(game)
    await db_session.commit()
    await db_session.refresh(game)

    return game


@pytest.fixture
async def test_game_session(db_session, test_game, test_user, test_wallets):
    """Create a test game session"""
    from models.game import GameSession

    session = GameSession(
        id=uuid.uuid4(),
        game_id=test_game.id,
        session_code="TEST1234",
        session_type="public",
        entry_fee=10000,  # Rs.100
        total_prize_pool=10000,
        max_players=4,
        current_players=1,
        min_players_to_start=2,
        status="waiting",
        is_private=False,
        auto_start=True,
        platform_fee_percentage=5.0
    )

    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return session


# ============================================================================
# KYC Fixtures
# ============================================================================

@pytest.fixture
async def test_kyc_document(db_session, test_user):
    """Create a test KYC document"""
    from models.kyc import KYCDocument

    kyc = KYCDocument(
        id=uuid.uuid4(),
        user_id=test_user.id,
        document_type="aadhaar",
        document_number="123456789012",
        full_name="Test User",
        date_of_birth=datetime(1990, 1, 1).date(),
        address_line1="123 Test St",
        city="Test City",
        state="Test State",
        pincode="123456",
        front_image_url="/uploads/kyc/front.jpg",
        back_image_url="/uploads/kyc/back.jpg",
        verification_status="pending"
    )

    db_session.add(kyc)
    await db_session.commit()
    await db_session.refresh(kyc)

    return kyc


# ============================================================================
# Reward Fixtures
# ============================================================================

@pytest.fixture
async def test_daily_bonus(db_session, test_user):
    """Create a test daily bonus record"""
    from models.referral import DailyBonus

    daily_bonus = DailyBonus(
        id=uuid.uuid4(),
        user_id=test_user.id,
        current_streak=0,
        longest_streak=0,
        total_claims=0,
        next_bonus_day=1,
        can_claim_today=True,
        streak_broken=False
    )

    db_session.add(daily_bonus)
    await db_session.commit()
    await db_session.refresh(daily_bonus)

    return daily_bonus


@pytest.fixture
async def test_achievement(db_session):
    """Create a test achievement"""
    from models.referral import Achievement

    achievement = Achievement(
        id=uuid.uuid4(),
        code="FIRST_WIN",
        name="First Victory",
        description="Win your first game",
        category="gaming",
        criteria={"type": "total_wins", "count": 1},
        reward_type="coins",
        reward_coins=100,
        difficulty="easy",
        points=10,
        is_active=True,
        is_hidden=False
    )

    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)

    return achievement


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def sample_game_state():
    """Sample game state for testing"""
    return {
        "game_type": "ludo",
        "num_players": 4,
        "current_turn": 1,
        "current_player_position": 1,
        "board": {
            "pieces": {
                "red": [
                    {"id": "red_1", "position": -1, "in_home": True},
                    {"id": "red_2", "position": -1, "in_home": True},
                    {"id": "red_3", "position": -1, "in_home": True},
                    {"id": "red_4", "position": -1, "in_home": True}
                ]
            }
        }
    }


@pytest.fixture
def sample_move_data():
    """Sample move data for testing"""
    return {
        "type": "roll_dice",
        "dice_value": 6
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_payment_gateway(monkeypatch):
    """Mock payment gateway responses"""
    class MockPaymentGateway:
        @staticmethod
        async def create_order(*args, **kwargs):
            return {
                "order_id": "TEST_ORDER_123",
                "status": "created",
                "amount": 10000
            }

        @staticmethod
        async def verify_payment(*args, **kwargs):
            return {"status": "success"}

    return MockPaymentGateway()


@pytest.fixture
def mock_sms_service(monkeypatch):
    """Mock SMS service"""
    class MockSMSService:
        @staticmethod
        async def send_otp(phone, otp):
            return {"status": "sent", "message_id": "TEST_MSG_123"}

    return MockSMSService()


@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service"""
    class MockEmailService:
        @staticmethod
        async def send_email(to, subject, body):
            return {"status": "sent", "message_id": "TEST_EMAIL_123"}

    return MockEmailService()
