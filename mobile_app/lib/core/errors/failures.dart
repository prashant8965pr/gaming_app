import 'package:equatable/equatable.dart';

/// Base failure class
abstract class Failure extends Equatable {
  final String message;
  final String? code;

  const Failure({
    required this.message,
    this.code,
  });

  @override
  List<Object?> get props => [message, code];
}

/// Network failure
class NetworkFailure extends Failure {
  const NetworkFailure({
    super.message = 'No internet connection. Please check your network.',
    super.code,
  });
}

/// Server failure
class ServerFailure extends Failure {
  final int? statusCode;

  const ServerFailure({
    super.message = 'Server error. Please try again later.',
    super.code,
    this.statusCode,
  });

  @override
  List<Object?> get props => [message, code, statusCode];
}

/// Cache failure
class CacheFailure extends Failure {
  const CacheFailure({
    super.message = 'Failed to load cached data.',
    super.code,
  });
}

/// Authentication failure
class AuthFailure extends Failure {
  const AuthFailure({
    super.message = 'Authentication failed.',
    super.code,
  });
}

/// Validation failure
class ValidationFailure extends Failure {
  const ValidationFailure({
    super.message = 'Validation failed.',
    super.code,
  });
}

/// Unauthorized failure
class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure({
    super.message = 'Session expired. Please login again.',
    super.code,
  });
}

/// Forbidden failure
class ForbiddenFailure extends Failure {
  const ForbiddenFailure({
    super.message = 'You do not have permission to access this resource.',
    super.code,
  });
}

/// Not found failure
class NotFoundFailure extends Failure {
  const NotFoundFailure({
    super.message = 'Resource not found.',
    super.code,
  });
}

/// Bad request failure
class BadRequestFailure extends Failure {
  const BadRequestFailure({
    super.message = 'Invalid request.',
    super.code,
  });
}

/// Timeout failure
class TimeoutFailure extends Failure {
  const TimeoutFailure({
    super.message = 'Request timeout. Please try again.',
    super.code,
  });
}

/// Insufficient balance failure
class InsufficientBalanceFailure extends Failure {
  const InsufficientBalanceFailure({
    super.message = 'Insufficient balance.',
    super.code,
  });
}

/// KYC not verified failure
class KYCNotVerifiedFailure extends Failure {
  const KYCNotVerifiedFailure({
    super.message = 'Please complete KYC verification to continue.',
    super.code,
  });
}

/// Unknown failure
class UnknownFailure extends Failure {
  const UnknownFailure({
    super.message = 'Something went wrong. Please try again.',
    super.code,
  });
}
