import 'package:equatable/equatable.dart';

abstract class TokenEvent extends Equatable {
  const TokenEvent();

  @override
  List<Object?> get props => [];
}

class LoadTokenWallet extends TokenEvent {
  const LoadTokenWallet();
}

class ClaimDailyBonus extends TokenEvent {
  const ClaimDailyBonus();
}

class WatchAdForTokens extends TokenEvent {
  const WatchAdForTokens();
}

class LoadTokenHistory extends TokenEvent {
  final int page;

  const LoadTokenHistory({this.page = 1});

  @override
  List<Object?> get props => [page];
}

class SpendTokens extends TokenEvent {
  final int amount;
  final String purpose;

  const SpendTokens({
    required this.amount,
    required this.purpose,
  });

  @override
  List<Object?> get props => [amount, purpose];
}

class RefreshTokenWallet extends TokenEvent {
  const RefreshTokenWallet();
}
