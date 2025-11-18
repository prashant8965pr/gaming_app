import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/tournament_repository.dart';
import 'tournament_event.dart';
import 'tournament_state.dart';

class TournamentBloc extends Bloc<TournamentEvent, TournamentState> {
  final TournamentRepository tournamentRepository;

  TournamentBloc({required this.tournamentRepository})
      : super(const TournamentState()) {
    on<LoadTournaments>(_onLoadTournaments);
    on<LoadTournamentDetails>(_onLoadTournamentDetails);
    on<RegisterForTournament>(_onRegisterForTournament);
    on<LoadTournamentBracket>(_onLoadTournamentBracket);
    on<LoadMyTournaments>(_onLoadMyTournaments);
    on<RefreshTournaments>(_onRefreshTournaments);
  }

  Future<void> _onLoadTournaments(
    LoadTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    if (event.page == 1) {
      emit(state.copyWith(status: TournamentStatus.loading));
    }

    try {
      final result = await tournamentRepository.getTournaments(
        status: event.status,
        page: event.page,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TournamentStatus.error,
            errorMessage: failure.message,
          ));
        },
        (newTournaments) {
          final updatedTournaments = event.page == 1
              ? newTournaments
              : [...state.tournaments, ...newTournaments];

          emit(state.copyWith(
            status: TournamentStatus.loaded,
            tournaments: updatedTournaments,
            hasMore: newTournaments.length >= 20,
            currentPage: event.page,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TournamentStatus.error,
        errorMessage: 'Failed to load tournaments: $e',
      ));
    }
  }

  Future<void> _onLoadTournamentDetails(
    LoadTournamentDetails event,
    Emitter<TournamentState> emit,
  ) async {
    emit(state.copyWith(status: TournamentStatus.loading));

    try {
      final result = await tournamentRepository.getTournamentDetails(
        tournamentId: event.tournamentId,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TournamentStatus.error,
            errorMessage: failure.message,
          ));
        },
        (tournament) {
          emit(state.copyWith(
            status: TournamentStatus.loaded,
            selectedTournament: tournament,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TournamentStatus.error,
        errorMessage: 'Failed to load tournament details: $e',
      ));
    }
  }

  Future<void> _onRegisterForTournament(
    RegisterForTournament event,
    Emitter<TournamentState> emit,
  ) async {
    emit(state.copyWith(status: TournamentStatus.registering));

    try {
      final result = await tournamentRepository.registerForTournament(
        tournamentId: event.tournamentId,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TournamentStatus.error,
            errorMessage: failure.message,
          ));
        },
        (registration) {
          emit(state.copyWith(status: TournamentStatus.loaded));
          // Reload tournament details
          add(LoadTournamentDetails(event.tournamentId));
          add(const LoadMyTournaments());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TournamentStatus.error,
        errorMessage: 'Failed to register for tournament: $e',
      ));
    }
  }

  Future<void> _onLoadTournamentBracket(
    LoadTournamentBracket event,
    Emitter<TournamentState> emit,
  ) async {
    emit(state.copyWith(status: TournamentStatus.loading));

    try {
      final result = await tournamentRepository.getTournamentBracket(
        tournamentId: event.tournamentId,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: TournamentStatus.error,
            errorMessage: failure.message,
          ));
        },
        (bracket) {
          emit(state.copyWith(
            status: TournamentStatus.loaded,
            bracket: bracket,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: TournamentStatus.error,
        errorMessage: 'Failed to load tournament bracket: $e',
      ));
    }
  }

  Future<void> _onLoadMyTournaments(
    LoadMyTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    try {
      final result = await tournamentRepository.getMyTournaments();

      result.fold(
        (failure) {
          // Silent fail
        },
        (myTournaments) {
          emit(state.copyWith(myTournaments: myTournaments));
        },
      );
    } catch (e) {
      // Silent fail
    }
  }

  Future<void> _onRefreshTournaments(
    RefreshTournaments event,
    Emitter<TournamentState> emit,
  ) async {
    add(const LoadTournaments(page: 1));
    add(const LoadMyTournaments());
  }
}
