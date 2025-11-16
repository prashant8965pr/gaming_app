import 'package:equatable/equatable.dart';

/// Base class for all user events
abstract class UserEvent extends Equatable {
  const UserEvent();

  @override
  List<Object?> get props => [];
}

/// Event to load user profile
class LoadUserProfileEvent extends UserEvent {
  const LoadUserProfileEvent();
}

/// Event to update user profile
class UpdateUserProfileEvent extends UserEvent {
  final String? displayName;
  final String? email;
  final String? avatarUrl;

  const UpdateUserProfileEvent({
    this.displayName,
    this.email,
    this.avatarUrl,
  });

  @override
  List<Object?> get props => [displayName, email, avatarUrl];
}

/// Event to load user statistics
class LoadUserStatisticsEvent extends UserEvent {
  const LoadUserStatisticsEvent();
}

/// Event to submit KYC document
class SubmitKYCDocumentEvent extends UserEvent {
  final String documentType;
  final String documentNumber;
  final String frontImage;
  final String? backImage;

  const SubmitKYCDocumentEvent({
    required this.documentType,
    required this.documentNumber,
    required this.frontImage,
    this.backImage,
  });

  @override
  List<Object?> get props => [documentType, documentNumber, frontImage, backImage];
}

/// Event to load KYC status
class LoadKYCStatusEvent extends UserEvent {
  const LoadKYCStatusEvent();
}

/// Event to load KYC documents
class LoadKYCDocumentsEvent extends UserEvent {
  const LoadKYCDocumentsEvent();
}

/// Event to update notification settings
class UpdateNotificationSettingsEvent extends UserEvent {
  final bool? pushEnabled;
  final bool? emailEnabled;
  final bool? smsEnabled;
  final bool? gameInvites;
  final bool? promotions;
  final bool? gameResults;
  final bool? walletUpdates;
  final bool? tournamentUpdates;

  const UpdateNotificationSettingsEvent({
    this.pushEnabled,
    this.emailEnabled,
    this.smsEnabled,
    this.gameInvites,
    this.promotions,
    this.gameResults,
    this.walletUpdates,
    this.tournamentUpdates,
  });

  @override
  List<Object?> get props => [
        pushEnabled,
        emailEnabled,
        smsEnabled,
        gameInvites,
        promotions,
        gameResults,
        walletUpdates,
        tournamentUpdates,
      ];
}

/// Event to load notification settings
class LoadNotificationSettingsEvent extends UserEvent {
  const LoadNotificationSettingsEvent();
}

/// Event to register FCM token
class RegisterFCMTokenEvent extends UserEvent {
  final String deviceId;
  final String fcmToken;
  final String deviceType;
  final String? deviceName;

  const RegisterFCMTokenEvent({
    required this.deviceId,
    required this.fcmToken,
    required this.deviceType,
    this.deviceName,
  });

  @override
  List<Object?> get props => [deviceId, fcmToken, deviceType, deviceName];
}
