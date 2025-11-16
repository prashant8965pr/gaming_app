import 'package:hive_flutter/hive_flutter.dart';

/// Hive box names
class HiveBoxes {
  static const String user = 'user_box';
  static const String wallet = 'wallet_box';
  static const String games = 'games_box';
  static const String transactions = 'transactions_box';
  static const String notifications = 'notifications_box';
  static const String cache = 'cache_box';
}

/// Hive configuration and initialization
class HiveConfig {
  /// Initialize Hive and open all boxes
  static Future<void> init() async {
    await Hive.initFlutter();

    // Register adapters here if using custom objects
    // Hive.registerAdapter(UserModelAdapter());

    // Open all boxes
    await Future.wait([
      Hive.openBox(HiveBoxes.user),
      Hive.openBox(HiveBoxes.wallet),
      Hive.openBox(HiveBoxes.games),
      Hive.openBox(HiveBoxes.transactions),
      Hive.openBox(HiveBoxes.notifications),
      Hive.openBox(HiveBoxes.cache),
    ]);
  }

  /// Close all boxes
  static Future<void> closeAll() async {
    await Hive.close();
  }

  /// Clear all boxes
  static Future<void> clearAll() async {
    await Future.wait([
      Hive.box(HiveBoxes.user).clear(),
      Hive.box(HiveBoxes.wallet).clear(),
      Hive.box(HiveBoxes.games).clear(),
      Hive.box(HiveBoxes.transactions).clear(),
      Hive.box(HiveBoxes.notifications).clear(),
      Hive.box(HiveBoxes.cache).clear(),
    ]);
  }

  /// Delete all boxes
  static Future<void> deleteAll() async {
    await Future.wait([
      Hive.deleteBoxFromDisk(HiveBoxes.user),
      Hive.deleteBoxFromDisk(HiveBoxes.wallet),
      Hive.deleteBoxFromDisk(HiveBoxes.games),
      Hive.deleteBoxFromDisk(HiveBoxes.transactions),
      Hive.deleteBoxFromDisk(HiveBoxes.notifications),
      Hive.deleteBoxFromDisk(HiveBoxes.cache),
    ]);
  }
}

/// Cache keys
class CacheKeys {
  static const String userProfile = 'user_profile';
  static const String walletBalance = 'wallet_balance';
  static const String gamesList = 'games_list';
  static const String activeGames = 'active_games';
  static const String leaderboard = 'leaderboard';
  static const String achievements = 'achievements';
  static const String referralData = 'referral_data';
  static const String kycStatus = 'kyc_status';
}

/// Cache helper for managing cached data
class CacheHelper {
  final Box _cacheBox;

  CacheHelper(this._cacheBox);

  /// Save data to cache with expiration
  Future<void> save({
    required String key,
    required dynamic data,
    Duration? expiresIn,
  }) async {
    final cacheData = {
      'data': data,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'expiresAt': expiresIn != null
          ? DateTime.now().add(expiresIn).millisecondsSinceEpoch
          : null,
    };
    await _cacheBox.put(key, cacheData);
  }

  /// Get data from cache
  dynamic get(String key) {
    final cacheData = _cacheBox.get(key);
    if (cacheData == null) return null;

    // Check if expired
    final expiresAt = cacheData['expiresAt'];
    if (expiresAt != null &&
        DateTime.now().millisecondsSinceEpoch > expiresAt) {
      _cacheBox.delete(key);
      return null;
    }

    return cacheData['data'];
  }

  /// Check if cache exists and is valid
  bool has(String key) {
    return get(key) != null;
  }

  /// Delete specific cache
  Future<void> delete(String key) async {
    await _cacheBox.delete(key);
  }

  /// Clear all cache
  Future<void> clearAll() async {
    await _cacheBox.clear();
  }

  /// Get cache age in milliseconds
  int? getCacheAge(String key) {
    final cacheData = _cacheBox.get(key);
    if (cacheData == null) return null;

    final timestamp = cacheData['timestamp'] as int?;
    if (timestamp == null) return null;

    return DateTime.now().millisecondsSinceEpoch - timestamp;
  }

  /// Check if cache is older than duration
  bool isOlderThan(String key, Duration duration) {
    final age = getCacheAge(key);
    if (age == null) return true;
    return age > duration.inMilliseconds;
  }
}
