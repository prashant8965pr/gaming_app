import 'package:equatable/equatable.dart';

/// Base class for all game events
abstract class GameEvent extends Equatable {
  const GameEvent();

  @override
  List<Object?> get props => [];
}

/// Event to load all games
class LoadGamesEvent extends GameEvent {
  const LoadGamesEvent();
}

/// Event to load game details
class LoadGameDetailsEvent extends GameEvent {
  final String gameId;

  const LoadGameDetailsEvent({required this.gameId});

  @override
  List<Object?> get props => [gameId];
}

/// Event to load active game sessions
class LoadActiveSessionsEvent extends GameEvent {
  final String gameId;

  const LoadActiveSessionsEvent({required this.gameId});

  @override
  List<Object?> get props => [gameId];
}

/// Event to create new game session
class CreateSessionEvent extends GameEvent {
  final String gameId;
  final double entryFee;
  final int maxPlayers;

  const CreateSessionEvent({
    required this.gameId,
    required this.entryFee,
    required this.maxPlayers,
  });

  @override
  List<Object?> get props => [gameId, entryFee, maxPlayers];
}

/// Event to join game session
class JoinSessionEvent extends GameEvent {
  final String sessionId;

  const JoinSessionEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to leave game session
class LeaveSessionEvent extends GameEvent {
  final String sessionId;

  const LeaveSessionEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to load session details
class LoadSessionDetailsEvent extends GameEvent {
  final String sessionId;

  const LoadSessionDetailsEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to load session players
class LoadSessionPlayersEvent extends GameEvent {
  final String sessionId;

  const LoadSessionPlayersEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to mark player as ready
class MarkReadyEvent extends GameEvent {
  final String sessionId;

  const MarkReadyEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to submit game result
class SubmitResultEvent extends GameEvent {
  final String sessionId;
  final Map<String, dynamic> gameData;

  const SubmitResultEvent({
    required this.sessionId,
    required this.gameData,
  });

  @override
  List<Object?> get props => [sessionId, gameData];
}

/// Event to load game result
class LoadGameResultEvent extends GameEvent {
  final String sessionId;

  const LoadGameResultEvent({required this.sessionId});

  @override
  List<Object?> get props => [sessionId];
}

/// Event to load game history
class LoadGameHistoryEvent extends GameEvent {
  final String? gameId;
  final int? limit;
  final int? offset;

  const LoadGameHistoryEvent({
    this.gameId,
    this.limit,
    this.offset,
  });

  @override
  List<Object?> get props => [gameId, limit, offset];
}

/// Event to load tournaments
class LoadTournamentsEvent extends GameEvent {
  final String? gameId;
  final String? status;

  const LoadTournamentsEvent({
    this.gameId,
    this.status,
  });

  @override
  List<Object?> get props => [gameId, status];
}

/// Event to load tournament details
class LoadTournamentDetailsEvent extends GameEvent {
  final String tournamentId;

  const LoadTournamentDetailsEvent({required this.tournamentId});

  @override
  List<Object?> get props => [tournamentId];
}

/// Event to register for tournament
class RegisterForTournamentEvent extends GameEvent {
  final String tournamentId;

  const RegisterForTournamentEvent({required this.tournamentId});

  @override
  List<Object?> get props => [tournamentId];
}

/// Event to load leaderboard
class LoadLeaderboardEvent extends GameEvent {
  final String? gameId;
  final String? period;
  final int? limit;

  const LoadLeaderboardEvent({
    this.gameId,
    this.period,
    this.limit,
  });

  @override
  List<Object?> get props => [gameId, period, limit];
}

/// Event to load achievements
class LoadAchievementsEvent extends GameEvent {
  const LoadAchievementsEvent();
}

/// Event to load referral data
class LoadReferralDataEvent extends GameEvent {
  const LoadReferralDataEvent();
}

/// Event to load referred users
class LoadReferredUsersEvent extends GameEvent {
  const LoadReferredUsersEvent();
}
