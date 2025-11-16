"""
Database Configuration
PostgreSQL, MongoDB, and Redis connection management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from typing import AsyncGenerator
from config.settings import settings

# PostgreSQL Configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session

    Usage:
        @app.get("/")
        async def read_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# MongoDB Configuration
class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]
        print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("❌ Closed MongoDB connection")


def get_mongodb():
    """Get MongoDB database instance"""
    return MongoDB.db


# Redis Configuration
class RedisClient:
    redis: aioredis.Redis = None

    @classmethod
    async def connect_redis(cls):
        """Connect to Redis"""
        cls.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )
        print(f"✅ Connected to Redis: {settings.REDIS_URL}")

    @classmethod
    async def close_redis(cls):
        """Close Redis connection"""
        if cls.redis:
            await cls.redis.close()
            print("❌ Closed Redis connection")


def get_redis():
    """Get Redis client instance"""
    return RedisClient.redis


# Database initialization
async def init_db():
    """Initialize all database connections"""
    await MongoDB.connect_db()
    await RedisClient.connect_redis()


async def close_db():
    """Close all database connections"""
    await MongoDB.close_db()
    await RedisClient.close_redis()
