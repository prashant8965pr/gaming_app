import 'package:equatable/equatable.dart';
import '../../../data/models/tournament_model.dart';

enum TournamentStatus { initial, loading, loaded, registering, error }

class TournamentState extends Equatable {
  final TournamentStatus status;
  final List<TournamentModel> tournaments;
  final List<TournamentModel> myTournaments;
  final TournamentModel? selectedTournament;
  final TournamentBracketModel? bracket;
  final String? errorMessage;
  final bool hasMore;
  final int currentPage;

  const TournamentState({
    this.status = TournamentStatus.initial,
    this.tournaments = const [],
    this.myTournaments = const [],
    this.selectedTournament,
    this.bracket,
    this.errorMessage,
    this.hasMore = true,
    this.currentPage = 1,
  });

  TournamentState copyWith({
    TournamentStatus? status,
    List<TournamentModel>? tournaments,
    List<TournamentModel>? myTournaments,
    TournamentModel? selectedTournament,
    TournamentBracketModel? bracket,
    String? errorMessage,
    bool? hasMore,
    int? currentPage,
  }) {
    return TournamentState(
      status: status ?? this.status,
      tournaments: tournaments ?? this.tournaments,
      myTournaments: myTournaments ?? this.myTournaments,
      selectedTournament: selectedTournament ?? this.selectedTournament,
      bracket: bracket ?? this.bracket,
      errorMessage: errorMessage,
      hasMore: hasMore ?? this.hasMore,
      currentPage: currentPage ?? this.currentPage,
    );
  }

  @override
  List<Object?> get props => [
        status,
        tournaments,
        myTournaments,
        selectedTournament,
        bracket,
        errorMessage,
        hasMore,
        currentPage,
      ];
}
