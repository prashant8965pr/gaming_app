import 'package:equatable/equatable.dart';
import '../../../data/models/token_model.dart';

abstract class TokenState extends Equatable {
  const TokenState();

  @override
  List<Object?> get props => [];
}

class TokenInitial extends TokenState {}

class TokenLoading extends TokenState {}

class TokenLoaded extends TokenState {
  final TokenWalletModel wallet;

  const TokenLoaded(this.wallet);

  @override
  List<Object?> get props => [wallet];
}

class TokenClaiming extends TokenState {}

class DailyBonusClaimed extends TokenState {
  final DailyBonusResponse response;
  final TokenWalletModel? wallet;

  const DailyBonusClaimed(this.response, {this.wallet});

  @override
  List<Object?> get props => [response, wallet];
}

class AdRewardEarned extends TokenState {
  final AdRewardResponse response;
  final TokenWalletModel? wallet;

  const AdRewardEarned(this.response, {this.wallet});

  @override
  List<Object?> get props => [response, wallet];
}

class TokenError extends TokenState {
  final String message;

  const TokenError(this.message);

  @override
  List<Object?> get props => [message];
}
