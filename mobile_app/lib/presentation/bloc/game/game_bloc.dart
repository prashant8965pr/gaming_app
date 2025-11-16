import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/game_repository.dart';
import 'game_event.dart';
import 'game_state.dart';

class GameBloc extends Bloc<GameEvent, GameState> {
  final GameRepository _gameRepository;

  GameBloc({required GameRepository gameRepository})
      : _gameRepository = gameRepository,
        super(const GameInitial()) {
    on<LoadGamesEvent>(_onLoadGames);
    on<LoadGameDetailsEvent>(_onLoadGameDetails);
    on<LoadActiveSessionsEvent>(_onLoadActiveSessions);
    on<CreateSessionEvent>(_onCreateSession);
    on<JoinSessionEvent>(_onJoinSession);
    on<LeaveSessionEvent>(_onLeaveSession);
    on<LoadSessionDetailsEvent>(_onLoadSessionDetails);
    on<LoadSessionPlayersEvent>(_onLoadSessionPlayers);
    on<MarkReadyEvent>(_onMarkReady);
    on<SubmitResultEvent>(_onSubmitResult);
    on<LoadGameResultEvent>(_onLoadGameResult);
    on<LoadGameHistoryEvent>(_onLoadGameHistory);
    on<LoadTournamentsEvent>(_onLoadTournaments);
    on<LoadTournamentDetailsEvent>(_onLoadTournamentDetails);
    on<RegisterForTournamentEvent>(_onRegisterForTournament);
    on<LoadLeaderboardEvent>(_onLoadLeaderboard);
    on<LoadAchievementsEvent>(_onLoadAchievements);
    on<LoadReferralDataEvent>(_onLoadReferralData);
    on<LoadReferredUsersEvent>(_onLoadReferredUsers);
  }

  Future<void> _onLoadGames(
    LoadGamesEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getGames();

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (games) => emit(GamesLoaded(games: games)),
    );
  }

  Future<void> _onLoadGameDetails(
    LoadGameDetailsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getGameDetails(gameId: event.gameId);

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (game) => emit(GameDetailsLoaded(game: game)),
    );
  }

  Future<void> _onLoadActiveSessions(
    LoadActiveSessionsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getActiveSessions(gameId: event.gameId);

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (sessions) => emit(ActiveSessionsLoaded(sessions: sessions)),
    );
  }

  Future<void> _onCreateSession(
    CreateSessionEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.createSession(
      gameId: event.gameId,
      entryFee: event.entryFee,
      maxPlayers: event.maxPlayers,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (session) => emit(SessionCreated(session: session)),
    );
  }

  Future<void> _onJoinSession(
    JoinSessionEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.joinSession(sessionId: event.sessionId);

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (session) => emit(SessionJoined(session: session)),
    );
  }

  Future<void> _onLeaveSession(
    LeaveSessionEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.leaveSession(sessionId: event.sessionId);

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (_) => emit(const SessionLeft()),
    );
  }

  Future<void> _onLoadSessionDetails(
    LoadSessionDetailsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getSessionDetails(
      sessionId: event.sessionId,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (session) => emit(SessionDetailsLoaded(session: session)),
    );
  }

  Future<void> _onLoadSessionPlayers(
    LoadSessionPlayersEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getSessionPlayers(
      sessionId: event.sessionId,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (players) => emit(SessionPlayersLoaded(players: players)),
    );
  }

  Future<void> _onMarkReady(
    MarkReadyEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.markReady(sessionId: event.sessionId);

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (_) => emit(const PlayerMarkedReady()),
    );
  }

  Future<void> _onSubmitResult(
    SubmitResultEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.submitResult(
      sessionId: event.sessionId,
      gameData: event.gameData,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (result) => emit(ResultSubmitted(result: result)),
    );
  }

  Future<void> _onLoadGameResult(
    LoadGameResultEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getGameResult(
      sessionId: event.sessionId,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (result) => emit(GameResultLoaded(result: result)),
    );
  }

  Future<void> _onLoadGameHistory(
    LoadGameHistoryEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getGameHistory(
      gameId: event.gameId,
      limit: event.limit,
      offset: event.offset,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (history) => emit(GameHistoryLoaded(history: history)),
    );
  }

  Future<void> _onLoadTournaments(
    LoadTournamentsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getTournaments(
      gameId: event.gameId,
      status: event.status,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (tournaments) => emit(TournamentsLoaded(tournaments: tournaments)),
    );
  }

  Future<void> _onLoadTournamentDetails(
    LoadTournamentDetailsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getTournamentDetails(
      tournamentId: event.tournamentId,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (tournament) => emit(TournamentDetailsLoaded(tournament: tournament)),
    );
  }

  Future<void> _onRegisterForTournament(
    RegisterForTournamentEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.registerForTournament(
      tournamentId: event.tournamentId,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (_) => emit(const TournamentRegistered()),
    );
  }

  Future<void> _onLoadLeaderboard(
    LoadLeaderboardEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getLeaderboard(
      gameId: event.gameId,
      period: event.period,
      limit: event.limit,
    );

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (entries) => emit(LeaderboardLoaded(entries: entries)),
    );
  }

  Future<void> _onLoadAchievements(
    LoadAchievementsEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getAchievements();

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (achievements) => emit(AchievementsLoaded(achievements: achievements)),
    );
  }

  Future<void> _onLoadReferralData(
    LoadReferralDataEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getReferralData();

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (referral) => emit(ReferralDataLoaded(referral: referral)),
    );
  }

  Future<void> _onLoadReferredUsers(
    LoadReferredUsersEvent event,
    Emitter<GameState> emit,
  ) async {
    emit(const GameLoading());

    final result = await _gameRepository.getReferredUsers();

    result.fold(
      (failure) => emit(GameError(message: failure.message)),
      (users) => emit(ReferredUsersLoaded(users: users)),
    );
  }
}
