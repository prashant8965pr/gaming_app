import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../data/models/user_model.dart';
import '../../data/models/kyc_model.dart';
import '../../data/models/notification_model.dart';

/// User repository interface
abstract class UserRepository {
  /// Get user profile
  Future<Either<Failure, UserModel>> getProfile();

  /// Update user profile
  Future<Either<Failure, UserModel>> updateProfile({
    String? displayName,
    String? email,
    String? avatarUrl,
  });

  /// Get user statistics
  Future<Either<Failure, UserStatisticsModel>> getStatistics();

  /// Submit KYC document
  Future<Either<Failure, KYCDocumentModel>> submitKYCDocument({
    required String documentType,
    required String documentNumber,
    required String frontImage,
    String? backImage,
  });

  /// Get KYC status
  Future<Either<Failure, KYCStatusModel>> getKYCStatus();

  /// Get KYC documents
  Future<Either<Failure, List<KYCDocumentModel>>> getKYCDocuments();

  /// Update notification settings
  Future<Either<Failure, NotificationSettingsModel>> updateNotificationSettings({
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    bool? gameInvites,
    bool? promotions,
    bool? gameResults,
    bool? walletUpdates,
    bool? tournamentUpdates,
  });

  /// Get notification settings
  Future<Either<Failure, NotificationSettingsModel>> getNotificationSettings();

  /// Register FCM token
  Future<Either<Failure, void>> registerFCMToken({
    required String deviceId,
    required String fcmToken,
    required String deviceType,
    String? deviceName,
  });

  /// Delete account
  Future<Either<Failure, void>> deleteAccount();
}
