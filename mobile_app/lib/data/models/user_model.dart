import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

/// User data model
@JsonSerializable()
class UserModel {
  final String id;
  final String username;
  final String? email;
  final String phone;
  @JsonKey(name: 'display_name')
  final String? displayName;
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  @JsonKey(name: 'date_of_birth')
  final DateTime? dateOfBirth;
  final String role;
  final String status;
  @JsonKey(name: 'kyc_status')
  final String kycStatus;
  @JsonKey(name: 'is_email_verified')
  final bool isEmailVerified;
  @JsonKey(name: 'is_phone_verified')
  final bool isPhoneVerified;
  @JsonKey(name: 'referral_code')
  final String referralCode;
  @JsonKey(name: 'referred_by')
  final String? referredBy;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  @JsonKey(name: 'last_login_at')
  final DateTime? lastLoginAt;

  UserModel({
    required this.id,
    required this.username,
    this.email,
    required this.phone,
    this.displayName,
    this.avatarUrl,
    this.dateOfBirth,
    required this.role,
    required this.status,
    required this.kycStatus,
    required this.isEmailVerified,
    required this.isPhoneVerified,
    required this.referralCode,
    this.referredBy,
    required this.createdAt,
    required this.updatedAt,
    this.lastLoginAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  UserModel copyWith({
    String? id,
    String? username,
    String? email,
    String? phone,
    String? displayName,
    String? avatarUrl,
    DateTime? dateOfBirth,
    String? role,
    String? status,
    String? kycStatus,
    bool? isEmailVerified,
    bool? isPhoneVerified,
    String? referralCode,
    String? referredBy,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLoginAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      displayName: displayName ?? this.displayName,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      role: role ?? this.role,
      status: status ?? this.status,
      kycStatus: kycStatus ?? this.kycStatus,
      isEmailVerified: isEmailVerified ?? this.isEmailVerified,
      isPhoneVerified: isPhoneVerified ?? this.isPhoneVerified,
      referralCode: referralCode ?? this.referralCode,
      referredBy: referredBy ?? this.referredBy,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
    );
  }
}

/// User statistics model
@JsonSerializable()
class UserStatisticsModel {
  @JsonKey(name: 'total_games_played')
  final int totalGamesPlayed;
  @JsonKey(name: 'total_games_won')
  final int totalGamesWon;
  @JsonKey(name: 'total_games_lost')
  final int totalGamesLost;
  @JsonKey(name: 'total_winnings')
  final double totalWinnings;
  @JsonKey(name: 'total_spent')
  final double totalSpent;
  @JsonKey(name: 'current_level')
  final int currentLevel;
  @JsonKey(name: 'experience_points')
  final int experiencePoints;
  @JsonKey(name: 'current_streak')
  final int currentStreak;
  @JsonKey(name: 'longest_streak')
  final int longestStreak;

  UserStatisticsModel({
    required this.totalGamesPlayed,
    required this.totalGamesWon,
    required this.totalGamesLost,
    required this.totalWinnings,
    required this.totalSpent,
    required this.currentLevel,
    required this.experiencePoints,
    required this.currentStreak,
    required this.longestStreak,
  });

  factory UserStatisticsModel.fromJson(Map<String, dynamic> json) =>
      _$UserStatisticsModelFromJson(json);

  Map<String, dynamic> toJson() => _$UserStatisticsModelToJson(this);

  double get winRate {
    if (totalGamesPlayed == 0) return 0.0;
    return (totalGamesWon / totalGamesPlayed) * 100;
  }

  double get roi {
    if (totalSpent == 0) return 0.0;
    return ((totalWinnings - totalSpent) / totalSpent) * 100;
  }
}
