import 'package:json_annotation/json_annotation.dart';

part 'notification_model.g.dart';

/// Notification model
@JsonSerializable()
class NotificationModel {
  final String id;
  final String title;
  final String message;
  final String type;
  final Map<String, dynamic>? data;
  @JsonKey(name: 'is_read')
  final bool isRead;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'read_at')
  final DateTime? readAt;

  NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    this.data,
    required this.isRead,
    required this.createdAt,
    this.readAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) =>
      _$NotificationModelFromJson(json);

  Map<String, dynamic> toJson() => _$NotificationModelToJson(this);

  NotificationModel copyWith({
    bool? isRead,
    DateTime? readAt,
  }) {
    return NotificationModel(
      id: id,
      title: title,
      message: message,
      type: type,
      data: data,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt,
      readAt: readAt ?? this.readAt,
    );
  }
}

/// Notification settings model
@JsonSerializable()
class NotificationSettingsModel {
  @JsonKey(name: 'push_enabled')
  final bool pushEnabled;
  @JsonKey(name: 'email_enabled')
  final bool emailEnabled;
  @JsonKey(name: 'sms_enabled')
  final bool smsEnabled;
  @JsonKey(name: 'game_invites')
  final bool gameInvites;
  @JsonKey(name: 'promotions')
  final bool promotions;
  @JsonKey(name: 'game_results')
  final bool gameResults;
  @JsonKey(name: 'wallet_updates')
  final bool walletUpdates;
  @JsonKey(name: 'tournament_updates')
  final bool tournamentUpdates;

  NotificationSettingsModel({
    required this.pushEnabled,
    required this.emailEnabled,
    required this.smsEnabled,
    required this.gameInvites,
    required this.promotions,
    required this.gameResults,
    required this.walletUpdates,
    required this.tournamentUpdates,
  });

  factory NotificationSettingsModel.fromJson(Map<String, dynamic> json) =>
      _$NotificationSettingsModelFromJson(json);

  Map<String, dynamic> toJson() => _$NotificationSettingsModelToJson(this);

  NotificationSettingsModel copyWith({
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    bool? gameInvites,
    bool? promotions,
    bool? gameResults,
    bool? walletUpdates,
    bool? tournamentUpdates,
  }) {
    return NotificationSettingsModel(
      pushEnabled: pushEnabled ?? this.pushEnabled,
      emailEnabled: emailEnabled ?? this.emailEnabled,
      smsEnabled: smsEnabled ?? this.smsEnabled,
      gameInvites: gameInvites ?? this.gameInvites,
      promotions: promotions ?? this.promotions,
      gameResults: gameResults ?? this.gameResults,
      walletUpdates: walletUpdates ?? this.walletUpdates,
      tournamentUpdates: tournamentUpdates ?? this.tournamentUpdates,
    );
  }
}

/// FCM token model
@JsonSerializable()
class FCMTokenModel {
  @JsonKey(name: 'device_id')
  final String deviceId;
  @JsonKey(name: 'fcm_token')
  final String fcmToken;
  @JsonKey(name: 'device_type')
  final String deviceType;
  @JsonKey(name: 'device_name')
  final String? deviceName;

  FCMTokenModel({
    required this.deviceId,
    required this.fcmToken,
    required this.deviceType,
    this.deviceName,
  });

  factory FCMTokenModel.fromJson(Map<String, dynamic> json) =>
      _$FCMTokenModelFromJson(json);

  Map<String, dynamic> toJson() => _$FCMTokenModelToJson(this);
}
