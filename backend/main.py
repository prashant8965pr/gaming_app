"""
Gaming Platform API
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from config.settings import settings
from config.database import init_db, close_db
from core.exceptions import GamePlatformException
from middleware.error_handler import (
    game_platform_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from middleware.logging_middleware import LoggingMiddleware

# Import API routers
from api.v1 import auth, users, kyc, bank, wallet, admin, rewards, games, websocket, two_factor, promo_codes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("=" * 50)
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print("=" * 50)

    # Initialize databases
    await init_db()

    yield

    # Shutdown
    print("=" * 50)
    print("🛑 Shutting down application")
    print("=" * 50)

    # Close database connections
    await close_db()


# Create FastAPI app with comprehensive documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # Gaming Platform API

    A comprehensive multi-game skill gaming platform with real-time features.

    ## Features

    * **Authentication** - OTP-based authentication with JWT tokens
    * **Two-Factor Authentication** - TOTP-based 2FA with backup codes for enhanced security
    * **User Management** - Complete user profiles and statistics
    * **KYC Verification** - Document verification system
    * **Multi-Wallet System** - Cash, Bonus, and Winnings wallets
    * **Payment Integration** - Deposits and withdrawals with payment gateway
    * **Game Management** - Multiple game types with session management
    * **Real-time Features** - WebSocket support for live gameplay
    * **Referral Program** - User referrals with rewards
    * **Promo Code System** - Marketing campaigns with flexible discount types
    * **Email Notifications** - Transactional emails for all major events
    * **Achievements & Leaderboard** - Gamification features
    * **Admin Panel** - Complete admin dashboard and management

    ## Authentication

    Most endpoints require authentication using JWT tokens. Include the token in the `Authorization` header:

    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ## Rate Limiting

    API requests are rate-limited to prevent abuse. Default limits:
    - 60 requests per minute
    - 1000 requests per hour

    ## Error Handling

    All errors follow a consistent format:

    ```json
    {
      "success": false,
      "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": {}
      }
    }
    ```

    ## Pagination

    List endpoints support pagination with query parameters:
    - `skip`: Number of items to skip (default: 0)
    - `limit`: Number of items to return (default: 20, max: 100)

    ## WebSocket Endpoints

    Real-time features are available via WebSocket connections:
    - `/api/v1/ws/game/{game_session_id}` - Live game sessions
    - `/api/v1/ws/notifications` - Real-time notifications

    WebSocket connections require token authentication via query parameter: `?token=<jwt-token>`
    """,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/api/v1/openapi.json",
    contact={
        "name": "Gaming Platform Support",
        "email": "support@gamingplatform.com",
        "url": "https://gamingplatform.com/support"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://gamingplatform.com/license"
    },
    terms_of_service="https://gamingplatform.com/terms",
    lifespan=lifespan,
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.gamingplatform.com",
            "description": "Production server"
        }
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# Exception Handlers
app.add_exception_handler(GamePlatformException, game_platform_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns API status and version
    """
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint

    Welcome message and API information
    """
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


# API v1 Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(kyc.router, prefix="/api/v1/kyc", tags=["KYC"])
app.include_router(bank.router, prefix="/api/v1/bank", tags=["Bank Accounts"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["Wallet"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(rewards.router, prefix="/api/v1/rewards", tags=["Rewards"])
app.include_router(games.router, prefix="/api/v1/games", tags=["Games"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])
app.include_router(two_factor.router, prefix="/api/v1/2fa", tags=["Two-Factor Authentication"])
app.include_router(promo_codes.router, prefix="/api/v1", tags=["Promo Codes"])


# Mount static files for uploads (local storage)
if settings.FILE_STORAGE_TYPE == "local":
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
