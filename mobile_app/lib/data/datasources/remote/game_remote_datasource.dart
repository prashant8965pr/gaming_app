import 'package:dio/dio.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/exceptions.dart';
import '../../models/game_model.dart';
import '../../models/rewards_model.dart';

/// Remote data source for game operations
abstract class GameRemoteDataSource {
  Future<List<GameModel>> getGames();
  Future<GameModel> getGameDetails({required String gameId});

  Future<List<GameSessionModel>> getActiveSessions({required String gameId});
  Future<GameSessionModel> createSession({
    required String gameId,
    required double entryFee,
    required int maxPlayers,
  });
  Future<GameSessionModel> joinSession({required String sessionId});
  Future<void> leaveSession({required String sessionId});
  Future<GameSessionModel> getSessionDetails({required String sessionId});
  Future<List<GamePlayerModel>> getSessionPlayers({required String sessionId});
  Future<void> markReady({required String sessionId});

  Future<GameResultModel> submitResult({
    required String sessionId,
    required Map<String, dynamic> gameData,
  });
  Future<GameResultModel> getGameResult({required String sessionId});
  Future<List<GameResultModel>> getGameHistory({
    String? gameId,
    int? limit,
    int? offset,
  });

  Future<List<TournamentModel>> getTournaments({
    String? gameId,
    String? status,
  });
  Future<TournamentModel> getTournamentDetails({required String tournamentId});
  Future<void> registerForTournament({required String tournamentId});

  Future<List<LeaderboardEntryModel>> getLeaderboard({
    String? gameId,
    String? period,
    int? limit,
  });
  Future<List<AchievementModel>> getAchievements();
  Future<ReferralModel> getReferralData();
  Future<List<ReferredUserModel>> getReferredUsers();
}

class GameRemoteDataSourceImpl implements GameRemoteDataSource {
  final Dio _dio;

  GameRemoteDataSourceImpl(this._dio);

  @override
  Future<List<GameModel>> getGames() async {
    try {
      final response = await _dio.get(ApiEndpoints.games);
      final List<dynamic> data = response.data['data'];
      return data.map((json) => GameModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameModel> getGameDetails({required String gameId}) async {
    try {
      final response = await _dio.get(ApiEndpoints.gameDetails(gameId));
      return GameModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<GameSessionModel>> getActiveSessions({
    required String gameId,
  }) async {
    try {
      final response = await _dio.get(ApiEndpoints.gameSessions(gameId));
      final List<dynamic> data = response.data['data'];
      return data.map((json) => GameSessionModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameSessionModel> createSession({
    required String gameId,
    required double entryFee,
    required int maxPlayers,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.createSession,
        data: {
          'game_id': gameId,
          'entry_fee': entryFee,
          'max_players': maxPlayers,
        },
      );
      return GameSessionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameSessionModel> joinSession({required String sessionId}) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.joinSession(sessionId),
      );
      return GameSessionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> leaveSession({required String sessionId}) async {
    try {
      await _dio.post(ApiEndpoints.leaveSession(sessionId));
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameSessionModel> getSessionDetails({
    required String sessionId,
  }) async {
    try {
      final response = await _dio.get(ApiEndpoints.sessionDetails(sessionId));
      return GameSessionModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<GamePlayerModel>> getSessionPlayers({
    required String sessionId,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.sessionPlayers(sessionId),
      );
      final List<dynamic> data = response.data['data'];
      return data.map((json) => GamePlayerModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> markReady({required String sessionId}) async {
    try {
      await _dio.post(ApiEndpoints.markReady(sessionId));
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameResultModel> submitResult({
    required String sessionId,
    required Map<String, dynamic> gameData,
  }) async {
    try {
      final response = await _dio.post(
        ApiEndpoints.submitResult(sessionId),
        data: gameData,
      );
      return GameResultModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<GameResultModel> getGameResult({required String sessionId}) async {
    try {
      final response = await _dio.get(ApiEndpoints.gameResult(sessionId));
      return GameResultModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<GameResultModel>> getGameHistory({
    String? gameId,
    int? limit,
    int? offset,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.gameHistory,
        queryParameters: {
          if (gameId != null) 'game_id': gameId,
          if (limit != null) 'limit': limit,
          if (offset != null) 'offset': offset,
        },
      );
      final List<dynamic> data = response.data['data'];
      return data.map((json) => GameResultModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<TournamentModel>> getTournaments({
    String? gameId,
    String? status,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.tournaments,
        queryParameters: {
          if (gameId != null) 'game_id': gameId,
          if (status != null) 'status': status,
        },
      );
      final List<dynamic> data = response.data['data'];
      return data.map((json) => TournamentModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<TournamentModel> getTournamentDetails({
    required String tournamentId,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.tournamentDetails(tournamentId),
      );
      return TournamentModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<void> registerForTournament({required String tournamentId}) async {
    try {
      await _dio.post(ApiEndpoints.tournamentRegister(tournamentId));
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<LeaderboardEntryModel>> getLeaderboard({
    String? gameId,
    String? period,
    int? limit,
  }) async {
    try {
      final response = await _dio.get(
        ApiEndpoints.leaderboard,
        queryParameters: {
          if (gameId != null) 'game_id': gameId,
          if (period != null) 'period': period,
          if (limit != null) 'limit': limit,
        },
      );
      final List<dynamic> data = response.data['data'];
      return data
          .map((json) => LeaderboardEntryModel.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<AchievementModel>> getAchievements() async {
    try {
      final response = await _dio.get(ApiEndpoints.achievements);
      final List<dynamic> data = response.data['data'];
      return data.map((json) => AchievementModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<ReferralModel> getReferralData() async {
    try {
      final response = await _dio.get(ApiEndpoints.referralData);
      return ReferralModel.fromJson(response.data['data']);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  @override
  Future<List<ReferredUserModel>> getReferredUsers() async {
    try {
      final response = await _dio.get(ApiEndpoints.referredUsers);
      final List<dynamic> data = response.data['data'];
      return data.map((json) => ReferredUserModel.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  AppException _handleError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return NetworkException(message: 'Connection timeout');
    }

    if (error.type == DioExceptionType.connectionError) {
      return NetworkException(message: 'No internet connection');
    }

    final statusCode = error.response?.statusCode;
    final message = error.response?.data['message'] ?? 'An error occurred';

    switch (statusCode) {
      case 400:
        return ValidationException(message: message);
      case 401:
        return UnauthorizedException(message: message);
      case 404:
        return NotFoundException(message: message);
      case 500:
        return ServerException(message: message);
      default:
        return ServerException(message: message);
    }
  }
}
