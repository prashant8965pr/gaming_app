import 'package:equatable/equatable.dart';

abstract class TournamentEvent extends Equatable {
  const TournamentEvent();

  @override
  List<Object?> get props => [];
}

class LoadTournaments extends TournamentEvent {
  final String? status;
  final String? gameId;
  final bool? isFeatured;
  final bool refresh;

  const LoadTournaments({
    this.status,
    this.gameId,
    this.isFeatured,
    this.refresh = false,
  });

  @override
  List<Object?> get props => [status, gameId, isFeatured, refresh];
}

class LoadTournamentDetails extends TournamentEvent {
  final String tournamentId;

  const LoadTournamentDetails(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class RegisterForTournament extends TournamentEvent {
  final String tournamentId;

  const RegisterForTournament(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class LoadTournamentBracket extends TournamentEvent {
  final String tournamentId;

  const LoadTournamentBracket(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class LoadMyTournaments extends TournamentEvent {
  final bool refresh;

  const LoadMyTournaments({this.refresh = false});

  @override
  List<Object?> get props => [refresh];
}

class FilterTournaments extends TournamentEvent {
  final String? status;
  final String? gameId;

  const FilterTournaments({
    this.status,
    this.gameId,
  });

  @override
  List<Object?> get props => [status, gameId];
}
