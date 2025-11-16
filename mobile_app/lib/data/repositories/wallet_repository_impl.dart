import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../domain/repositories/wallet_repository.dart';
import '../datasources/local/wallet_local_datasource.dart';
import '../datasources/remote/wallet_remote_datasource.dart';
import '../models/wallet_model.dart';

class WalletRepositoryImpl implements WalletRepository {
  final WalletRemoteDataSource _remoteDataSource;
  final WalletLocalDataSource _localDataSource;

  WalletRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
  );

  @override
  Future<Either<Failure, WalletBalanceModel>> getBalance() async {
    try {
      final result = await _remoteDataSource.getBalance();
      await _localDataSource.cacheBalance(result);
      return Right(result);
    } on NetworkException catch (e) {
      // Try to get cached data
      final cachedBalance = await _localDataSource.getCachedBalance();
      if (cachedBalance != null) {
        return Right(cachedBalance);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, TransactionModel>> addMoney({
    required double amount,
    required String paymentMethod,
    String? promoCode,
  }) async {
    try {
      final result = await _remoteDataSource.addMoney(
        amount: amount,
        paymentMethod: paymentMethod,
        promoCode: promoCode,
      );
      await _localDataSource.addTransaction(result);
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
  Future<Either<Failure, TransactionModel>> withdrawMoney({
    required double amount,
    required String bankAccountId,
  }) async {
    try {
      final result = await _remoteDataSource.withdrawMoney(
        amount: amount,
        bankAccountId: bankAccountId,
      );
      await _localDataSource.addTransaction(result);
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
  Future<Either<Failure, List<TransactionModel>>> getTransactions({
    int? limit,
    int? offset,
    String? type,
    String? status,
  }) async {
    try {
      final result = await _remoteDataSource.getTransactions(
        limit: limit,
        offset: offset,
        type: type,
        status: status,
      );
      await _localDataSource.cacheTransactions(result);
      return Right(result);
    } on NetworkException catch (e) {
      // Try to get cached data
      final cachedTransactions =
          await _localDataSource.getCachedTransactions();
      if (cachedTransactions.isNotEmpty) {
        return Right(cachedTransactions);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, TransactionModel>> getTransactionDetails({
    required String transactionId,
  }) async {
    try {
      final result = await _remoteDataSource.getTransactionDetails(
        transactionId: transactionId,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, BankAccountModel>> addBankAccount({
    required String accountHolderName,
    required String accountNumber,
    required String ifscCode,
    required String bankName,
  }) async {
    try {
      final result = await _remoteDataSource.addBankAccount(
        accountHolderName: accountHolderName,
        accountNumber: accountNumber,
        ifscCode: ifscCode,
        bankName: bankName,
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
  Future<Either<Failure, List<BankAccountModel>>> getBankAccounts() async {
    try {
      final result = await _remoteDataSource.getBankAccounts();
      await _localDataSource.cacheBankAccounts(result);
      return Right(result);
    } on NetworkException catch (e) {
      // Try to get cached data
      final cachedAccounts = await _localDataSource.getCachedBankAccounts();
      if (cachedAccounts.isNotEmpty) {
        return Right(cachedAccounts);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteBankAccount({
    required String accountId,
  }) async {
    try {
      await _remoteDataSource.deleteBankAccount(accountId: accountId);
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> setPrimaryBankAccount({
    required String accountId,
  }) async {
    try {
      await _remoteDataSource.setPrimaryBankAccount(accountId: accountId);
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, PromoCodeModel>> validatePromoCode({
    required String code,
  }) async {
    try {
      final result = await _remoteDataSource.validatePromoCode(code: code);
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
  Future<Either<Failure, void>> applyPromoCode({
    required String code,
  }) async {
    try {
      await _remoteDataSource.applyPromoCode(code: code);
      return const Right(null);
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
}
