import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../../data/models/game_model.dart';
import '../../data/models/rewards_model.dart';

/// Game repository interface
abstract class GameRepository {
  /// Get all available games
  Future<Either<Failure, List<GameModel>>> getGames();

  /// Get game details
  Future<Either<Failure, GameModel>> getGameDetails({
    required String gameId,
  });

  /// Get active game sessions
  Future<Either<Failure, List<GameSessionModel>>> getActiveSessions({
    required String gameId,
  });

  /// Create new game session
  Future<Either<Failure, GameSessionModel>> createSession({
    required String gameId,
    required double entryFee,
    required int maxPlayers,
  });

  /// Join game session
  Future<Either<Failure, GameSessionModel>> joinSession({
    required String sessionId,
  });

  /// Leave game session
  Future<Either<Failure, void>> leaveSession({
    required String sessionId,
  });

  /// Get session details
  Future<Either<Failure, GameSessionModel>> getSessionDetails({
    required String sessionId,
  });

  /// Get session players
  Future<Either<Failure, List<GamePlayerModel>>> getSessionPlayers({
    required String sessionId,
  });

  /// Mark player as ready
  Future<Either<Failure, void>> markReady({
    required String sessionId,
  });

  /// Submit game result
  Future<Either<Failure, GameResultModel>> submitResult({
    required String sessionId,
    required Map<String, dynamic> gameData,
  });

  /// Get game result
  Future<Either<Failure, GameResultModel>> getGameResult({
    required String sessionId,
  });

  /// Get game history
  Future<Either<Failure, List<GameResultModel>>> getGameHistory({
    String? gameId,
    int? limit,
    int? offset,
  });

  /// Get tournaments
  Future<Either<Failure, List<TournamentModel>>> getTournaments({
    String? gameId,
    String? status,
  });

  /// Get tournament details
  Future<Either<Failure, TournamentModel>> getTournamentDetails({
    required String tournamentId,
  });

  /// Register for tournament
  Future<Either<Failure, void>> registerForTournament({
    required String tournamentId,
  });

  /// Get leaderboard
  Future<Either<Failure, List<LeaderboardEntryModel>>> getLeaderboard({
    String? gameId,
    String? period,
    int? limit,
  });

  /// Get achievements
  Future<Either<Failure, List<AchievementModel>>> getAchievements();

  /// Get referral data
  Future<Either<Failure, ReferralModel>> getReferralData();

  /// Get referred users
  Future<Either<Failure, List<ReferredUserModel>>> getReferredUsers();
}
