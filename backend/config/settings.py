"""
Application Settings
Centralized configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Gaming Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database - PostgreSQL
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "gaming_platform"

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # SMS - Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Email - SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""

    # Payment - Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Payment - Cashfree
    CASHFREE_APP_ID: str = ""
    CASHFREE_SECRET_KEY: str = ""

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # File Storage
    FILE_STORAGE_TYPE: str = "local"  # local, s3, cloudinary
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE_MB: int = 5

    # Firebase
    FCM_SERVER_KEY: str = ""

    # Sentry
    SENTRY_DSN: str = ""

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # OTP
    OTP_EXPIRY_MINUTES: int = 5
    MAX_OTP_ATTEMPTS: int = 3

    # KYC
    KYC_AUTO_APPROVAL: bool = False  # Auto-approve KYC in development
    KYC_REQUIRED_FOR_WITHDRAWAL: bool = True

    # Wallet & Transactions
    MIN_DEPOSIT_AMOUNT: float = 10.0  # Minimum deposit in rupees
    MAX_DEPOSIT_AMOUNT: float = 100000.0  # Maximum deposit in rupees
    MIN_WITHDRAWAL_AMOUNT: float = 100.0  # Minimum withdrawal in rupees
    MAX_WITHDRAWAL_AMOUNT: float = 100000.0  # Maximum withdrawal in rupees
    WITHDRAWAL_PROCESSING_FEE: float = 0.0  # Processing fee in rupees
    TDS_PERCENTAGE: float = 30.0  # TDS on winnings above threshold
    TDS_THRESHOLD: float = 10000.0  # TDS applicable on winnings above this amount

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
