import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../data/models/rewards_model.dart';
import '../../../data/repositories/rewards_repository.dart';

// Events
abstract class RewardsEvent extends Equatable {
  const RewardsEvent();
  @override
  List<Object?> get props => [];
}

class LoadAchievements extends RewardsEvent {}
class ClaimAchievement extends RewardsEvent {
  final int achievementId;
  const ClaimAchievement(this.achievementId);
  @override
  List<Object?> get props => [achievementId];
}

class LoadLeaderboard extends RewardsEvent {
  final String period;
  const LoadLeaderboard({this.period = 'all_time'});
  @override
  List<Object?> get props => [period];
}

class LoadReferrals extends RewardsEvent {}
class LoadReferralStats extends RewardsEvent {}

// State
enum RewardsStatus { initial, loading, loaded, claiming, error }

class RewardsState extends Equatable {
  final RewardsStatus status;
  final List<AchievementModel> achievements;
  final List<LeaderboardEntryModel> leaderboard;
  final LeaderboardEntryModel? myRank;
  final List<ReferralModel> referrals;
  final ReferralStatsModel? referralStats;
  final String? errorMessage;

  const RewardsState({
    this.status = RewardsStatus.initial,
    this.achievements = const [],
    this.leaderboard = const [],
    this.myRank,
    this.referrals = const [],
    this.referralStats,
    this.errorMessage,
  });

  RewardsState copyWith({
    RewardsStatus? status,
    List<AchievementModel>? achievements,
    List<LeaderboardEntryModel>? leaderboard,
    LeaderboardEntryModel? myRank,
    List<ReferralModel>? referrals,
    ReferralStatsModel? referralStats,
    String? errorMessage,
  }) {
    return RewardsState(
      status: status ?? this.status,
      achievements: achievements ?? this.achievements,
      leaderboard: leaderboard ?? this.leaderboard,
      myRank: myRank ?? this.myRank,
      referrals: referrals ?? this.referrals,
      referralStats: referralStats ?? this.referralStats,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [
        status,
        achievements,
        leaderboard,
        myRank,
        referrals,
        referralStats,
        errorMessage,
      ];
}

// BLoC
class RewardsBloc extends Bloc<RewardsEvent, RewardsState> {
  final RewardsRepository rewardsRepository;

  RewardsBloc({required this.rewardsRepository}) : super(const RewardsState()) {
    on<LoadAchievements>(_onLoadAchievements);
    on<ClaimAchievement>(_onClaimAchievement);
    on<LoadLeaderboard>(_onLoadLeaderboard);
    on<LoadReferrals>(_onLoadReferrals);
    on<LoadReferralStats>(_onLoadReferralStats);
  }

  Future<void> _onLoadAchievements(LoadAchievements event, Emitter<RewardsState> emit) async {
    emit(state.copyWith(status: RewardsStatus.loading));
    final result = await rewardsRepository.getAchievements();
    result.fold(
      (failure) => emit(state.copyWith(status: RewardsStatus.error, errorMessage: failure.message)),
      (achievements) => emit(state.copyWith(status: RewardsStatus.loaded, achievements: achievements)),
    );
  }

  Future<void> _onClaimAchievement(ClaimAchievement event, Emitter<RewardsState> emit) async {
    emit(state.copyWith(status: RewardsStatus.claiming));
    final result = await rewardsRepository.claimAchievement(achievementId: event.achievementId);
    result.fold(
      (failure) => emit(state.copyWith(status: RewardsStatus.error, errorMessage: failure.message)),
      (_) {
        emit(state.copyWith(status: RewardsStatus.loaded));
        add(LoadAchievements());
      },
    );
  }

  Future<void> _onLoadLeaderboard(LoadLeaderboard event, Emitter<RewardsState> emit) async {
    emit(state.copyWith(status: RewardsStatus.loading));
    final result = await rewardsRepository.getLeaderboard(period: event.period);
    result.fold(
      (failure) => emit(state.copyWith(status: RewardsStatus.error, errorMessage: failure.message)),
      (leaderboardData) => emit(state.copyWith(
        status: RewardsStatus.loaded,
        leaderboard: leaderboardData.entries,
        myRank: leaderboardData.myRank,
      )),
    );
  }

  Future<void> _onLoadReferrals(LoadReferrals event, Emitter<RewardsState> emit) async {
    final result = await rewardsRepository.getReferrals();
    result.fold(
      (failure) => {},
      (referrals) => emit(state.copyWith(referrals: referrals)),
    );
  }

  Future<void> _onLoadReferralStats(LoadReferralStats event, Emitter<RewardsState> emit) async {
    final result = await rewardsRepository.getReferralStats();
    result.fold(
      (failure) => {},
      (stats) => emit(state.copyWith(referralStats: stats)),
    );
  }
}
