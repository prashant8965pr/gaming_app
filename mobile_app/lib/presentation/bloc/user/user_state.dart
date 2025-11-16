import 'package:equatable/equatable.dart';
import '../../../data/models/user_model.dart';
import '../../../data/models/kyc_model.dart';
import '../../../data/models/notification_model.dart';

/// Base class for all user states
abstract class UserState extends Equatable {
  const UserState();

  @override
  List<Object?> get props => [];
}

/// Initial state
class UserInitial extends UserState {
  const UserInitial();
}

/// Loading state
class UserLoading extends UserState {
  const UserLoading();
}

/// User profile loaded
class UserProfileLoaded extends UserState {
  final UserModel user;

  const UserProfileLoaded({required this.user});

  @override
  List<Object?> get props => [user];
}

/// User profile updated
class UserProfileUpdated extends UserState {
  final UserModel user;

  const UserProfileUpdated({required this.user});

  @override
  List<Object?> get props => [user];
}

/// User statistics loaded
class UserStatisticsLoaded extends UserState {
  final UserStatisticsModel statistics;

  const UserStatisticsLoaded({required this.statistics});

  @override
  List<Object?> get props => [statistics];
}

/// KYC document submitted
class KYCDocumentSubmitted extends UserState {
  final KYCDocumentModel document;

  const KYCDocumentSubmitted({required this.document});

  @override
  List<Object?> get props => [document];
}

/// KYC status loaded
class KYCStatusLoaded extends UserState {
  final KYCStatusModel status;

  const KYCStatusLoaded({required this.status});

  @override
  List<Object?> get props => [status];
}

/// KYC documents loaded
class KYCDocumentsLoaded extends UserState {
  final List<KYCDocumentModel> documents;

  const KYCDocumentsLoaded({required this.documents});

  @override
  List<Object?> get props => [documents];
}

/// Notification settings loaded
class NotificationSettingsLoaded extends UserState {
  final NotificationSettingsModel settings;

  const NotificationSettingsLoaded({required this.settings});

  @override
  List<Object?> get props => [settings];
}

/// Notification settings updated
class NotificationSettingsUpdated extends UserState {
  final NotificationSettingsModel settings;

  const NotificationSettingsUpdated({required this.settings});

  @override
  List<Object?> get props => [settings];
}

/// FCM token registered
class FCMTokenRegistered extends UserState {
  const FCMTokenRegistered();
}

/// Error state
class UserError extends UserState {
  final String message;

  const UserError({required this.message});

  @override
  List<Object?> get props => [message];
}
