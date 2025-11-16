import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../data/models/wallet_model.dart';

/// Wallet repository interface
abstract class WalletRepository {
  /// Get wallet balance
  Future<Either<Failure, WalletBalanceModel>> getBalance();

  /// Add money to wallet
  Future<Either<Failure, TransactionModel>> addMoney({
    required double amount,
    required String paymentMethod,
    String? promoCode,
  });

  /// Withdraw money from wallet
  Future<Either<Failure, TransactionModel>> withdrawMoney({
    required double amount,
    required String bankAccountId,
  });

  /// Get transaction history
  Future<Either<Failure, List<TransactionModel>>> getTransactions({
    int? limit,
    int? offset,
    String? type,
    String? status,
  });

  /// Get transaction details
  Future<Either<Failure, TransactionModel>> getTransactionDetails({
    required String transactionId,
  });

  /// Add bank account
  Future<Either<Failure, BankAccountModel>> addBankAccount({
    required String accountHolderName,
    required String accountNumber,
    required String ifscCode,
    required String bankName,
  });

  /// Get bank accounts
  Future<Either<Failure, List<BankAccountModel>>> getBankAccounts();

  /// Delete bank account
  Future<Either<Failure, void>> deleteBankAccount({
    required String accountId,
  });

  /// Set primary bank account
  Future<Either<Failure, void>> setPrimaryBankAccount({
    required String accountId,
  });

  /// Validate promo code
  Future<Either<Failure, PromoCodeModel>> validatePromoCode({
    required String code,
  });

  /// Apply promo code
  Future<Either<Failure, void>> applyPromoCode({
    required String code,
  });
}
