import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/auth_repository.dart';
import '../../../core/storage/secure_storage.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository authRepository;
  final SecureStorage secureStorage;

  AuthBloc({
    required this.authRepository,
    required this.secureStorage,
  }) : super(const AuthState()) {
    on<LoginRequested>(_onLoginRequested);
    on<RegisterRequested>(_onRegisterRequested);
    on<LogoutRequested>(_onLogoutRequested);
    on<CheckAuthStatus>(_onCheckAuthStatus);
    on<UpdateProfile>(_onUpdateProfile);
    on<RefreshUserData>(_onRefreshUserData);
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(state.copyWith(status: AuthStatus.loading));

    try {
      final result = await authRepository.login(
        username: event.username,
        password: event.password,
      );

      await result.fold(
        (failure) async {
          emit(state.copyWith(
            status: AuthStatus.error,
            errorMessage: failure.message,
          ));
        },
        (authResponse) async {
          // Save token
          await secureStorage.saveToken(authResponse.accessToken);

          // Save user data if needed
          if (event.rememberMe) {
            await secureStorage.saveRefreshToken(authResponse.accessToken);
          }

          emit(state.copyWith(
            status: AuthStatus.authenticated,
            user: authResponse.user,
            token: authResponse.accessToken,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'An unexpected error occurred: $e',
      ));
    }
  }

  Future<void> _onRegisterRequested(
    RegisterRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(state.copyWith(status: AuthStatus.loading));

    try {
      final result = await authRepository.register(
        username: event.username,
        email: event.email,
        phoneNumber: event.phoneNumber,
        password: event.password,
        referralCode: event.referralCode,
      );

      await result.fold(
        (failure) async {
          emit(state.copyWith(
            status: AuthStatus.error,
            errorMessage: failure.message,
          ));
        },
        (authResponse) async {
          // Save token
          await secureStorage.saveToken(authResponse.accessToken);

          emit(state.copyWith(
            status: AuthStatus.authenticated,
            user: authResponse.user,
            token: authResponse.accessToken,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'An unexpected error occurred: $e',
      ));
    }
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(state.copyWith(status: AuthStatus.loading));

    try {
      await secureStorage.deleteToken();
      await secureStorage.deleteRefreshToken();

      emit(const AuthState(status: AuthStatus.unauthenticated));
    } catch (e) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Failed to logout: $e',
      ));
    }
  }

  Future<void> _onCheckAuthStatus(
    CheckAuthStatus event,
    Emitter<AuthState> emit,
  ) async {
    emit(state.copyWith(status: AuthStatus.loading));

    try {
      final token = await secureStorage.getToken();

      if (token == null || token.isEmpty) {
        emit(const AuthState(status: AuthStatus.unauthenticated));
        return;
      }

      final result = await authRepository.getCurrentUser();

      result.fold(
        (failure) {
          emit(const AuthState(status: AuthStatus.unauthenticated));
        },
        (user) {
          emit(AuthState(
            status: AuthStatus.authenticated,
            user: user,
            token: token,
          ));
        },
      );
    } catch (e) {
      emit(const AuthState(status: AuthStatus.unauthenticated));
    }
  }

  Future<void> _onUpdateProfile(
    UpdateProfile event,
    Emitter<AuthState> emit,
  ) async {
    if (state.user == null) return;

    emit(state.copyWith(status: AuthStatus.loading));

    try {
      final result = await authRepository.updateProfile(
        fullName: event.fullName,
        email: event.email,
        phoneNumber: event.phoneNumber,
        avatarUrl: event.avatarUrl,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: AuthStatus.error,
            errorMessage: failure.message,
          ));
        },
        (updatedUser) {
          emit(state.copyWith(
            status: AuthStatus.authenticated,
            user: updatedUser,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Failed to update profile: $e',
      ));
    }
  }

  Future<void> _onRefreshUserData(
    RefreshUserData event,
    Emitter<AuthState> emit,
  ) async {
    if (state.user == null) return;

    try {
      final result = await authRepository.getCurrentUser();

      result.fold(
        (failure) {
          // Don't change state if refresh fails
        },
        (user) {
          emit(state.copyWith(user: user));
        },
      );
    } catch (e) {
      // Silent fail on refresh
    }
  }
}
