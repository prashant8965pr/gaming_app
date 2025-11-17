import 'package:equatable/equatable.dart';
import '../../../data/models/tournament_model.dart';

abstract class TournamentState extends Equatable {
  const TournamentState();

  @override
  List<Object?> get props => [];
}

class TournamentInitial extends TournamentState {}

class TournamentLoading extends TournamentState {}

class TournamentLoaded extends TournamentState {
  final List<TournamentModel> tournaments;
  final bool hasMore;

  const TournamentLoaded({
    required this.tournaments,
    this.hasMore = true,
  });

  @override
  List<Object?> get props => [tournaments, hasMore];
}

class TournamentDetailsLoading extends TournamentState {}

class TournamentDetailsLoaded extends TournamentState {
  final TournamentModel tournament;

  const TournamentDetailsLoaded(this.tournament);

  @override
  List<Object?> get props => [tournament];
}

class TournamentRegistering extends TournamentState {}

class TournamentRegistered extends TournamentState {
  final TournamentRegistrationModel registration;

  const TournamentRegistered(this.registration);

  @override
  List<Object?> get props => [registration];
}

class TournamentBracketLoading extends TournamentState {}

class TournamentBracketLoaded extends TournamentState {
  final TournamentBracketModel bracket;

  const TournamentBracketLoaded(this.bracket);

  @override
  List<Object?> get props => [bracket];
}

class MyTournamentsLoading extends TournamentState {}

class MyTournamentsLoaded extends TournamentState {
  final List<TournamentRegistrationModel> registrations;

  const MyTournamentsLoaded(this.registrations);

  @override
  List<Object?> get props => [registrations];
}

class TournamentError extends TournamentState {
  final String message;

  const TournamentError(this.message);

  @override
  List<Object?> get props => [message];
}
