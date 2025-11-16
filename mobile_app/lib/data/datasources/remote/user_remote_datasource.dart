import 'package:dio/dio.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/exceptions.dart';
import '../../models/user_model.dart';
import '../../models/kyc_model.dart';
import '../../models/notification_model.dart';

/// Remote data source for user operations
abstract class UserRemoteDataSource {
  Future<UserModel> getProfile();

  Future<UserModel> updateProfile({
    String? displayName,
    String? email,
    String? avatarUrl,
  });

  Future<UserStatisticsModel> getStatistics();

  Future<KYCDocumentModel> submitKYCDocument({
    required String documentType,
    required String documentNumber,
    required String frontImage,
    String? backImage,
  });

  Future<KYCStatusModel> getKYCStatus();
  Future<List<KYCDocumentModel>> getKYCDocuments();

  Future<NotificationSettingsModel> updateNotificationSettings({
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    bool? gameInvites,
    bool? promotions,
    bool? gameResults,
    bool? walletUpdates,
    bool? tournamentUpdates,
  });

  Future<NotificationSettingsModel> getNotificationSettings();

  Future<void> registerFCMToken({
    required String deviceId,
    required String fcmToken,
    required String deviceType,
    String? deviceName,
  });

  Future<void> deleteAccount();
}

class UserRemoteDataSourceImpl implements UserRemoteDataSource {
  final Dio _dio;

  UserRemoteDataSourceImpl(this._dio);

  @override
  Future<UserModel> getProfile() async {
    try {
      final response = await _dio.get(ApiEndpoints.userProfile);
      return UserModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<UserModel> updateProfile({
    String? displayName,
    String? email,
    String? avatarUrl,
  }) async {
    try {
      final response = await _dio.put(
        ApiEndpoints.userProfile,
        data: {
          if (displayName != null) 'display_name': displayName,
          if (email != null) 'email': email,
          if (avatarUrl != null) 'avatar_url': avatarUrl,
        },
      );
      return UserModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<UserStatisticsModel> getStatistics() async {
    try {
      final response = await _dio.get(ApiEndpoints.userStatistics);
      return UserStatisticsModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<KYCDocumentModel> submitKYCDocument({
    required String documentType,
    required String documentNumber,
    required String frontImage,
    String? backImage,
  }) async {
    try {
      final formData = FormData.fromMap({
        'document_type': documentType,
        'document_number': documentNumber,
        'front_image': await MultipartFile.fromFile(frontImage),
        if (backImage != null)
          'back_image': await MultipartFile.fromFile(backImage),
      });

      final response = await _dio.post(
        ApiEndpoints.kycSubmit,
        data: formData,
      );

      return KYCDocumentModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<KYCStatusModel> getKYCStatus() async {
    try {
      final response = await _dio.get(ApiEndpoints.kycStatus);
      return KYCStatusModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<KYCDocumentModel>> getKYCDocuments() async {
    try {
      final response = await _dio.get(ApiEndpoints.kycDocuments);
      final List<dynamic> data = response.data['data'];
      return data.map((json) => KYCDocumentModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<NotificationSettingsModel> updateNotificationSettings({
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
      final response = await _dio.put(
        ApiEndpoints.notificationSettings,
        data: {
          if (pushEnabled != null) 'push_enabled': pushEnabled,
          if (emailEnabled != null) 'email_enabled': emailEnabled,
          if (smsEnabled != null) 'sms_enabled': smsEnabled,
          if (gameInvites != null) 'game_invites': gameInvites,
          if (promotions != null) 'promotions': promotions,
          if (gameResults != null) 'game_results': gameResults,
          if (walletUpdates != null) 'wallet_updates': walletUpdates,
          if (tournamentUpdates != null)
            'tournament_updates': tournamentUpdates,
        },
      );

      return NotificationSettingsModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<NotificationSettingsModel> getNotificationSettings() async {
    try {
      final response = await _dio.get(ApiEndpoints.notificationSettings);
      return NotificationSettingsModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> registerFCMToken({
    required String deviceId,
    required String fcmToken,
    required String deviceType,
    String? deviceName,
  }) async {
    try {
      await _dio.post(
        ApiEndpoints.fcmToken,
        data: {
          'device_id': deviceId,
          'fcm_token': fcmToken,
          'device_type': deviceType,
          if (deviceName != null) 'device_name': deviceName,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> deleteAccount() async {
    try {
      await _dio.delete(ApiEndpoints.deleteAccount);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  AppException _handleError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return NetworkException(message: 'Connection timeout');
    }

    if (error.type == DioExceptionType.connectionError) {
      return NetworkException(message: 'No internet connection');
    }

    final statusCode = error.response?.statusCode;
    final message = error.response?.data['message'] ?? 'An error occurred';

    switch (statusCode) {
      case 400:
        return ValidationException(message: message);
      case 401:
        return UnauthorizedException(message: message);
      case 404:
        return NotFoundException(message: message);
      case 500:
        return ServerException(message: message);
      default:
        return ServerException(message: message);
    }
  }
}
