import 'package:equatable/equatable.dart';

/// Base class for all auth events
abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

/// Event to send OTP to phone number
class SendOTPEvent extends AuthEvent {
  final String phoneNumber;

  const SendOTPEvent({required this.phoneNumber});

  @override
  List<Object?> get props => [phoneNumber];
}

/// Event to verify OTP
class VerifyOTPEvent extends AuthEvent {
  final String phoneNumber;
  final String otp;

  const VerifyOTPEvent({
    required this.phoneNumber,
    required this.otp,
  });

  @override
  List<Object?> get props => [phoneNumber, otp];
}

/// Event for social login
class SocialLoginEvent extends AuthEvent {
  final String provider;
  final String accessToken;
  final String? deviceId;
  final String? deviceName;

  const SocialLoginEvent({
    required this.provider,
    required this.accessToken,
    this.deviceId,
    this.deviceName,
  });

  @override
  List<Object?> get props => [provider, accessToken, deviceId, deviceName];
}

/// Event to complete user profile
class CompleteProfileEvent extends AuthEvent {
  final String username;
  final String displayName;
  final DateTime dateOfBirth;
  final String gender;
  final String? referralCode;

  const CompleteProfileEvent({
    required this.username,
    required this.displayName,
    required this.dateOfBirth,
    required this.gender,
    this.referralCode,
  });

  @override
  List<Object?> get props => [
        username,
        displayName,
        dateOfBirth,
        gender,
        referralCode,
      ];
}

/// Event to logout
class LogoutEvent extends AuthEvent {
  const LogoutEvent();
}

/// Event to check authentication status
class CheckAuthStatusEvent extends AuthEvent {
  const CheckAuthStatusEvent();
}

/// Event to refresh access token
class RefreshTokenEvent extends AuthEvent {
  const RefreshTokenEvent();
}
