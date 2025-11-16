import 'package:dio/dio.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/exceptions.dart';
import '../../models/wallet_model.dart';

/// Remote data source for wallet operations
abstract class WalletRemoteDataSource {
  Future<WalletBalanceModel> getBalance();

  Future<TransactionModel> addMoney({
    required double amount,
    required String paymentMethod,
    String? promoCode,
  });

  Future<TransactionModel> withdrawMoney({
    required double amount,
    required String bankAccountId,
  });

  Future<List<TransactionModel>> getTransactions({
    int? limit,
    int? offset,
    String? type,
    String? status,
  });

  Future<TransactionModel> getTransactionDetails({
    required String transactionId,
  });

  Future<BankAccountModel> addBankAccount({
    required String accountHolderName,
    required String accountNumber,
    required String ifscCode,
    required String bankName,
  });

  Future<List<BankAccountModel>> getBankAccounts();

  Future<void> deleteBankAccount({required String accountId});

  Future<void> setPrimaryBankAccount({required String accountId});

  Future<PromoCodeModel> validatePromoCode({required String code});

  Future<void> applyPromoCode({required String code});
}

class WalletRemoteDataSourceImpl implements WalletRemoteDataSource {
  final Dio _dio;

  WalletRemoteDataSourceImpl(this._dio);

  @override
  Future<WalletBalanceModel> getBalance() async {
    try {
      final response = await _dio.get(ApiEndpoints.walletBalance);
      return WalletBalanceModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<TransactionModel> addMoney({
    required double amount,
    required String paymentMethod,
    String? promoCode,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.walletDeposit,
        data: {
          'amount': amount,
          'payment_method': paymentMethod,
          if (promoCode != null) 'promo_code': promoCode,
        },
      );
      return TransactionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<TransactionModel> withdrawMoney({
    required double amount,
    required String bankAccountId,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.walletWithdraw,
        data: {
          'amount': amount,
          'bank_account_id': bankAccountId,
        },
      );
      return TransactionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<TransactionModel>> getTransactions({
    int? limit,
    int? offset,
    String? type,
    String? status,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.walletTransactions,
        queryParameters: {
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
          if (type != null) 'type': type,
          if (status != null) 'status': status,
        },
      );
      final List<dynamic> data = response.data['data'];
      return data.map((json) => TransactionModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<TransactionModel> getTransactionDetails({
    required String transactionId,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.transactionDetails(transactionId),
      );
      return TransactionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<BankAccountModel> addBankAccount({
    required String accountHolderName,
    required String accountNumber,
    required String ifscCode,
    required String bankName,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.bankAccounts,
        data: {
          'account_holder_name': accountHolderName,
          'account_number': accountNumber,
          'ifsc_code': ifscCode,
          'bank_name': bankName,
        },
      );
      return BankAccountModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<BankAccountModel>> getBankAccounts() async {
    try {
      final response = await _dio.get(ApiEndpoints.bankAccounts);
      final List<dynamic> data = response.data['data'];
      return data.map((json) => BankAccountModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> deleteBankAccount({required String accountId}) async {
    try {
      await _dio.delete(ApiEndpoints.bankAccountDetails(accountId));
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> setPrimaryBankAccount({required String accountId}) async {
    try {
      await _dio.put(ApiEndpoints.bankAccountPrimary(accountId));
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<PromoCodeModel> validatePromoCode({required String code}) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.promoCodeValidate,
        data: {'code': code},
      );
      return PromoCodeModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> applyPromoCode({required String code}) async {
    try {
      await _dio.post(
        ApiEndpoints.promoCodeApply,
        data: {'code': code},
      );
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
