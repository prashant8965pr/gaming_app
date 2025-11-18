import 'package:equatable/equatable.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class LoginRequested extends AuthEvent {
  final String username;
  final String password;
  final bool rememberMe;

  const LoginRequested({
    required this.username,
    required this.password,
    this.rememberMe = false,
  });

  @override
  List<Object?> get props => [username, password, rememberMe];
}

class RegisterRequested extends AuthEvent {
  final String username;
  final String email;
  final String phoneNumber;
  final String password;
  final String referralCode;

  const RegisterRequested({
    required this.username,
    required this.email,
    required this.phoneNumber,
    required this.password,
    this.referralCode = '',
  });

  @override
  List<Object?> get props => [username, email, phoneNumber, password, referralCode];
}

class LogoutRequested extends AuthEvent {
  const LogoutRequested();
}

class CheckAuthStatus extends AuthEvent {
  const CheckAuthStatus();
}

class UpdateProfile extends AuthEvent {
  final String? fullName;
  final String? email;
  final String? phoneNumber;
  final String? avatarUrl;

  const UpdateProfile({
    this.fullName,
    this.email,
    this.phoneNumber,
    this.avatarUrl,
  });

  @override
  List<Object?> get props => [fullName, email, phoneNumber, avatarUrl];
}

class RefreshUserData extends AuthEvent {
  const RefreshUserData();
}
