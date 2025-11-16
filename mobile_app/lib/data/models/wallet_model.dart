import 'package:json_annotation/json_annotation.dart';

part 'wallet_model.g.dart';

/// Wallet balance model
@JsonSerializable()
class WalletBalanceModel {
  @JsonKey(name: 'cash_balance')
  final double cashBalance;
  @JsonKey(name: 'bonus_balance')
  final double bonusBalance;
  @JsonKey(name: 'winnings_balance')
  final double winningsBalance;
  @JsonKey(name: 'total_balance')
  final double totalBalance;

  WalletBalanceModel({
    required this.cashBalance,
    required this.bonusBalance,
    required this.winningsBalance,
    required this.totalBalance,
  });

  factory WalletBalanceModel.fromJson(Map<String, dynamic> json) =>
      _$WalletBalanceModelFromJson(json);

  Map<String, dynamic> toJson() => _$WalletBalanceModelToJson(this);
}

/// Transaction model
@JsonSerializable()
class TransactionModel {
  final String id;
  @JsonKey(name: 'user_id')
  final String userId;
  final String type;
  final double amount;
  final String status;
  @JsonKey(name: 'wallet_type')
  final String walletType;
  final String? description;
  @JsonKey(name: 'transaction_id')
  final String? transactionId;
  @JsonKey(name: 'payment_method')
  final String? paymentMethod;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  TransactionModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.amount,
    required this.status,
    required this.walletType,
    this.description,
    this.transactionId,
    this.paymentMethod,
    required this.createdAt,
    required this.updatedAt,
  });

  factory TransactionModel.fromJson(Map<String, dynamic> json) =>
      _$TransactionModelFromJson(json);

  Map<String, dynamic> toJson() => _$TransactionModelToJson(this);
}

/// Bank account model
@JsonSerializable()
class BankAccountModel {
  final String id;
  @JsonKey(name: 'account_holder_name')
  final String accountHolderName;
  @JsonKey(name: 'account_number')
  final String accountNumber;
  @JsonKey(name: 'ifsc_code')
  final String ifscCode;
  @JsonKey(name: 'bank_name')
  final String bankName;
  @JsonKey(name: 'account_type')
  final String accountType;
  @JsonKey(name: 'is_primary')
  final bool isPrimary;
  @JsonKey(name: 'is_verified')
  final bool isVerified;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  BankAccountModel({
    required this.id,
    required this.accountHolderName,
    required this.accountNumber,
    required this.ifscCode,
    required this.bankName,
    required this.accountType,
    required this.isPrimary,
    required this.isVerified,
    required this.createdAt,
  });

  factory BankAccountModel.fromJson(Map<String, dynamic> json) =>
      _$BankAccountModelFromJson(json);

  Map<String, dynamic> toJson() => _$BankAccountModelToJson(this);
}

/// Promo code model
@JsonSerializable()
class PromoCodeModel {
  final String code;
  final String? description;
  final String type;
  final double value;
  @JsonKey(name: 'max_discount')
  final double? maxDiscount;
  @JsonKey(name: 'min_transaction_amount')
  final double? minTransactionAmount;
  @JsonKey(name: 'valid_until')
  final DateTime validUntil;

  PromoCodeModel({
    required this.code,
    this.description,
    required this.type,
    required this.value,
    this.maxDiscount,
    this.minTransactionAmount,
    required this.validUntil,
  });

  factory PromoCodeModel.fromJson(Map<String, dynamic> json) =>
      _$PromoCodeModelFromJson(json);

  Map<String, dynamic> toJson() => _$PromoCodeModelToJson(this);
}
