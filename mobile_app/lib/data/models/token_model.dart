import 'package:equatable/equatable.dart';

class TokenWalletModel extends Equatable {
  final String id;
  final String userId;
  final int balance;
  final int totalEarned;
  final int totalSpent;
  final DateTime? lastDailyClaim;
  final int dailyClaimStreak;
  final DateTime? lastAdWatch;
  final int adsWatchedToday;
  final DateTime? adsResetDate;
  final DateTime createdAt;
  final DateTime updatedAt;

  const TokenWalletModel({
    required this.id,
    required this.userId,
    required this.balance,
    required this.totalEarned,
    required this.totalSpent,
    this.lastDailyClaim,
    required this.dailyClaimStreak,
    this.lastAdWatch,
    required this.adsWatchedToday,
    this.adsResetDate,
    required this.createdAt,
    required this.updatedAt,
  });

  factory TokenWalletModel.fromJson(Map<String, dynamic> json) {
    return TokenWalletModel(
      id: json['id'],
      userId: json['user_id'],
      balance: json['balance'],
      totalEarned: json['total_earned'],
      totalSpent: json['total_spent'],
      lastDailyClaim: json['last_daily_claim'] != null
          ? DateTime.parse(json['last_daily_claim'])
          : null,
      dailyClaimStreak: json['daily_claim_streak'] ?? 0,
      lastAdWatch: json['last_ad_watch'] != null
          ? DateTime.parse(json['last_ad_watch'])
          : null,
      adsWatchedToday: json['ads_watched_today'] ?? 0,
      adsResetDate: json['ads_reset_date'] != null
          ? DateTime.parse(json['ads_reset_date'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'balance': balance,
      'total_earned': totalEarned,
      'total_spent': totalSpent,
      'last_daily_claim': lastDailyClaim?.toIso8601String(),
      'daily_claim_streak': dailyClaimStreak,
      'last_ad_watch': lastAdWatch?.toIso8601String(),
      'ads_watched_today': adsWatchedToday,
      'ads_reset_date': adsResetDate?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  bool get canClaimDailyBonus {
    if (lastDailyClaim == null) return true;
    final now = DateTime.now();
    return lastDailyClaim!.day != now.day ||
        lastDailyClaim!.month != now.month ||
        lastDailyClaim!.year != now.year;
  }

  bool get canWatchAd => adsWatchedToday < 5;

  int get adsRemaining => 5 - adsWatchedToday;

  int get nextDailyBonusAmount {
    final baseBonus = 100;
    final streakBonus = (dailyClaimStreak + 1) * 10;
    final cappedStreakBonus = streakBonus > 100 ? 100 : streakBonus;
    return baseBonus + cappedStreakBonus;
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        balance,
        totalEarned,
        totalSpent,
        lastDailyClaim,
        dailyClaimStreak,
        lastAdWatch,
        adsWatchedToday,
        adsResetDate,
        createdAt,
        updatedAt,
      ];
}

class TokenTransactionModel extends Equatable {
  final String id;
  final String userId;
  final String walletId;
  final int amount;
  final String transactionType;
  final String source;
  final String description;
  final int balanceAfter;
  final DateTime createdAt;

  const TokenTransactionModel({
    required this.id,
    required this.userId,
    required this.walletId,
    required this.amount,
    required this.transactionType,
    required this.source,
    required this.description,
    required this.balanceAfter,
    required this.createdAt,
  });

  factory TokenTransactionModel.fromJson(Map<String, dynamic> json) {
    return TokenTransactionModel(
      id: json['id'],
      userId: json['user_id'],
      walletId: json['wallet_id'],
      amount: json['amount'],
      transactionType: json['transaction_type'],
      source: json['source'],
      description: json['description'],
      balanceAfter: json['balance_after'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'wallet_id': walletId,
      'amount': amount,
      'transaction_type': transactionType,
      'source': source,
      'description': description,
      'balance_after': balanceAfter,
      'created_at': createdAt.toIso8601String(),
    };
  }

  bool get isEarn => transactionType == 'earn';
  bool get isSpend => transactionType == 'spend';

  String get typeDisplay {
    switch (transactionType) {
      case 'earn':
        return 'Earned';
      case 'spend':
        return 'Spent';
      default:
        return transactionType;
    }
  }

  String get sourceDisplay {
    switch (source) {
      case 'daily_login':
        return 'Daily Login';
      case 'ad_watch':
        return 'Ad Watch';
      case 'achievement':
        return 'Achievement';
      case 'practice_game':
        return 'Practice Game';
      case 'referral':
        return 'Referral Bonus';
      default:
        return source;
    }
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        walletId,
        amount,
        transactionType,
        source,
        description,
        balanceAfter,
        createdAt,
      ];
}

class TokenPackageModel extends Equatable {
  final String id;
  final String name;
  final String? description;
  final int tokenAmount;
  final double price;
  final String currency;
  final int? bonusTokens;
  final bool isActive;
  final bool isFeatured;
  final int sortOrder;

  const TokenPackageModel({
    required this.id,
    required this.name,
    this.description,
    required this.tokenAmount,
    required this.price,
    required this.currency,
    this.bonusTokens,
    required this.isActive,
    required this.isFeatured,
    required this.sortOrder,
  });

  factory TokenPackageModel.fromJson(Map<String, dynamic> json) {
    return TokenPackageModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      tokenAmount: json['token_amount'],
      price: json['price'].toDouble(),
      currency: json['currency'],
      bonusTokens: json['bonus_tokens'],
      isActive: json['is_active'] ?? true,
      isFeatured: json['is_featured'] ?? false,
      sortOrder: json['sort_order'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'token_amount': tokenAmount,
      'price': price,
      'currency': currency,
      'bonus_tokens': bonusTokens,
      'is_active': isActive,
      'is_featured': isFeatured,
      'sort_order': sortOrder,
    };
  }

  int get totalTokens => tokenAmount + (bonusTokens ?? 0);

  String get priceDisplay {
    switch (currency) {
      case 'USD':
        return '\$${price.toStringAsFixed(2)}';
      case 'INR':
        return '₹${price.toStringAsFixed(0)}';
      case 'EUR':
        return '€${price.toStringAsFixed(2)}';
      default:
        return '$currency ${price.toStringAsFixed(2)}';
    }
  }

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        tokenAmount,
        price,
        currency,
        bonusTokens,
        isActive,
        isFeatured,
        sortOrder,
      ];
}

class DailyBonusResponse extends Equatable {
  final int tokensEarned;
  final int currentStreak;
  final int newBalance;

  const DailyBonusResponse({
    required this.tokensEarned,
    required this.currentStreak,
    required this.newBalance,
  });

  factory DailyBonusResponse.fromJson(Map<String, dynamic> json) {
    return DailyBonusResponse(
      tokensEarned: json['tokens_earned'],
      currentStreak: json['current_streak'],
      newBalance: json['new_balance'],
    );
  }

  @override
  List<Object?> get props => [tokensEarned, currentStreak, newBalance];
}

class AdRewardResponse extends Equatable {
  final int tokensEarned;
  final int adsWatchedToday;
  final int adsRemaining;
  final int newBalance;

  const AdRewardResponse({
    required this.tokensEarned,
    required this.adsWatchedToday,
    required this.adsRemaining,
    required this.newBalance,
  });

  factory AdRewardResponse.fromJson(Map<String, dynamic> json) {
    return AdRewardResponse(
      tokensEarned: json['tokens_earned'],
      adsWatchedToday: json['ads_watched_today'],
      adsRemaining: json['ads_remaining'],
      newBalance: json['new_balance'],
    );
  }

  @override
  List<Object?> get props =>
      [tokensEarned, adsWatchedToday, adsRemaining, newBalance];
}
