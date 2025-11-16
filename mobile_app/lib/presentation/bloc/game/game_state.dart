import 'package:equatable/equatable.dart';
import '../../../data/models/game_model.dart';
import '../../../data/models/rewards_model.dart';

/// Base class for all game states
abstract class GameState extends Equatable {
  const GameState();

  @override
  List<Object?> get props => [];
}

/// Initial state
class GameInitial extends GameState {
  const GameInitial();
}

/// Loading state
class GameLoading extends GameState {
  const GameLoading();
}

/// Games loaded
class GamesLoaded extends GameState {
  final List<GameModel> games;

  const GamesLoaded({required this.games});

  @override
  List<Object?> get props => [games];
}

/// Game details loaded
class GameDetailsLoaded extends GameState {
  final GameModel game;

  const GameDetailsLoaded({required this.game});

  @override
  List<Object?> get props => [game];
}

/// Active sessions loaded
class ActiveSessionsLoaded extends GameState {
  final List<GameSessionModel> sessions;

  const ActiveSessionsLoaded({required this.sessions});

  @override
  List<Object?> get props => [sessions];
}

/// Session created
class SessionCreated extends GameState {
  final GameSessionModel session;

  const SessionCreated({required this.session});

  @override
  List<Object?> get props => [session];
}

/// Session joined
class SessionJoined extends GameState {
  final GameSessionModel session;

  const SessionJoined({required this.session});

  @override
  List<Object?> get props => [session];
}

/// Session left
class SessionLeft extends GameState {
  const SessionLeft();
}

/// Session details loaded
class SessionDetailsLoaded extends GameState {
  final GameSessionModel session;

  const SessionDetailsLoaded({required this.session});

  @override
  List<Object?> get props => [session];
}

/// Session players loaded
class SessionPlayersLoaded extends GameState {
  final List<GamePlayerModel> players;

  const SessionPlayersLoaded({required this.players});

  @override
  List<Object?> get props => [players];
}

/// Player marked as ready
class PlayerMarkedReady extends GameState {
  const PlayerMarkedReady();
}

/// Game result submitted
class ResultSubmitted extends GameState {
  final GameResultModel result;

  const ResultSubmitted({required this.result});

  @override
  List<Object?> get props => [result];
}

/// Game result loaded
class GameResultLoaded extends GameState {
  final GameResultModel result;

  const GameResultLoaded({required this.result});

  @override
  List<Object?> get props => [result];
}

/// Game history loaded
class GameHistoryLoaded extends GameState {
  final List<GameResultModel> history;

  const GameHistoryLoaded({required this.history});

  @override
  List<Object?> get props => [history];
}

/// Tournaments loaded
class TournamentsLoaded extends GameState {
  final List<TournamentModel> tournaments;

  const TournamentsLoaded({required this.tournaments});

  @override
  List<Object?> get props => [tournaments];
}

/// Tournament details loaded
class TournamentDetailsLoaded extends GameState {
  final TournamentModel tournament;

  const TournamentDetailsLoaded({required this.tournament});

  @override
  List<Object?> get props => [tournament];
}

/// Tournament registered
class TournamentRegistered extends GameState {
  const TournamentRegistered();
}

/// Leaderboard loaded
class LeaderboardLoaded extends GameState {
  final List<LeaderboardEntryModel> entries;

  const LeaderboardLoaded({required this.entries});

  @override
  List<Object?> get props => [entries];
}

/// Achievements loaded
class AchievementsLoaded extends GameState {
  final List<AchievementModel> achievements;

  const AchievementsLoaded({required this.achievements});

  @override
  List<Object?> get props => [achievements];
}

/// Referral data loaded
class ReferralDataLoaded extends GameState {
  final ReferralModel referral;

  const ReferralDataLoaded({required this.referral});

  @override
  List<Object?> get props => [referral];
}

/// Referred users loaded
class ReferredUsersLoaded extends GameState {
  final List<ReferredUserModel> users;

  const ReferredUsersLoaded({required this.users});

  @override
  List<Object?> get props => [users];
}

/// Error state
class GameError extends GameState {
  final String message;

  const GameError({required this.message});

  @override
  List<Object?> get props => [message];
}
