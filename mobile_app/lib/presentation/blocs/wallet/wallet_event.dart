import 'package:equatable/equatable.dart';

abstract class WalletEvent extends Equatable {
  const WalletEvent();

  @override
  List<Object?> get props => [];
}

class LoadWallets extends WalletEvent {
  const LoadWallets();
}

class DepositMoney extends WalletEvent {
  final double amount;
  final String paymentMethod;
  final String? promoCode;

  const DepositMoney({
    required this.amount,
    required this.paymentMethod,
    this.promoCode,
  });

  @override
  List<Object?> get props => [amount, paymentMethod, promoCode];
}

class WithdrawMoney extends WalletEvent {
  final String walletType;
  final double amount;
  final int bankAccountId;

  const WithdrawMoney({
    required this.walletType,
    required this.amount,
    required this.bankAccountId,
  });

  @override
  List<Object?> get props => [walletType, amount, bankAccountId];
}

class LoadTransactions extends WalletEvent {
  final String? walletType;
  final String? transactionType;
  final int page;
  final int limit;

  const LoadTransactions({
    this.walletType,
    this.transactionType,
    this.page = 1,
    this.limit = 20,
  });

  @override
  List<Object?> get props => [walletType, transactionType, page, limit];
}

class RefreshWallets extends WalletEvent {
  const RefreshWallets();
}
