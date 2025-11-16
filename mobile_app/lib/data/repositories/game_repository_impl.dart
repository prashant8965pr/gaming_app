import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../domain/repositories/game_repository.dart';
import '../datasources/local/game_local_datasource.dart';
import '../datasources/remote/game_remote_datasource.dart';
import '../models/game_model.dart';
import '../models/rewards_model.dart';

class GameRepositoryImpl implements GameRepository {
  final GameRemoteDataSource _remoteDataSource;
  final GameLocalDataSource _localDataSource;

  GameRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
  );

  @override
  Future<Either<Failure, List<GameModel>>> getGames() async {
    try {
      final result = await _remoteDataSource.getGames();
      await _localDataSource.cacheGames(result);
      return Right(result);
    } on NetworkException catch (e) {
      final cachedGames = await _localDataSource.getCachedGames();
      if (cachedGames.isNotEmpty) {
        return Right(cachedGames);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameModel>> getGameDetails({
    required String gameId,
  }) async {
    try {
      final result = await _remoteDataSource.getGameDetails(gameId: gameId);
      return Right(result);
    } on NetworkException catch (e) {
      final cachedGame = await _localDataSource.getCachedGame(gameId);
      if (cachedGame != null) {
        return Right(cachedGame);
      }
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<GameSessionModel>>> getActiveSessions({
    required String gameId,
  }) async {
    try {
      final result = await _remoteDataSource.getActiveSessions(gameId: gameId);
      await _localDataSource.cacheActiveSessions(result);
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameSessionModel>> createSession({
    required String gameId,
    required double entryFee,
    required int maxPlayers,
  }) async {
    try {
      final result = await _remoteDataSource.createSession(
        gameId: gameId,
        entryFee: entryFee,
        maxPlayers: maxPlayers,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameSessionModel>> joinSession({
    required String sessionId,
  }) async {
    try {
      final result = await _remoteDataSource.joinSession(sessionId: sessionId);
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> leaveSession({
    required String sessionId,
  }) async {
    try {
      await _remoteDataSource.leaveSession(sessionId: sessionId);
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameSessionModel>> getSessionDetails({
    required String sessionId,
  }) async {
    try {
      final result =
          await _remoteDataSource.getSessionDetails(sessionId: sessionId);
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<GamePlayerModel>>> getSessionPlayers({
    required String sessionId,
  }) async {
    try {
      final result =
          await _remoteDataSource.getSessionPlayers(sessionId: sessionId);
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> markReady({
    required String sessionId,
  }) async {
    try {
      await _remoteDataSource.markReady(sessionId: sessionId);
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameResultModel>> submitResult({
    required String sessionId,
    required Map<String, dynamic> gameData,
  }) async {
    try {
      final result = await _remoteDataSource.submitResult(
        sessionId: sessionId,
        gameData: gameData,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, GameResultModel>> getGameResult({
    required String sessionId,
  }) async {
    try {
      final result = await _remoteDataSource.getGameResult(
        sessionId: sessionId,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<GameResultModel>>> getGameHistory({
    String? gameId,
    int? limit,
    int? offset,
  }) async {
    try {
      final result = await _remoteDataSource.getGameHistory(
        gameId: gameId,
        limit: limit,
        offset: offset,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<TournamentModel>>> getTournaments({
    String? gameId,
    String? status,
  }) async {
    try {
      final result = await _remoteDataSource.getTournaments(
        gameId: gameId,
        status: status,
      );
      await _localDataSource.cacheTournaments(result);
      return Right(result);
    } on NetworkException catch (e) {
      final cachedTournaments =
          await _localDataSource.getCachedTournaments();
      if (cachedTournaments.isNotEmpty) {
        return Right(cachedTournaments);
      }
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, TournamentModel>> getTournamentDetails({
    required String tournamentId,
  }) async {
    try {
      final result = await _remoteDataSource.getTournamentDetails(
        tournamentId: tournamentId,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, void>> registerForTournament({
    required String tournamentId,
  }) async {
    try {
      await _remoteDataSource.registerForTournament(
        tournamentId: tournamentId,
      );
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<LeaderboardEntryModel>>> getLeaderboard({
    String? gameId,
    String? period,
    int? limit,
  }) async {
    try {
      final result = await _remoteDataSource.getLeaderboard(
        gameId: gameId,
        period: period,
        limit: limit,
      );
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<AchievementModel>>> getAchievements() async {
    try {
      final result = await _remoteDataSource.getAchievements();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, ReferralModel>> getReferralData() async {
    try {
      final result = await _remoteDataSource.getReferralData();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }

  @override
  Future<Either<Failure, List<ReferredUserModel>>> getReferredUsers() async {
    try {
      final result = await _remoteDataSource.getReferredUsers();
      return Right(result);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(message: e.message));
    } on AppException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Unexpected error occurred'));
    }
  }
}
