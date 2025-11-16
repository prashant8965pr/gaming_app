import 'package:json_annotation/json_annotation.dart';

part 'game_model.g.dart';

/// Game catalog model
@JsonSerializable()
class GameModel {
  final String id;
  final String name;
  final String description;
  @JsonKey(name: 'game_type')
  final String gameType;
  @JsonKey(name: 'thumbnail_url')
  final String? thumbnailUrl;
  @JsonKey(name: 'min_players')
  final int minPlayers;
  @JsonKey(name: 'max_players')
  final int maxPlayers;
  @JsonKey(name: 'min_entry_fee')
  final double minEntryFee;
  @JsonKey(name: 'max_entry_fee')
  final double maxEntryFee;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'active_players')
  final int? activePlayers;
  final String? rules;

  GameModel({
    required this.id,
    required this.name,
    required this.description,
    required this.gameType,
    this.thumbnailUrl,
    required this.minPlayers,
    required this.maxPlayers,
    required this.minEntryFee,
    required this.maxEntryFee,
    required this.isActive,
    this.activePlayers,
    this.rules,
  });

  factory GameModel.fromJson(Map<String, dynamic> json) =>
      _$GameModelFromJson(json);

  Map<String, dynamic> toJson() => _$GameModelToJson(this);
}

/// Game session model
@JsonSerializable()
class GameSessionModel {
  final String id;
  @JsonKey(name: 'game_id')
  final String gameId;
  @JsonKey(name: 'entry_fee')
  final double entryFee;
  @JsonKey(name: 'prize_pool')
  final double prizePool;
  @JsonKey(name: 'max_players')
  final int maxPlayers;
  @JsonKey(name: 'current_players')
  final int currentPlayers;
  final String status;
  @JsonKey(name: 'start_time')
  final DateTime? startTime;
  @JsonKey(name: 'end_time')
  final DateTime? endTime;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  GameSessionModel({
    required this.id,
    required this.gameId,
    required this.entryFee,
    required this.prizePool,
    required this.maxPlayers,
    required this.currentPlayers,
    required this.status,
    this.startTime,
    this.endTime,
    required this.createdAt,
  });

  factory GameSessionModel.fromJson(Map<String, dynamic> json) =>
      _$GameSessionModelFromJson(json);

  Map<String, dynamic> toJson() => _$GameSessionModelToJson(this);

  bool get isFull => currentPlayers >= maxPlayers;
  bool get canJoin => !isFull && status == 'waiting';
}

/// Game player model
@JsonSerializable()
class GamePlayerModel {
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  final int position;
  final String status;
  @JsonKey(name: 'is_ready')
  final bool isReady;

  GamePlayerModel({
    required this.userId,
    required this.username,
    this.avatarUrl,
    required this.position,
    required this.status,
    required this.isReady,
  });

  factory GamePlayerModel.fromJson(Map<String, dynamic> json) =>
      _$GamePlayerModelFromJson(json);

  Map<String, dynamic> toJson() => _$GamePlayerModelToJson(this);
}

/// Game result model
@JsonSerializable()
class GameResultModel {
  @JsonKey(name: 'session_id')
  final String sessionId;
  final List<PlayerResultModel> players;
  @JsonKey(name: 'winner_id')
  final String winnerId;
  @JsonKey(name: 'winner_prize')
  final double winnerPrize;
  @JsonKey(name: 'completed_at')
  final DateTime completedAt;

  GameResultModel({
    required this.sessionId,
    required this.players,
    required this.winnerId,
    required this.winnerPrize,
    required this.completedAt,
  });

  factory GameResultModel.fromJson(Map<String, dynamic> json) =>
      _$GameResultModelFromJson(json);

  Map<String, dynamic> toJson() => _$GameResultModelToJson(this);
}

@JsonSerializable()
class PlayerResultModel {
  @JsonKey(name: 'user_id')
  final String userId;
  final String username;
  final int rank;
  final int score;
  final double prize;

  PlayerResultModel({
    required this.userId,
    required this.username,
    required this.rank,
    required this.score,
    required this.prize,
  });

  factory PlayerResultModel.fromJson(Map<String, dynamic> json) =>
      _$PlayerResultModelFromJson(json);

  Map<String, dynamic> toJson() => _$PlayerResultModelToJson(this);
}

/// Tournament model
@JsonSerializable()
class TournamentModel {
  final String id;
  final String name;
  final String description;
  @JsonKey(name: 'game_id')
  final String gameId;
  @JsonKey(name: 'entry_fee')
  final double entryFee;
  @JsonKey(name: 'prize_pool')
  final double prizePool;
  @JsonKey(name: 'max_participants')
  final int maxParticipants;
  @JsonKey(name: 'current_participants')
  final int currentParticipants;
  @JsonKey(name: 'start_time')
  final DateTime startTime;
  @JsonKey(name: 'end_time')
  final DateTime? endTime;
  final String status;
  @JsonKey(name: 'tournament_type')
  final String tournamentType;

  TournamentModel({
    required this.id,
    required this.name,
    required this.description,
    required this.gameId,
    required this.entryFee,
    required this.prizePool,
    required this.maxParticipants,
    required this.currentParticipants,
    required this.startTime,
    this.endTime,
    required this.status,
    required this.tournamentType,
  });

  factory TournamentModel.fromJson(Map<String, dynamic> json) =>
      _$TournamentModelFromJson(json);

  Map<String, dynamic> toJson() => _$TournamentModelToJson(this);

  bool get isFull => currentParticipants >= maxParticipants;
  bool get canRegister => !isFull && status == 'upcoming';
}
