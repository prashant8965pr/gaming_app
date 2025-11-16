import 'package:equatable/equatable.dart';
import '../../../data/models/wallet_model.dart';

/// Base class for all wallet states
abstract class WalletState extends Equatable {
  const WalletState();

  @override
  List<Object?> get props => [];
}

/// Initial state
class WalletInitial extends WalletState {
  const WalletInitial();
}

/// Loading state
class WalletLoading extends WalletState {
  const WalletLoading();
}

/// Wallet balance loaded
class WalletBalanceLoaded extends WalletState {
  final WalletBalanceModel balance;

  const WalletBalanceLoaded({required this.balance});

  @override
  List<Object?> get props => [balance];
}

/// Money added successfully
class MoneyAdded extends WalletState {
  final TransactionModel transaction;

  const MoneyAdded({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

/// Money withdrawn successfully
class MoneyWithdrawn extends WalletState {
  final TransactionModel transaction;

  const MoneyWithdrawn({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

/// Transactions loaded
class TransactionsLoaded extends WalletState {
  final List<TransactionModel> transactions;

  const TransactionsLoaded({required this.transactions});

  @override
  List<Object?> get props => [transactions];
}

/// Transaction details loaded
class TransactionDetailsLoaded extends WalletState {
  final TransactionModel transaction;

  const TransactionDetailsLoaded({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

/// Bank account added
class BankAccountAdded extends WalletState {
  final BankAccountModel account;

  const BankAccountAdded({required this.account});

  @override
  List<Object?> get props => [account];
}

/// Bank accounts loaded
class BankAccountsLoaded extends WalletState {
  final List<BankAccountModel> accounts;

  const BankAccountsLoaded({required this.accounts});

  @override
  List<Object?> get props => [accounts];
}

/// Bank account deleted
class BankAccountDeleted extends WalletState {
  const BankAccountDeleted();
}

/// Primary bank account set
class PrimaryBankAccountSet extends WalletState {
  const PrimaryBankAccountSet();
}

/// Promo code validated
class PromoCodeValidated extends WalletState {
  final PromoCodeModel promoCode;

  const PromoCodeValidated({required this.promoCode});

  @override
  List<Object?> get props => [promoCode];
}

/// Promo code applied
class PromoCodeApplied extends WalletState {
  const PromoCodeApplied();
}

/// Error state
class WalletError extends WalletState {
  final String message;

  const WalletError({required this.message});

  @override
  List<Object?> get props => [message];
}
