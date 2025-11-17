import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/token_repository.dart';
import 'token_event.dart';
import 'token_state.dart';

class TokenBloc extends Bloc<TokenEvent, TokenState> {
  final TokenRepository repository;

  TokenBloc({required this.repository}) : super(TokenInitial()) {
    on<LoadTokenBalance>(_onLoadTokenBalance);
    on<ClaimDailyBonus>(_onClaimDailyBonus);
    on<WatchAdForTokens>(_onWatchAdForTokens);
  }

  Future<void> _onLoadTokenBalance(
    LoadTokenBalance event,
    Emitter<TokenState> emit,
  ) async {
    if (event.refresh) {
      emit(TokenLoading());
    }

    final result = await repository.getBalance();

    result.fold(
      (failure) => emit(TokenError(failure.message)),
      (wallet) => emit(TokenLoaded(wallet)),
    );
  }

  Future<void> _onClaimDailyBonus(
    ClaimDailyBonus event,
    Emitter<TokenState> emit,
  ) async {
    emit(TokenClaiming());

    final result = await repository.claimDailyBonus();

    await result.fold(
      (failure) async {
        emit(TokenError(failure.message));
      },
      (response) async {
        // Reload wallet balance after claiming
        final walletResult = await repository.getBalance();
        walletResult.fold(
          (failure) => emit(DailyBonusClaimed(response)),
          (wallet) => emit(DailyBonusClaimed(response, wallet: wallet)),
        );
      },
    );
  }

  Future<void> _onWatchAdForTokens(
    WatchAdForTokens event,
    Emitter<TokenState> emit,
  ) async {
    emit(TokenClaiming());

    final result = await repository.earnFromAd();

    await result.fold(
      (failure) async {
        emit(TokenError(failure.message));
      },
      (response) async {
        // Reload wallet balance after earning
        final walletResult = await repository.getBalance();
        walletResult.fold(
          (failure) => emit(AdRewardEarned(response)),
          (wallet) => emit(AdRewardEarned(response, wallet: wallet)),
        );
      },
    );
  }
}
