import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../core/storage/secure_storage.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/local/user_local_datasource.dart';
import '../datasources/remote/auth_remote_datasource.dart';
import '../models/auth_models.dart';
import '../models/user_model.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final UserLocalDataSource _localDataSource;
  final SecureStorage _secureStorage;

  AuthRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
    this._secureStorage,
  );

  @override
  Future<Either<Failure, SendOTPResponseModel>> sendOTP({
    required String phoneNumber,
  }) async {
    try {
      final result = await _remoteDataSource.sendOTP(
        phoneNumber: phoneNumber,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, AuthResponseModel>> verifyOTP({
    required String phoneNumber,
    required String otp,
  }) async {
    try {
      final result = await _remoteDataSource.verifyOTP(
        phoneNumber: phoneNumber,
        otp: otp,
      );

      // Save tokens and user data
      if (result.data != null) {
        await _secureStorage.saveAccessToken(result.data!.accessToken);
        await _secureStorage.saveRefreshToken(result.data!.refreshToken);
        await _secureStorage.saveUserId(result.data!.user.id);
        await _localDataSource.cacheUser(result.data!.user);
      }

      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on UnauthorizedException catch (e) {
      return Left(AuthFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, AuthResponseModel>> socialLogin({
    required String provider,
    required String accessToken,
    String? deviceId,
    String? deviceName,
  }) async {
    try {
      final result = await _remoteDataSource.socialLogin(
        provider: provider,
        accessToken: accessToken,
        deviceId: deviceId,
        deviceName: deviceName,
      );

      // Save tokens and user data
      if (result.data != null) {
        await _secureStorage.saveAccessToken(result.data!.accessToken);
        await _secureStorage.saveRefreshToken(result.data!.refreshToken);
        await _secureStorage.saveUserId(result.data!.user.id);
        await _localDataSource.cacheUser(result.data!.user);
      }

      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, AuthResponseModel>> completeProfile({
    required String username,
    required String displayName,
    required DateTime dateOfBirth,
    required String gender,
    String? referralCode,
  }) async {
    try {
      final result = await _remoteDataSource.completeProfile(
        username: username,
        displayName: displayName,
        dateOfBirth: dateOfBirth,
        gender: gender,
        referralCode: referralCode,
      );

      // Update cached user data
      if (result.data != null) {
        await _localDataSource.cacheUser(result.data!.user);
      }

      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, AuthResponseModel>> refreshToken({
    required String refreshToken,
  }) async {
    try {
      final result = await _remoteDataSource.refreshToken(
        refreshToken: refreshToken,
      );

      // Update tokens
      if (result.data != null) {
        await _secureStorage.saveAccessToken(result.data!.accessToken);
        await _secureStorage.saveRefreshToken(result.data!.refreshToken);
      }

      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on UnauthorizedException catch (e) {
      // Clear all auth data if refresh token is invalid
      await logout();
      return Left(AuthFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> logout() async {
    try {
      await _remoteDataSource.logout();

      // Clear all local data
      await _secureStorage.clearAll();
      await _localDataSource.clearUser();

      return const Right(null);
    } on AppException catch (e) {
      // Still clear local data even if server call fails
      await _secureStorage.clearAll();
      await _localDataSource.clearUser();
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      // Still clear local data
      await _secureStorage.clearAll();
      await _localDataSource.clearUser();
      return const Right(null);
    }
  }

  @override
  Future<bool> isLoggedIn() async {
    return await _secureStorage.isLoggedIn();
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    return await _localDataSource.getCachedUser();
  }
}
