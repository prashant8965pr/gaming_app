import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../data/models/game_model.dart';
import '../../../data/repositories/game_repository.dart';

// Events
abstract class GameEvent extends Equatable {
  const GameEvent();
  @override
  List<Object?> get props => [];
}

class LoadGameCatalog extends GameEvent {}
class LoadGameDetails extends GameEvent {
  final int gameId;
  const LoadGameDetails(this.gameId);
  @override
  List<Object?> get props => [gameId];
}

class CreateGameSession extends GameEvent {
  final int gameId;
  final double entryFee;
  final int maxPlayers;
  const CreateGameSession(this.gameId, this.entryFee, this.maxPlayers);
  @override
  List<Object?> get props => [gameId, entryFee, maxPlayers];
}

class JoinGameSession extends GameEvent {
  final int sessionId;
  const JoinGameSession(this.sessionId);
  @override
  List<Object?> get props => [sessionId];
}

class LoadActiveSessions extends GameEvent {}
class LoadMyGameHistory extends GameEvent {
  final int page;
  const LoadMyGameHistory({this.page = 1});
  @override
  List<Object?> get props => [page];
}

// State
enum GameStatus { initial, loading, loaded, creating, joining, error }

class GameState extends Equatable {
  final GameStatus status;
  final List<GameModel> games;
  final GameModel? selectedGame;
  final List<GameSessionModel> activeSessions;
  final List<GameSessionModel> myHistory;
  final String? errorMessage;

  const GameState({
    this.status = GameStatus.initial,
    this.games = const [],
    this.selectedGame,
    this.activeSessions = const [],
    this.myHistory = const [],
    this.errorMessage,
  });

  GameState copyWith({
    GameStatus? status,
    List<GameModel>? games,
    GameModel? selectedGame,
    List<GameSessionModel>? activeSessions,
    List<GameSessionModel>? myHistory,
    String? errorMessage,
  }) {
    return GameState(
      status: status ?? this.status,
      games: games ?? this.games,
      selectedGame: selectedGame ?? this.selectedGame,
      activeSessions: activeSessions ?? this.activeSessions,
      myHistory: myHistory ?? this.myHistory,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, games, selectedGame, activeSessions, myHistory, errorMessage];
}

// BLoC
class GameBloc extends Bloc<GameEvent, GameState> {
  final GameRepository gameRepository;

  GameBloc({required this.gameRepository}) : super(const GameState()) {
    on<LoadGameCatalog>(_onLoadGameCatalog);
    on<LoadGameDetails>(_onLoadGameDetails);
    on<CreateGameSession>(_onCreateGameSession);
    on<JoinGameSession>(_onJoinGameSession);
    on<LoadActiveSessions>(_onLoadActiveSessions);
    on<LoadMyGameHistory>(_onLoadMyGameHistory);
  }

  Future<void> _onLoadGameCatalog(LoadGameCatalog event, Emitter<GameState> emit) async {
    emit(state.copyWith(status: GameStatus.loading));
    final result = await gameRepository.getGameCatalog();
    result.fold(
      (failure) => emit(state.copyWith(status: GameStatus.error, errorMessage: failure.message)),
      (games) => emit(state.copyWith(status: GameStatus.loaded, games: games)),
    );
  }

  Future<void> _onLoadGameDetails(LoadGameDetails event, Emitter<GameState> emit) async {
    emit(state.copyWith(status: GameStatus.loading));
    final result = await gameRepository.getGameDetails(gameId: event.gameId);
    result.fold(
      (failure) => emit(state.copyWith(status: GameStatus.error, errorMessage: failure.message)),
      (game) => emit(state.copyWith(status: GameStatus.loaded, selectedGame: game)),
    );
  }

  Future<void> _onCreateGameSession(CreateGameSession event, Emitter<GameState> emit) async {
    emit(state.copyWith(status: GameStatus.creating));
    final result = await gameRepository.createGameSession(
      gameId: event.gameId,
      entryFee: event.entryFee,
      maxPlayers: event.maxPlayers,
    );
    result.fold(
      (failure) => emit(state.copyWith(status: GameStatus.error, errorMessage: failure.message)),
      (session) {
        emit(state.copyWith(status: GameStatus.loaded));
        add(LoadActiveSessions());
      },
    );
  }

  Future<void> _onJoinGameSession(JoinGameSession event, Emitter<GameState> emit) async {
    emit(state.copyWith(status: GameStatus.joining));
    final result = await gameRepository.joinGameSession(sessionId: event.sessionId);
    result.fold(
      (failure) => emit(state.copyWith(status: GameStatus.error, errorMessage: failure.message)),
      (_) {
        emit(state.copyWith(status: GameStatus.loaded));
        add(LoadActiveSessions());
      },
    );
  }

  Future<void> _onLoadActiveSessions(LoadActiveSessions event, Emitter<GameState> emit) async {
    final result = await gameRepository.getActiveSessions();
    result.fold(
      (failure) => {},
      (sessions) => emit(state.copyWith(activeSessions: sessions)),
    );
  }

  Future<void> _onLoadMyGameHistory(LoadMyGameHistory event, Emitter<GameState> emit) async {
    if (event.page == 1) emit(state.copyWith(status: GameStatus.loading));
    final result = await gameRepository.getMyGameHistory(page: event.page);
    result.fold(
      (failure) => emit(state.copyWith(status: GameStatus.error, errorMessage: failure.message)),
      (history) {
        final updatedHistory = event.page == 1 ? history : [...state.myHistory, ...history];
        emit(state.copyWith(status: GameStatus.loaded, myHistory: updatedHistory));
      },
    );
  }
}
