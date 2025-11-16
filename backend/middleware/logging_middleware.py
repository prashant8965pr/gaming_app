"""
Logging Middleware
Log all HTTP requests and responses
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests"""

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Log request
        logger.info(f"➡️  {method} {path} from {client_ip}")

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time
            duration_ms = int(duration * 1000)

            # Log response
            status_code = response.status_code
            status_emoji = "✅" if status_code < 400 else "❌"

            logger.info(
                f"{status_emoji} {method} {path} - "
                f"Status: {status_code} - "
                f"Duration: {duration_ms}ms"
            )

            return response

        except Exception as exc:
            # Log error
            duration = time.time() - start_time
            duration_ms = int(duration * 1000)

            logger.error(
                f"💥 {method} {path} - "
                f"Error: {str(exc)} - "
                f"Duration: {duration_ms}ms"
            )
            raise
