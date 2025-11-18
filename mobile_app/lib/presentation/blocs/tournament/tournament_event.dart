import 'package:equatable/equatable.dart';

abstract class TournamentEvent extends Equatable {
  const TournamentEvent();

  @override
  List<Object?> get props => [];
}

class LoadTournaments extends TournamentEvent {
  final String status;
  final int page;

  const LoadTournaments({
    this.status = 'upcoming',
    this.page = 1,
  });

  @override
  List<Object?> get props => [status, page];
}

class LoadTournamentDetails extends TournamentEvent {
  final int tournamentId;

  const LoadTournamentDetails(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class RegisterForTournament extends TournamentEvent {
  final int tournamentId;

  const RegisterForTournament(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class LoadTournamentBracket extends TournamentEvent {
  final int tournamentId;

  const LoadTournamentBracket(this.tournamentId);

  @override
  List<Object?> get props => [tournamentId];
}

class LoadMyTournaments extends TournamentEvent {
  const LoadMyTournaments();
}

class RefreshTournaments extends TournamentEvent {
  const RefreshTournaments();
}
