import 'package:json_annotation/json_annotation.dart';
import 'user_model.dart';

part 'auth_models.g.dart';

/// Login/OTP response model
@JsonSerializable()
class AuthResponseModel {
  final bool success;
  final String message;
  final AuthDataModel? data;

  AuthResponseModel({
    required this.success,
    required this.message,
    this.data,
  });

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseModelFromJson(json);

  Map<String, dynamic> toJson() => _$AuthResponseModelToJson(this);
}

/// Auth data containing tokens and user
@JsonSerializable()
class AuthDataModel {
  @JsonKey(name: 'access_token')
  final String accessToken;
  @JsonKey(name: 'refresh_token')
  final String refreshToken;
  @JsonKey(name: 'token_type')
  final String tokenType;
  @JsonKey(name: 'expires_in')
  final int expiresIn;
  final UserModel user;
  @JsonKey(name: 'is_new_user')
  final bool? isNewUser;

  AuthDataModel({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
    this.isNewUser,
  });

  factory AuthDataModel.fromJson(Map<String, dynamic> json) =>
      _$AuthDataModelFromJson(json);

  Map<String, dynamic> toJson() => _$AuthDataModelToJson(this);
}

/// Send OTP response
@JsonSerializable()
class SendOTPResponseModel {
  final bool success;
  final String message;
  final SendOTPDataModel? data;

  SendOTPResponseModel({
    required this.success,
    required this.message,
    this.data,
  });

  factory SendOTPResponseModel.fromJson(Map<String, dynamic> json) =>
      _$SendOTPResponseModelFromJson(json);

  Map<String, dynamic> toJson() => _$SendOTPResponseModelToJson(this);
}

@JsonSerializable()
class SendOTPDataModel {
  @JsonKey(name: 'otp_sent')
  final bool otpSent;
  @JsonKey(name: 'expires_in')
  final int expiresIn;

  SendOTPDataModel({
    required this.otpSent,
    required this.expiresIn,
  });

  factory SendOTPDataModel.fromJson(Map<String, dynamic> json) =>
      _$SendOTPDataModelFromJson(json);

  Map<String, dynamic> toJson() => _$SendOTPDataModelToJson(this);
}

/// Social login request
@JsonSerializable()
class SocialLoginRequestModel {
  final String provider; // google, facebook, apple
  @JsonKey(name: 'access_token')
  final String accessToken;
  @JsonKey(name: 'device_id')
  final String? deviceId;
  @JsonKey(name: 'device_name')
  final String? deviceName;
  @JsonKey(name: 'device_os')
  final String? deviceOs;

  SocialLoginRequestModel({
    required this.provider,
    required this.accessToken,
    this.deviceId,
    this.deviceName,
    this.deviceOs,
  });

  factory SocialLoginRequestModel.fromJson(Map<String, dynamic> json) =>
      _$SocialLoginRequestModelFromJson(json);

  Map<String, dynamic> toJson() => _$SocialLoginRequestModelToJson(this);
}

/// Profile setup request
@JsonSerializable()
class ProfileSetupRequestModel {
  final String username;
  @JsonKey(name: 'display_name')
  final String displayName;
  @JsonKey(name: 'date_of_birth')
  final String dateOfBirth; // YYYY-MM-DD format
  final String? gender;
  @JsonKey(name: 'referral_code')
  final String? referralCode;

  ProfileSetupRequestModel({
    required this.username,
    required this.displayName,
    required this.dateOfBirth,
    this.gender,
    this.referralCode,
  });

  factory ProfileSetupRequestModel.fromJson(Map<String, dynamic> json) =>
      _$ProfileSetupRequestModelFromJson(json);

  Map<String, dynamic> toJson() => _$ProfileSetupRequestModelToJson(this);
}
