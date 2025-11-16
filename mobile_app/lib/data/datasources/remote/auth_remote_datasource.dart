import 'package:dio/dio.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/exceptions.dart';
import '../../models/auth_models.dart';
import '../../models/user_model.dart';

/// Remote data source for authentication
abstract class AuthRemoteDataSource {
  Future<SendOTPResponseModel> sendOTP({required String phoneNumber});

  Future<AuthResponseModel> verifyOTP({
    required String phoneNumber,
    required String otp,
  });

  Future<AuthResponseModel> socialLogin({
    required String provider,
    required String accessToken,
    String? deviceId,
    String? deviceName,
  });

  Future<AuthResponseModel> completeProfile({
    required String username,
    required String displayName,
    required DateTime dateOfBirth,
    required String gender,
    String? referralCode,
  });

  Future<AuthResponseModel> refreshToken({required String refreshToken});

  Future<void> logout();
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final Dio _dio;

  AuthRemoteDataSourceImpl(this._dio);

  @override
  Future<SendOTPResponseModel> sendOTP({required String phoneNumber}) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.sendOtp,
        data: {'phone_number': phoneNumber},
      );

      return SendOTPResponseModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<AuthResponseModel> verifyOTP({
    required String phoneNumber,
    required String otp,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.verifyOtp,
        data: {
          'phone_number': phoneNumber,
          'otp': otp,
        },
      );

      return AuthResponseModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<AuthResponseModel> socialLogin({
    required String provider,
    required String accessToken,
    String? deviceId,
    String? deviceName,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.socialLogin,
        data: {
          'provider': provider,
          'access_token': accessToken,
          'device_id': deviceId,
          'device_name': deviceName,
        },
      );

      return AuthResponseModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<AuthResponseModel> completeProfile({
    required String username,
    required String displayName,
    required DateTime dateOfBirth,
    required String gender,
    String? referralCode,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.completeProfile,
        data: {
          'username': username,
          'display_name': displayName,
          'date_of_birth': dateOfBirth.toIso8601String(),
          'gender': gender,
          if (referralCode != null) 'referral_code': referralCode,
        },
      );

      return AuthResponseModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<AuthResponseModel> refreshToken({required String refreshToken}) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.refreshToken,
        data: {'refresh_token': refreshToken},
      );

      return AuthResponseModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> logout() async {
    try {
      await _dio.post(ApiEndpoints.logout);
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
