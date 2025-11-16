import 'package:json_annotation/json_annotation.dart';

part 'rewards_model.g.dart';

/// Achievement model
@JsonSerializable()
class AchievementModel {
  final String id;
  final String name;
  final String description;
  @JsonKey(name: 'icon_url')
  final String? iconUrl;
  final int points;
  final String category;
  @JsonKey(name: 'requirement_type')
  final String requirementType;
  @JsonKey(name: 'requirement_value')
  final int requirementValue;
  @JsonKey(name: 'current_progress')
  final int? currentProgress;
  @JsonKey(name: 'is_unlocked')
  final bool isUnlocked;
  @JsonKey(name: 'unlocked_at')
  final DateTime? unlockedAt;

  AchievementModel({
    required this.id,
    required this.name,
    required this.description,
    this.iconUrl,
    required this.points,
    required this.category,
    required this.requirementType,
    required this.requirementValue,
    this.currentProgress,
    required this.isUnlocked,
    this.unlockedAt,
  });

  factory AchievementModel.fromJson(Map<String, dynamic> json) =>
      _$AchievementModelFromJson(json);

  Map<String, dynamic> toJson() => _$AchievementModelToJson(this);

  double get progressPercentage {
    if (isUnlocked) return 100.0;
    if (currentProgress == null) return 0.0;
    return (currentProgress! / requirementValue * 100).clamp(0.0, 100.0);
  }
}

/// Leaderboard entry model
@JsonSerializable()
class LeaderboardEntryModel {
  final int rank;
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  final int score;
  final double winnings;
  @JsonKey(name: 'games_played')
  final int gamesPlayed;
  @JsonKey(name: 'games_won')
  final int gamesWon;
  @JsonKey(name: 'is_current_user')
  final bool? isCurrentUser;

  LeaderboardEntryModel({
    required this.rank,
    required this.userId,
    required this.username,
    this.avatarUrl,
    required this.score,
    required this.winnings,
    required this.gamesPlayed,
    required this.gamesWon,
    this.isCurrentUser,
  });

  factory LeaderboardEntryModel.fromJson(Map<String, dynamic> json) =>
      _$LeaderboardEntryModelFromJson(json);

  Map<String, dynamic> toJson() => _$LeaderboardEntryModelToJson(this);

  double get winRate {
    if (gamesPlayed == 0) return 0.0;
    return (gamesWon / gamesPlayed * 100);
  }
}

/// Referral model
@JsonSerializable()
class ReferralModel {
  @JsonKey(name: 'referral_code')
  final String referralCode;
  @JsonKey(name: 'total_referrals')
  final int totalReferrals;
  @JsonKey(name: 'active_referrals')
  final int activeReferrals;
  @JsonKey(name: 'total_earnings')
  final double totalEarnings;
  @JsonKey(name: 'pending_earnings')
  final double pendingEarnings;
  @JsonKey(name: 'referral_bonus')
  final double referralBonus;

  ReferralModel({
    required this.referralCode,
    required this.totalReferrals,
    required this.activeReferrals,
    required this.totalEarnings,
    required this.pendingEarnings,
    required this.referralBonus,
  });

  factory ReferralModel.fromJson(Map<String, dynamic> json) =>
      _$ReferralModelFromJson(json);

  Map<String, dynamic> toJson() => _$ReferralModelToJson(this);
}

/// Referred user model
@JsonSerializable()
class ReferredUserModel {
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  @JsonKey(name: 'joined_at')
  final DateTime joinedAt;
  final String status;
  @JsonKey(name: 'earnings_from_user')
  final double earningsFromUser;

  ReferredUserModel({
    required this.userId,
    required this.username,
    this.avatarUrl,
    required this.joinedAt,
    required this.status,
    required this.earningsFromUser,
  });

  factory ReferredUserModel.fromJson(Map<String, dynamic> json) =>
      _$ReferredUserModelFromJson(json);

  Map<String, dynamic> toJson() => _$ReferredUserModelToJson(this);

  bool get isActive => status == 'active';
}

/// Daily reward model
@JsonSerializable()
class DailyRewardModel {
  final int day;
  @JsonKey(name: 'reward_type')
  final String rewardType;
  @JsonKey(name: 'reward_value')
  final double rewardValue;
  @JsonKey(name: 'is_claimed')
  final bool isClaimed;
  @JsonKey(name: 'claimed_at')
  final DateTime? claimedAt;

  DailyRewardModel({
    required this.day,
    required this.rewardType,
    required this.rewardValue,
    required this.isClaimed,
    this.claimedAt,
  });

  factory DailyRewardModel.fromJson(Map<String, dynamic> json) =>
      _$DailyRewardModelFromJson(json);

  Map<String, dynamic> toJson() => _$DailyRewardModelToJson(this);

  bool get canClaim => !isClaimed;
}

/// Spin wheel reward model
@JsonSerializable()
class SpinWheelRewardModel {
  @JsonKey(name: 'reward_type')
  final String rewardType;
  @JsonKey(name: 'reward_value')
  final double rewardValue;
  final String message;
  @JsonKey(name: 'spins_remaining')
  final int spinsRemaining;

  SpinWheelRewardModel({
    required this.rewardType,
    required this.rewardValue,
    required this.message,
    required this.spinsRemaining,
  });

  factory SpinWheelRewardModel.fromJson(Map<String, dynamic> json) =>
      _$SpinWheelRewardModelFromJson(json);

  Map<String, dynamic> toJson() => _$SpinWheelRewardModelToJson(this);
}
