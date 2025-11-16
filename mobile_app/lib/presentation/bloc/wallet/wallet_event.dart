import 'package:equatable/equatable.dart';

/// Base class for all wallet events
abstract class WalletEvent extends Equatable {
  const WalletEvent();

  @override
  List<Object?> get props => [];
}

/// Event to load wallet balance
class LoadWalletBalanceEvent extends WalletEvent {
  final bool forceRefresh;

  const LoadWalletBalanceEvent({this.forceRefresh = false});

  @override
  List<Object?> get props => [forceRefresh];
}

/// Event to add money to wallet
class AddMoneyEvent extends WalletEvent {
  final double amount;
  final String paymentMethod;
  final String? promoCode;

  const AddMoneyEvent({
    required this.amount,
    required this.paymentMethod,
    this.promoCode,
  });

  @override
  List<Object?> get props => [amount, paymentMethod, promoCode];
}

/// Event to withdraw money from wallet
class WithdrawMoneyEvent extends WalletEvent {
  final double amount;
  final String bankAccountId;

  const WithdrawMoneyEvent({
    required this.amount,
    required this.bankAccountId,
  });

  @override
  List<Object?> get props => [amount, bankAccountId];
}

/// Event to load transaction history
class LoadTransactionsEvent extends WalletEvent {
  final int? limit;
  final int? offset;
  final String? type;
  final String? status;

  const LoadTransactionsEvent({
    this.limit,
    this.offset,
    this.type,
    this.status,
  });

  @override
  List<Object?> get props => [limit, offset, type, status];
}

/// Event to load transaction details
class LoadTransactionDetailsEvent extends WalletEvent {
  final String transactionId;

  const LoadTransactionDetailsEvent({required this.transactionId});

  @override
  List<Object?> get props => [transactionId];
}

/// Event to add bank account
class AddBankAccountEvent extends WalletEvent {
  final String accountHolderName;
  final String accountNumber;
  final String ifscCode;
  final String bankName;

  const AddBankAccountEvent({
    required this.accountHolderName,
    required this.accountNumber,
    required this.ifscCode,
    required this.bankName,
  });

  @override
  List<Object?> get props => [
        accountHolderName,
        accountNumber,
        ifscCode,
        bankName,
      ];
}

/// Event to load bank accounts
class LoadBankAccountsEvent extends WalletEvent {
  const LoadBankAccountsEvent();
}

/// Event to delete bank account
class DeleteBankAccountEvent extends WalletEvent {
  final String accountId;

  const DeleteBankAccountEvent({required this.accountId});

  @override
  List<Object?> get props => [accountId];
}

/// Event to set primary bank account
class SetPrimaryBankAccountEvent extends WalletEvent {
  final String accountId;

  const SetPrimaryBankAccountEvent({required this.accountId});

  @override
  List<Object?> get props => [accountId];
}

/// Event to validate promo code
class ValidatePromoCodeEvent extends WalletEvent {
  final String code;

  const ValidatePromoCodeEvent({required this.code});

  @override
  List<Object?> get props => [code];
}

/// Event to apply promo code
class ApplyPromoCodeEvent extends WalletEvent {
  final String code;

  const ApplyPromoCodeEvent({required this.code});

  @override
  List<Object?> get props => [code];
}
