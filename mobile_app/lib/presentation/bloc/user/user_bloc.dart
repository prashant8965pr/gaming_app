import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/user_repository.dart';
import 'user_event.dart';
import 'user_state.dart';

class UserBloc extends Bloc<UserEvent, UserState> {
  final UserRepository _userRepository;

  UserBloc({required UserRepository userRepository})
      : _userRepository = userRepository,
        super(const UserInitial()) {
    on<LoadUserProfileEvent>(_onLoadUserProfile);
    on<UpdateUserProfileEvent>(_onUpdateUserProfile);
    on<LoadUserStatisticsEvent>(_onLoadUserStatistics);
    on<SubmitKYCDocumentEvent>(_onSubmitKYCDocument);
    on<LoadKYCStatusEvent>(_onLoadKYCStatus);
    on<LoadKYCDocumentsEvent>(_onLoadKYCDocuments);
    on<UpdateNotificationSettingsEvent>(_onUpdateNotificationSettings);
    on<LoadNotificationSettingsEvent>(_onLoadNotificationSettings);
    on<RegisterFCMTokenEvent>(_onRegisterFCMToken);
  }

  Future<void> _onLoadUserProfile(
    LoadUserProfileEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.getProfile();

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (user) => emit(UserProfileLoaded(user: user)),
    );
  }

  Future<void> _onUpdateUserProfile(
    UpdateUserProfileEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.updateProfile(
      displayName: event.displayName,
      email: event.email,
      avatarUrl: event.avatarUrl,
    );

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (user) => emit(UserProfileUpdated(user: user)),
    );
  }

  Future<void> _onLoadUserStatistics(
    LoadUserStatisticsEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.getStatistics();

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (statistics) => emit(UserStatisticsLoaded(statistics: statistics)),
    );
  }

  Future<void> _onSubmitKYCDocument(
    SubmitKYCDocumentEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.submitKYCDocument(
      documentType: event.documentType,
      documentNumber: event.documentNumber,
      frontImage: event.frontImage,
      backImage: event.backImage,
    );

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (document) => emit(KYCDocumentSubmitted(document: document)),
    );
  }

  Future<void> _onLoadKYCStatus(
    LoadKYCStatusEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.getKYCStatus();

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (status) => emit(KYCStatusLoaded(status: status)),
    );
  }

  Future<void> _onLoadKYCDocuments(
    LoadKYCDocumentsEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.getKYCDocuments();

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (documents) => emit(KYCDocumentsLoaded(documents: documents)),
    );
  }

  Future<void> _onUpdateNotificationSettings(
    UpdateNotificationSettingsEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.updateNotificationSettings(
      pushEnabled: event.pushEnabled,
      emailEnabled: event.emailEnabled,
      smsEnabled: event.smsEnabled,
      gameInvites: event.gameInvites,
      promotions: event.promotions,
      gameResults: event.gameResults,
      walletUpdates: event.walletUpdates,
      tournamentUpdates: event.tournamentUpdates,
    );

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (settings) => emit(NotificationSettingsUpdated(settings: settings)),
    );
  }

  Future<void> _onLoadNotificationSettings(
    LoadNotificationSettingsEvent event,
    Emitter<UserState> emit,
  ) async {
    emit(const UserLoading());

    final result = await _userRepository.getNotificationSettings();

    result.fold(
      (failure) => emit(UserError(message: failure.message)),
      (settings) => emit(NotificationSettingsLoaded(settings: settings)),
    );
  }

  Future<void> _onRegisterFCMToken(
    RegisterFCMTokenEvent event,
    Emitter<UserState> emit,
  ) async {
    // Don't emit loading for token registration
    final result = await _userRepository.registerFCMToken(
      deviceId: event.deviceId,
      fcmToken: event.fcmToken,
      deviceType: event.deviceType,
      deviceName: event.deviceName,
    );

    result.fold(
      (failure) {
        // Silently fail - token registration is not critical
      },
      (_) => emit(const FCMTokenRegistered()),
    );
  }
}
