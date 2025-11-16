import 'package:json_annotation/json_annotation.dart';

part 'kyc_model.g.dart';

/// KYC document model
@JsonSerializable()
class KYCDocumentModel {
  final String id;
  @JsonKey(name: 'document_type')
  final String documentType;
  @JsonKey(name: 'document_number')
  final String documentNumber;
  @JsonKey(name: 'front_image_url')
  final String? frontImageUrl;
  @JsonKey(name: 'back_image_url')
  final String? backImageUrl;
  final String status;
  @JsonKey(name: 'rejection_reason')
  final String? rejectionReason;
  @JsonKey(name: 'submitted_at')
  final DateTime? submittedAt;
  @JsonKey(name: 'verified_at')
  final DateTime? verifiedAt;

  KYCDocumentModel({
    required this.id,
    required this.documentType,
    required this.documentNumber,
    this.frontImageUrl,
    this.backImageUrl,
    required this.status,
    this.rejectionReason,
    this.submittedAt,
    this.verifiedAt,
  });

  factory KYCDocumentModel.fromJson(Map<String, dynamic> json) =>
      _$KYCDocumentModelFromJson(json);

  Map<String, dynamic> toJson() => _$KYCDocumentModelToJson(this);

  bool get isPending => status == 'pending';
  bool get isVerified => status == 'verified';
  bool get isRejected => status == 'rejected';
}

/// KYC status model
@JsonSerializable()
class KYCStatusModel {
  final String status;
  @JsonKey(name: 'kyc_level')
  final int kycLevel;
  @JsonKey(name: 'is_verified')
  final bool isVerified;
  @JsonKey(name: 'documents_submitted')
  final int documentsSubmitted;
  @JsonKey(name: 'documents_verified')
  final int documentsVerified;
  @JsonKey(name: 'rejection_reason')
  final String? rejectionReason;
  @JsonKey(name: 'submitted_at')
  final DateTime? submittedAt;
  @JsonKey(name: 'approved_at')
  final DateTime? approvedAt;

  KYCStatusModel({
    required this.status,
    required this.kycLevel,
    required this.isVerified,
    required this.documentsSubmitted,
    required this.documentsVerified,
    this.rejectionReason,
    this.submittedAt,
    this.approvedAt,
  });

  factory KYCStatusModel.fromJson(Map<String, dynamic> json) =>
      _$KYCStatusModelFromJson(json);

  Map<String, dynamic> toJson() => _$KYCStatusModelToJson(this);

  bool get canWithdraw => isVerified && kycLevel >= 1;
  bool get needsDocuments => documentsSubmitted == 0;
}

/// KYC submission request model
@JsonSerializable()
class KYCSubmissionModel {
  @JsonKey(name: 'document_type')
  final String documentType;
  @JsonKey(name: 'document_number')
  final String documentNumber;
  @JsonKey(name: 'front_image')
  final String frontImage; // Base64 or file path
  @JsonKey(name: 'back_image')
  final String? backImage;

  KYCSubmissionModel({
    required this.documentType,
    required this.documentNumber,
    required this.frontImage,
    this.backImage,
  });

  factory KYCSubmissionModel.fromJson(Map<String, dynamic> json) =>
      _$KYCSubmissionModelFromJson(json);

  Map<String, dynamic> toJson() => _$KYCSubmissionModelToJson(this);
}
