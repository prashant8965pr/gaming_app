"""
Logging configuration for Gaming Platform
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
APP_ENV = os.getenv("APP_ENV", "development")


def setup_logging():
    """Setup logging configuration"""

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Format
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(simple_formatter if APP_ENV == "production" else detailed_formatter)
    root_logger.addHandler(console_handler)

    # File handler - Application logs (rotating by size)
    app_log_file = LOGS_DIR / "application.log"
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    app_file_handler.setLevel(LOG_LEVEL)
    app_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_file_handler)

    # File handler - Error logs (rotating by time)
    error_log_file = LOGS_DIR / "errors.log"
    error_file_handler = TimedRotatingFileHandler(
        error_log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)

    # File handler - Access logs (rotating daily)
    access_log_file = LOGS_DIR / "access.log"
    access_file_handler = TimedRotatingFileHandler(
        access_log_file,
        when='midnight',
        interval=1,
        backupCount=14,
        encoding='utf-8'
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(simple_formatter)

    # Create access logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_file_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    # Suppress noisy loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # In production, suppress debug logs from libraries
    if APP_ENV == "production":
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("asyncpg").setLevel(logging.WARNING)
        logging.getLogger("aioredis").setLevel(logging.WARNING)

    logging.info(f"Logging configured - Level: {LOG_LEVEL}, Environment: {APP_ENV}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_request(method: str, path: str, status_code: int, duration: float, user_id: str = None):
    """Log API request"""
    access_logger = logging.getLogger("access")
    user_info = f"user={user_id}" if user_id else "anonymous"
    access_logger.info(
        f"{method} {path} {status_code} {duration:.3f}s {user_info}"
    )


def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    logger = logging.getLogger("error")
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"{type(error).__name__}: {str(error)}{context_str}", exc_info=True)


# Initialize logging when module is imported
if APP_ENV != "test":
    setup_logging()
