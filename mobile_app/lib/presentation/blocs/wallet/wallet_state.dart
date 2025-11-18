import 'package:equatable/equatable.dart';
import '../../../data/models/wallet_model.dart';

enum WalletStatus { initial, loading, loaded, error, depositing, withdrawing }

class WalletState extends Equatable {
  final WalletStatus status;
  final List<WalletModel> wallets;
  final List<TransactionModel> transactions;
  final String? errorMessage;
  final bool hasMoreTransactions;
  final int currentPage;

  const WalletState({
    this.status = WalletStatus.initial,
    this.wallets = const [],
    this.transactions = const [],
    this.errorMessage,
    this.hasMoreTransactions = true,
    this.currentPage = 1,
  });

  double get totalBalance {
    return wallets.fold(0.0, (sum, wallet) => sum + wallet.balance);
  }

  WalletModel? getWalletByType(String type) {
    try {
      return wallets.firstWhere((w) => w.walletType == type);
    } catch (e) {
      return null;
    }
  }

  WalletState copyWith({
    WalletStatus? status,
    List<WalletModel>? wallets,
    List<TransactionModel>? transactions,
    String? errorMessage,
    bool? hasMoreTransactions,
    int? currentPage,
  }) {
    return WalletState(
      status: status ?? this.status,
      wallets: wallets ?? this.wallets,
      transactions: transactions ?? this.transactions,
      errorMessage: errorMessage,
      hasMoreTransactions: hasMoreTransactions ?? this.hasMoreTransactions,
      currentPage: currentPage ?? this.currentPage,
    );
  }

  @override
  List<Object?> get props => [
        status,
        wallets,
        transactions,
        errorMessage,
        hasMoreTransactions,
        currentPage,
      ];
}
