import 'package:equatable/equatable.dart';

abstract class TokenEvent extends Equatable {
  const TokenEvent();

  @override
  List<Object?> get props => [];
}

class LoadTokenBalance extends TokenEvent {
  final bool refresh;

  const LoadTokenBalance({this.refresh = false});

  @override
  List<Object?> get props => [refresh];
}

class ClaimDailyBonus extends TokenEvent {
  const ClaimDailyBonus();
}

class WatchAdForTokens extends TokenEvent {
  const WatchAdForTokens();
}
