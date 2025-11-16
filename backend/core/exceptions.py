"""
Custom Exceptions
Application-specific exceptions for better error handling
"""


class GamePlatformException(Exception):
    """Base exception for all custom exceptions"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(GamePlatformException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class InvalidCredentialsError(GamePlatformException):
    """Invalid username/password"""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "INVALID_CREDENTIALS")


class TokenExpiredError(GamePlatformException):
    """JWT token has expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "TOKEN_EXPIRED")


class InvalidTokenError(GamePlatformException):
    """Invalid JWT token"""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, "INVALID_TOKEN")


class UserNotFoundError(GamePlatformException):
    """User not found in database"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, "USER_NOT_FOUND")


class UserAlreadyExistsError(GamePlatformException):
    """User already exists (duplicate username/email/phone)"""
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, "USER_ALREADY_EXISTS")


class OTPExpiredError(GamePlatformException):
    """OTP has expired"""
    def __init__(self, message: str = "OTP has expired"):
        super().__init__(message, "OTP_EXPIRED")


class InvalidOTPError(GamePlatformException):
    """Invalid OTP provided"""
    def __init__(self, message: str = "Invalid OTP"):
        super().__init__(message, "INVALID_OTP")


class InsufficientBalanceError(GamePlatformException):
    """Insufficient wallet balance"""
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message, "INSUFFICIENT_BALANCE")


class KYCNotVerifiedError(GamePlatformException):
    """KYC verification required"""
    def __init__(self, message: str = "KYC verification required"):
        super().__init__(message, "KYC_NOT_VERIFIED")


class UserBannedError(GamePlatformException):
    """User account is banned"""
    def __init__(self, message: str = "Account has been banned"):
        super().__init__(message, "USER_BANNED")


class RateLimitExceededError(GamePlatformException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Too many requests. Please try again later"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


class ValidationError(GamePlatformException):
    """Validation error"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "VALIDATION_ERROR")
