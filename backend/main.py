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
from api.v1 import auth, users, kyc, bank, wallet, admin, rewards
# from api.v1 import games  # Will be added in Phase 4


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


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-game skill gaming platform API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
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
# app.include_router(games.router, prefix="/api/v1/games", tags=["Games"])  # Phase 4


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
