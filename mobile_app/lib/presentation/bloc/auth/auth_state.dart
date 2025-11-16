import 'package:equatable/equatable.dart';
import '../../../data/models/user_model.dart';

/// Base class for all auth states
abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

/// Initial state
class AuthInitial extends AuthState {
  const AuthInitial();
}

/// Loading state
class AuthLoading extends AuthState {
  const AuthLoading();
}

/// OTP sent successfully
class OTPSent extends AuthState {
  final String phoneNumber;
  final String message;

  const OTPSent({
    required this.phoneNumber,
    required this.message,
  });

  @override
  List<Object?> get props => [phoneNumber, message];
}

/// OTP verified - user needs to complete profile
class OTPVerifiedNewUser extends AuthState {
  const OTPVerifiedNewUser();
}

/// User authenticated successfully
class Authenticated extends AuthState {
  final UserModel user;

  const Authenticated({required this.user});

  @override
  List<Object?> get props => [user];
}

/// User not authenticated
class Unauthenticated extends AuthState {
  const Unauthenticated();
}

/// Error state
class AuthError extends AuthState {
  final String message;

  const AuthError({required this.message});

  @override
  List<Object?> get props => [message];
}

/// Token refreshed successfully
class TokenRefreshed extends AuthState {
  const TokenRefreshed();
}
