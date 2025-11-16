import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../domain/repositories/user_repository.dart';
import '../datasources/local/user_local_datasource.dart';
import '../datasources/remote/user_remote_datasource.dart';
import '../models/user_model.dart';
import '../models/kyc_model.dart';
import '../models/notification_model.dart';

class UserRepositoryImpl implements UserRepository {
  final UserRemoteDataSource _remoteDataSource;
  final UserLocalDataSource _localDataSource;

  UserRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
  );

  @override
  Future<Either<Failure, UserModel>> getProfile() async {
    try {
      final result = await _remoteDataSource.getProfile();
      await _localDataSource.cacheUser(result);
      return Right(result);
    } on NetworkException catch (e) {
      // Try to get cached data
      final cachedUser = await _localDataSource.getCachedUser();
      if (cachedUser != null) {
        return Right(cachedUser);
      }
      return Left(NetworkFailure(message: e.message));
    } on UnauthorizedException catch (e) {
      return Left(AuthFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, UserModel>> updateProfile({
    String? displayName,
    String? email,
    String? avatarUrl,
  }) async {
    try {
      final result = await _remoteDataSource.updateProfile(
        displayName: displayName,
        email: email,
        avatarUrl: avatarUrl,
      );
      await _localDataSource.cacheUser(result);
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
  Future<Either<Failure, UserStatisticsModel>> getStatistics() async {
    try {
      final result = await _remoteDataSource.getStatistics();
      await _localDataSource.cacheUserStatistics(result);
      return Right(result);
    } on NetworkException catch (e) {
      // Try to get cached data
      final cachedStats = await _localDataSource.getCachedUserStatistics();
      if (cachedStats != null) {
        return Right(cachedStats);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, KYCDocumentModel>> submitKYCDocument({
    required String documentType,
    required String documentNumber,
    required String frontImage,
    String? backImage,
  }) async {
    try {
      final result = await _remoteDataSource.submitKYCDocument(
        documentType: documentType,
        documentNumber: documentNumber,
        frontImage: frontImage,
        backImage: backImage,
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
  Future<Either<Failure, KYCStatusModel>> getKYCStatus() async {
    try {
      final result = await _remoteDataSource.getKYCStatus();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<KYCDocumentModel>>> getKYCDocuments() async {
    try {
      final result = await _remoteDataSource.getKYCDocuments();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, NotificationSettingsModel>>
      updateNotificationSettings({
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    bool? gameInvites,
    bool? promotions,
    bool? gameResults,
    bool? walletUpdates,
    bool? tournamentUpdates,
  }) async {
    try {
      final result = await _remoteDataSource.updateNotificationSettings(
        pushEnabled: pushEnabled,
        emailEnabled: emailEnabled,
        smsEnabled: smsEnabled,
        gameInvites: gameInvites,
        promotions: promotions,
        gameResults: gameResults,
        walletUpdates: walletUpdates,
        tournamentUpdates: tournamentUpdates,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, NotificationSettingsModel>>
      getNotificationSettings() async {
    try {
      final result = await _remoteDataSource.getNotificationSettings();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> registerFCMToken({
    required String deviceId,
    required String fcmToken,
    required String deviceType,
    String? deviceName,
  }) async {
    try {
      await _remoteDataSource.registerFCMToken(
        deviceId: deviceId,
        fcmToken: fcmToken,
        deviceType: deviceType,
        deviceName: deviceName,
      );
      return const Right(null);
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteAccount() async {
    try {
      await _remoteDataSource.deleteAccount();
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }
}
