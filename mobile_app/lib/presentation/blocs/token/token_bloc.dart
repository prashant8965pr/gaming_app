import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/token_repository.dart';
import 'token_event.dart';
import 'token_state.dart';

class TokenBloc extends Bloc<TokenEvent, TokenState> {
  final TokenRepository tokenRepository;

  TokenBloc({required this.tokenRepository}) : super(const TokenState()) {
    on<LoadTokenWallet>(_onLoadTokenWallet);
    on<ClaimDailyBonus>(_onClaimDailyBonus);
    on<WatchAdForTokens>(_onWatchAdForTokens);
    on<LoadTokenHistory>(_onLoadTokenHistory);
    on<SpendTokens>(_onSpendTokens);
    on<RefreshTokenWallet>(_onRefreshTokenWallet);
  }

  Future<void> _onLoadTokenWallet(
    LoadTokenWallet event,
    Emitter<TokenState> emit,
  ) async {
    emit(state.copyWith(status: TokenStatus.loading));

    try {
      final result = await tokenRepository.getTokenWallet();

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TokenStatus.error,
            errorMessage: failure.message,
          ));
        },
        (wallet) {
          emit(state.copyWith(
            status: TokenStatus.loaded,
            tokenWallet: wallet,
            canClaimDaily: wallet.canClaimDailyBonus,
            adsWatchedToday: wallet.adsWatchedToday,
            canWatchAd: wallet.adsWatchedToday < 5,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Failed to load token wallet: $e',
      ));
    }
  }

  Future<void> _onClaimDailyBonus(
    ClaimDailyBonus event,
    Emitter<TokenState> emit,
  ) async {
    if (!state.canClaimDaily) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Daily bonus already claimed today',
      ));
      return;
    }

    emit(state.copyWith(status: TokenStatus.claiming));

    try {
      final result = await tokenRepository.claimDailyBonus();

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TokenStatus.error,
            errorMessage: failure.message,
          ));
        },
        (response) {
          emit(state.copyWith(status: TokenStatus.loaded));
          add(const RefreshTokenWallet());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Failed to claim daily bonus: $e',
      ));
    }
  }

  Future<void> _onWatchAdForTokens(
    WatchAdForTokens event,
    Emitter<TokenState> emit,
  ) async {
    if (!state.canWatchAd) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Ad limit reached for today',
      ));
      return;
    }

    emit(state.copyWith(status: TokenStatus.claiming));

    try {
      final result = await tokenRepository.watchAdForTokens();

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TokenStatus.error,
            errorMessage: failure.message,
          ));
        },
        (response) {
          emit(state.copyWith(status: TokenStatus.loaded));
          add(const RefreshTokenWallet());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Failed to watch ad: $e',
      ));
    }
  }

  Future<void> _onLoadTokenHistory(
    LoadTokenHistory event,
    Emitter<TokenState> emit,
  ) async {
    if (event.page == 1) {
      emit(state.copyWith(status: TokenStatus.loading));
    }

    try {
      final result = await tokenRepository.getTokenHistory(page: event.page);

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TokenStatus.error,
            errorMessage: failure.message,
          ));
        },
        (newTransactions) {
          final updatedTransactions = event.page == 1
              ? newTransactions
              : [...state.transactions, ...newTransactions];

          emit(state.copyWith(
            status: TokenStatus.loaded,
            transactions: updatedTransactions,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Failed to load token history: $e',
      ));
    }
  }

  Future<void> _onSpendTokens(
    SpendTokens event,
    Emitter<TokenState> emit,
  ) async {
    if (state.tokenBalance < event.amount) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Insufficient tokens',
      ));
      return;
    }

    emit(state.copyWith(status: TokenStatus.loading));

    try {
      // Spend tokens logic would go here
      emit(state.copyWith(status: TokenStatus.loaded));
      add(const RefreshTokenWallet());
    } catch (e) {
      emit(state.copyWith(
        status: TokenStatus.error,
        errorMessage: 'Failed to spend tokens: $e',
      ));
    }
  }

  Future<void> _onRefreshTokenWallet(
    RefreshTokenWallet event,
    Emitter<TokenState> emit,
  ) async {
    try {
      final result = await tokenRepository.getTokenWallet();

      result.fold(
        (failure) {
          // Silent fail
        },
        (wallet) {
          emit(state.copyWith(
            tokenWallet: wallet,
            canClaimDaily: wallet.canClaimDailyBonus,
            adsWatchedToday: wallet.adsWatchedToday,
            canWatchAd: wallet.adsWatchedToday < 5,
          ));
        },
      );
    } catch (e) {
      // Silent fail
    }
  }
}
