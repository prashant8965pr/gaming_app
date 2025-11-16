import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../data/models/auth_models.dart';
import '../../data/models/user_model.dart';

/// Authentication repository interface
abstract class AuthRepository {
  /// Send OTP to phone number
  Future<Either<Failure, SendOTPResponseModel>> sendOTP({
    required String phoneNumber,
  });

  /// Verify OTP
  Future<Either<Failure, AuthResponseModel>> verifyOTP({
    required String phoneNumber,
    required String otp,
  });

  /// Social login (Google, Facebook, Apple)
  Future<Either<Failure, AuthResponseModel>> socialLogin({
    required String provider,
    required String accessToken,
    String? deviceId,
    String? deviceName,
  });

  /// Complete profile setup for new users
  Future<Either<Failure, AuthResponseModel>> completeProfile({
    required String username,
    required String displayName,
    required DateTime dateOfBirth,
    required String gender,
    String? referralCode,
  });

  /// Refresh access token
  Future<Either<Failure, AuthResponseModel>> refreshToken({
    required String refreshToken,
  });

  /// Logout
  Future<Either<Failure, void>> logout();

  /// Check if user is logged in
  Future<bool> isLoggedIn();

  /// Get current user from cache
  Future<UserModel?> getCurrentUser();
}
