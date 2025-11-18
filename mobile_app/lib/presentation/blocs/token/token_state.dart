import 'package:equatable/equatable.dart';
import '../../../data/models/token_model.dart';

enum TokenStatus { initial, loading, loaded, claiming, error }

class TokenState extends Equatable {
  final TokenStatus status;
  final TokenWalletModel? tokenWallet;
  final List<TokenTransactionModel> transactions;
  final String? errorMessage;
  final bool canClaimDaily;
  final bool canWatchAd;
  final int adsWatchedToday;

  const TokenState({
    this.status = TokenStatus.initial,
    this.tokenWallet,
    this.transactions = const [],
    this.errorMessage,
    this.canClaimDaily = false,
    this.canWatchAd = true,
    this.adsWatchedToday = 0,
  });

  int get tokenBalance => tokenWallet?.balance ?? 0;
  int get currentStreak => tokenWallet?.dailyLoginStreak ?? 0;

  TokenState copyWith({
    TokenStatus? status,
    TokenWalletModel? tokenWallet,
    List<TokenTransactionModel>? transactions,
    String? errorMessage,
    bool? canClaimDaily,
    bool? canWatchAd,
    int? adsWatchedToday,
  }) {
    return TokenState(
      status: status ?? this.status,
      tokenWallet: tokenWallet ?? this.tokenWallet,
      transactions: transactions ?? this.transactions,
      errorMessage: errorMessage,
      canClaimDaily: canClaimDaily ?? this.canClaimDaily,
      canWatchAd: canWatchAd ?? this.canWatchAd,
      adsWatchedToday: adsWatchedToday ?? this.adsWatchedToday,
    );
  }

  @override
  List<Object?> get props => [
        status,
        tokenWallet,
        transactions,
        errorMessage,
        canClaimDaily,
        canWatchAd,
        adsWatchedToday,
      ];
}
