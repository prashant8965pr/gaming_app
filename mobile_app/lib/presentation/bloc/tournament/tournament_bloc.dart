import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/tournament_repository.dart';
import 'tournament_event.dart';
import 'tournament_state.dart';

class TournamentBloc extends Bloc<TournamentEvent, TournamentState> {
  final TournamentRepository repository;

  TournamentBloc({required this.repository}) : super(TournamentInitial()) {
    on<LoadTournaments>(_onLoadTournaments);
    on<LoadTournamentDetails>(_onLoadTournamentDetails);
    on<RegisterForTournament>(_onRegisterForTournament);
    on<LoadTournamentBracket>(_onLoadTournamentBracket);
    on<LoadMyTournaments>(_onLoadMyTournaments);
    on<FilterTournaments>(_onFilterTournaments);
  }

  Future<void> _onLoadTournaments(
    LoadTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    if (event.refresh) {
      emit(TournamentLoading());
    }

    final result = await repository.getTournaments(
      status: event.status,
      gameId: event.gameId,
      isFeatured: event.isFeatured,
    );

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (tournaments) => emit(TournamentLoaded(
        tournaments: tournaments,
        hasMore: tournaments.length >= 20,
      )),
    );
  }

  Future<void> _onLoadTournamentDetails(
    LoadTournamentDetails event,
    Emitter<TournamentState> emit,
  ) async {
    emit(TournamentDetailsLoading());

    final result = await repository.getTournamentById(event.tournamentId);

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (tournament) => emit(TournamentDetailsLoaded(tournament)),
    );
  }

  Future<void> _onRegisterForTournament(
    RegisterForTournament event,
    Emitter<TournamentState> emit,
  ) async {
    emit(TournamentRegistering());

    final result = await repository.registerForTournament(event.tournamentId);

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (registration) => emit(TournamentRegistered(registration)),
    );
  }

  Future<void> _onLoadTournamentBracket(
    LoadTournamentBracket event,
    Emitter<TournamentState> emit,
  ) async {
    emit(TournamentBracketLoading());

    final result = await repository.getTournamentBracket(event.tournamentId);

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (bracket) => emit(TournamentBracketLoaded(bracket)),
    );
  }

  Future<void> _onLoadMyTournaments(
    LoadMyTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    emit(MyTournamentsLoading());

    final result = await repository.getMyTournaments();

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (registrations) => emit(MyTournamentsLoaded(registrations)),
    );
  }

  Future<void> _onFilterTournaments(
    FilterTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    emit(TournamentLoading());

    final result = await repository.getTournaments(
      status: event.status,
      gameId: event.gameId,
    );

    result.fold(
      (failure) => emit(TournamentError(failure.message)),
      (tournaments) => emit(TournamentLoaded(
        tournaments: tournaments,
        hasMore: tournaments.length >= 20,
      )),
    );
  }
}
