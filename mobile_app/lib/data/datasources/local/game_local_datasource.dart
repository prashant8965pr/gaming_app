import 'package:hive/hive.dart';
import '../../models/game_model.dart';
import '../../../core/storage/hive_config.dart';

/// Local data source for game data
abstract class GameLocalDataSource {
  Future<void> cacheGames(List<GameModel> games);
  Future<List<GameModel>> getCachedGames();
  Future<GameModel?> getCachedGame(String gameId);

  Future<void> cacheActiveSessions(List<GameSessionModel> sessions);
  Future<List<GameSessionModel>> getCachedActiveSessions();

  Future<void> cacheTournaments(List<TournamentModel> tournaments);
  Future<List<TournamentModel>> getCachedTournaments();
}

class GameLocalDataSourceImpl implements GameLocalDataSource {
  final Box _gamesBox;
  final CacheHelper _cacheHelper;

  GameLocalDataSourceImpl(this._gamesBox, this._cacheHelper);

  static const String _gamesKey = 'games_list';
  static const String _activeSessionsKey = 'active_sessions';
  static const String _tournamentsKey = 'tournaments';

  @override
  Future<void> cacheGames(List<GameModel> games) async {
    final gamesData = games.map((e) => e.toJson()).toList();
    await _gamesBox.put(_gamesKey, gamesData);
    await _cacheHelper.save(
      key: CacheKeys.gamesList,
      data: gamesData,
      expiresIn: const Duration(hours: 12),
    );
  }

  @override
  Future<List<GameModel>> getCachedGames() async {
    final gamesData = _gamesBox.get(_gamesKey);
    if (gamesData == null) return [];

    try {
      final List<dynamic> dataList = gamesData;
      return dataList
          .map((e) => GameModel.fromJson(Map<String, dynamic>.from(e)))
          .toList();
    } catch (e) {
      return [];
    }
  }

  @override
  Future<GameModel?> getCachedGame(String gameId) async {
    final games = await getCachedGames();
    try {
      return games.firstWhere((game) => game.id == gameId);
    } catch (e) {
      return null;
    }
  }

  @override
  Future<void> cacheActiveSessions(List<GameSessionModel> sessions) async {
    final sessionsData = sessions.map((e) => e.toJson()).toList();
    await _gamesBox.put(_activeSessionsKey, sessionsData);
    await _cacheHelper.save(
      key: CacheKeys.activeGames,
      data: sessionsData,
      expiresIn: const Duration(minutes: 2),
    );
  }

  @override
  Future<List<GameSessionModel>> getCachedActiveSessions() async {
    final sessionsData = _gamesBox.get(_activeSessionsKey);
    if (sessionsData == null) return [];

    try {
      final List<dynamic> dataList = sessionsData;
      return dataList
          .map((e) => GameSessionModel.fromJson(Map<String, dynamic>.from(e)))
          .toList();
    } catch (e) {
      return [];
    }
  }

  @override
  Future<void> cacheTournaments(List<TournamentModel> tournaments) async {
    final tournamentsData = tournaments.map((e) => e.toJson()).toList();
    await _gamesBox.put(_tournamentsKey, tournamentsData);
  }

  @override
  Future<List<TournamentModel>> getCachedTournaments() async {
    final tournamentsData = _gamesBox.get(_tournamentsKey);
    if (tournamentsData == null) return [];

    try {
      final List<dynamic> dataList = tournamentsData;
      return dataList
          .map((e) => TournamentModel.fromJson(Map<String, dynamic>.from(e)))
          .toList();
    } catch (e) {
      return [];
    }
  }
}
