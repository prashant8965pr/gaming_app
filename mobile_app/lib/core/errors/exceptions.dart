/// Custom exceptions for error handling
class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic data;

  AppException({
    required this.message,
    this.code,
    this.data,
  });

  @override
  String toString() => message;
}

/// Network-related exceptions
class NetworkException extends AppException {
  NetworkException({
    required super.message,
    super.code,
    super.data,
  });
}

/// Server-related exceptions
class ServerException extends AppException {
  final int? statusCode;

  ServerException({
    required super.message,
    super.code,
    super.data,
    this.statusCode,
  });
}

/// Authentication exceptions
class AuthException extends AppException {
  AuthException({
    required super.message,
    super.code,
    super.data,
  });
}

/// Validation exceptions
class ValidationException extends AppException {
  ValidationException({
    required super.message,
    super.code,
    super.data,
  });
}

/// Cache exceptions
class CacheException extends AppException {
  CacheException({
    required super.message,
    super.code,
    super.data,
  });
}

/// Timeout exception
class TimeoutException extends AppException {
  TimeoutException({
    super.message = 'Request timeout. Please try again.',
    super.code,
    super.data,
  });
}

/// Unauthorized exception
class UnauthorizedException extends AuthException {
  UnauthorizedException({
    super.message = 'Session expired. Please login again.',
    super.code,
    super.data,
  });
}

/// Forbidden exception
class ForbiddenException extends AppException {
  ForbiddenException({
    super.message = 'You do not have permission to access this resource.',
    super.code,
    super.data,
  });
}

/// Not found exception
class NotFoundException extends AppException {
  NotFoundException({
    super.message = 'Resource not found.',
    super.code,
    super.data,
  });
}

/// Bad request exception
class BadRequestException extends AppException {
  BadRequestException({
    super.message = 'Invalid request.',
    super.code,
    super.data,
  });
}

/// Insufficient balance exception
class InsufficientBalanceException extends AppException {
  InsufficientBalanceException({
    super.message = 'Insufficient balance.',
    super.code,
    super.data,
  });
}

/// KYC not verified exception
class KYCNotVerifiedException extends AppException {
  KYCNotVerifiedException({
    super.message = 'Please complete KYC verification to continue.',
    super.code,
    super.data,
  });
}
