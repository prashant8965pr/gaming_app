import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';
import '../errors/exceptions.dart';

/// Dio HTTP client configuration
class DioClient {
  late final Dio _dio;
  final FlutterSecureStorage _storage;

  DioClient(this._storage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        sendTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    _dio.interceptors.add(_AuthInterceptor(_storage));
    _dio.interceptors.add(_ErrorInterceptor());
    _dio.interceptors.add(_LoggingInterceptor());
  }

  /// GET request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  /// POST request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  /// PUT request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  /// PATCH request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      final response = await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  /// DELETE request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }

  /// Upload file
  Future<Response> uploadFile(
    String path,
    String filePath, {
    String? fileName,
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: fileName,
        ),
        if (data != null) ...data,
      });

      final response = await _dio.post(
        path,
        data: formData,
        onSendProgress: onSendProgress,
      );
      return response;
    } catch (e) {
      rethrow;
    }
  }
}

/// Authentication interceptor - adds token to requests
class _AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;

  _AuthInterceptor(this._storage);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Get access token from secure storage
    final accessToken = await _storage.read(key: AppConstants.accessTokenKey);

    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }

    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Handle 401 Unauthorized - refresh token
    if (err.response?.statusCode == 401) {
      try {
        // Try to refresh token
        final refreshToken = await _storage.read(key: AppConstants.refreshTokenKey);

        if (refreshToken != null) {
          // TODO: Implement token refresh logic
          // For now, just pass the error
          handler.next(err);
        } else {
          handler.next(err);
        }
      } catch (e) {
        handler.next(err);
      }
    } else {
      handler.next(err);
    }
  }
}

/// Error interceptor - handles HTTP errors
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        throw TimeoutException(
          message: 'Request timeout. Please check your connection and try again.',
        );

      case DioExceptionType.badResponse:
        _handleStatusCode(err.response);
        break;

      case DioExceptionType.cancel:
        throw AppException(message: 'Request cancelled');

      case DioExceptionType.connectionError:
        throw NetworkException(
          message: 'No internet connection. Please check your network.',
        );

      case DioExceptionType.badCertificate:
        throw NetworkException(message: 'SSL certificate error');

      case DioExceptionType.unknown:
        throw AppException(
          message: err.message ?? 'An unknown error occurred',
        );
    }

    handler.next(err);
  }

  void _handleStatusCode(Response? response) {
    final statusCode = response?.statusCode ?? 0;
    final message = _getErrorMessage(response);

    switch (statusCode) {
      case 400:
        throw BadRequestException(
          message: message,
          statusCode: statusCode,
        );
      case 401:
        throw UnauthorizedException(
          message: message.isEmpty ? 'Session expired. Please login again.' : message,
        );
      case 403:
        throw ForbiddenException(
          message: message.isEmpty ? 'You do not have permission to access this resource.' : message,
        );
      case 404:
        throw NotFoundException(
          message: message.isEmpty ? 'Resource not found.' : message,
        );
      case 422:
        throw ValidationException(
          message: message.isEmpty ? 'Validation failed.' : message,
          data: response?.data,
        );
      case 500:
      case 502:
      case 503:
      case 504:
        throw ServerException(
          message: 'Server error. Please try again later.',
          statusCode: statusCode,
        );
      default:
        throw ServerException(
          message: message.isEmpty ? 'An error occurred' : message,
          statusCode: statusCode,
        );
    }
  }

  String _getErrorMessage(Response? response) {
    try {
      if (response?.data is Map) {
        final data = response!.data as Map<String, dynamic>;

        // Try different error message keys
        if (data.containsKey('message')) {
          return data['message'] as String;
        } else if (data.containsKey('error')) {
          final error = data['error'];
          if (error is String) {
            return error;
          } else if (error is Map && error.containsKey('message')) {
            return error['message'] as String;
          }
        } else if (data.containsKey('detail')) {
          return data['detail'] as String;
        }
      }
      return '';
    } catch (e) {
      return '';
    }
  }
}

/// Logging interceptor - logs requests and responses
class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    print('┌─────────────────────────────────────────────────');
    print('│ REQUEST: ${options.method} ${options.path}');
    print('│ Headers: ${options.headers}');
    print('│ Query Parameters: ${options.queryParameters}');
    if (options.data != null) {
      print('│ Body: ${options.data}');
    }
    print('└─────────────────────────────────────────────────');
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    print('┌─────────────────────────────────────────────────');
    print('│ RESPONSE: ${response.statusCode} ${response.requestOptions.path}');
    print('│ Data: ${response.data}');
    print('└─────────────────────────────────────────────────');
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    print('┌─────────────────────────────────────────────────');
    print('│ ERROR: ${err.requestOptions.method} ${err.requestOptions.path}');
    print('│ Message: ${err.message}');
    print('│ Response: ${err.response?.data}');
    print('└─────────────────────────────────────────────────');
    handler.next(err);
  }
}
