import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/auth_repository.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc({required AuthRepository authRepository})
      : _authRepository = authRepository,
        super(const AuthInitial()) {
    on<SendOTPEvent>(_onSendOTP);
    on<VerifyOTPEvent>(_onVerifyOTP);
    on<SocialLoginEvent>(_onSocialLogin);
    on<CompleteProfileEvent>(_onCompleteProfile);
    on<LogoutEvent>(_onLogout);
    on<CheckAuthStatusEvent>(_onCheckAuthStatus);
    on<RefreshTokenEvent>(_onRefreshToken);
  }

  Future<void> _onSendOTP(
    SendOTPEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final result = await _authRepository.sendOTP(
      phoneNumber: event.phoneNumber,
    );

    result.fold(
      (failure) => emit(AuthError(message: failure.message)),
      (response) => emit(OTPSent(
        phoneNumber: event.phoneNumber,
        message: response.message,
      )),
    );
  }

  Future<void> _onVerifyOTP(
    VerifyOTPEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final result = await _authRepository.verifyOTP(
      phoneNumber: event.phoneNumber,
      otp: event.otp,
    );

    result.fold(
      (failure) => emit(AuthError(message: failure.message)),
      (response) {
        if (response.data != null) {
          // Check if user is new
          if (response.data!.isNewUser == true) {
            emit(const OTPVerifiedNewUser());
          } else {
            emit(Authenticated(user: response.data!.user));
          }
        } else {
          emit(const AuthError(message: 'Invalid response from server'));
        }
      },
    );
  }

  Future<void> _onSocialLogin(
    SocialLoginEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final result = await _authRepository.socialLogin(
      provider: event.provider,
      accessToken: event.accessToken,
      deviceId: event.deviceId,
      deviceName: event.deviceName,
    );

    result.fold(
      (failure) => emit(AuthError(message: failure.message)),
      (response) {
        if (response.data != null) {
          // Check if user is new
          if (response.data!.isNewUser == true) {
            emit(const OTPVerifiedNewUser());
          } else {
            emit(Authenticated(user: response.data!.user));
          }
        } else {
          emit(const AuthError(message: 'Invalid response from server'));
        }
      },
    );
  }

  Future<void> _onCompleteProfile(
    CompleteProfileEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final result = await _authRepository.completeProfile(
      username: event.username,
      displayName: event.displayName,
      dateOfBirth: event.dateOfBirth,
      gender: event.gender,
      referralCode: event.referralCode,
    );

    result.fold(
      (failure) => emit(AuthError(message: failure.message)),
      (response) {
        if (response.data != null) {
          emit(Authenticated(user: response.data!.user));
        } else {
          emit(const AuthError(message: 'Invalid response from server'));
        }
      },
    );
  }

  Future<void> _onLogout(
    LogoutEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final result = await _authRepository.logout();

    result.fold(
      (failure) {
        // Even if logout fails on server, clear local auth state
        emit(const Unauthenticated());
      },
      (_) => emit(const Unauthenticated()),
    );
  }

  Future<void> _onCheckAuthStatus(
    CheckAuthStatusEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    final isLoggedIn = await _authRepository.isLoggedIn();

    if (isLoggedIn) {
      final user = await _authRepository.getCurrentUser();
      if (user != null) {
        emit(Authenticated(user: user));
      } else {
        emit(const Unauthenticated());
      }
    } else {
      emit(const Unauthenticated());
    }
  }

  Future<void> _onRefreshToken(
    RefreshTokenEvent event,
    Emitter<AuthState> emit,
  ) async {
    // Note: This is typically called silently without emitting loading state
    // to avoid disrupting the user experience

    // Get refresh token from secure storage
    // This will be implemented through the repository
    final result = await _authRepository.refreshToken(
      refreshToken: '', // Will be retrieved from secure storage
    );

    result.fold(
      (failure) {
        // If refresh fails, logout user
        emit(const Unauthenticated());
      },
      (_) => emit(const TokenRefreshed()),
    );
  }
}
