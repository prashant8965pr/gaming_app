import 'package:hive/hive.dart';
import '../../models/user_model.dart';
import '../../../core/storage/hive_config.dart';

/// Local data source for user data
abstract class UserLocalDataSource {
  Future<void> cacheUser(UserModel user);
  Future<UserModel?> getCachedUser();
  Future<void> clearUser();

  Future<void> cacheUserStatistics(UserStatisticsModel statistics);
  Future<UserStatisticsModel?> getCachedUserStatistics();
}

class UserLocalDataSourceImpl implements UserLocalDataSource {
  final Box _userBox;
  final CacheHelper _cacheHelper;

  UserLocalDataSourceImpl(this._userBox, this._cacheHelper);

  static const String _userKey = 'current_user';
  static const String _statisticsKey = 'user_statistics';

  @override
  Future<void> cacheUser(UserModel user) async {
    await _userBox.put(_userKey, user.toJson());
    await _cacheHelper.save(
      key: CacheKeys.userProfile,
      data: user.toJson(),
      expiresIn: const Duration(hours: 24),
    );
  }

  @override
  Future<UserModel?> getCachedUser() async {
    final userData = _userBox.get(_userKey);
    if (userData == null) return null;

    try {
      return UserModel.fromJson(Map<String, dynamic>.from(userData));
    } catch (e) {
      return null;
    }
  }

  @override
  Future<void> clearUser() async {
    await _userBox.delete(_userKey);
    await _cacheHelper.delete(CacheKeys.userProfile);
  }

  @override
  Future<void> cacheUserStatistics(UserStatisticsModel statistics) async {
    await _userBox.put(_statisticsKey, statistics.toJson());
  }

  @override
  Future<UserStatisticsModel?> getCachedUserStatistics() async {
    final statsData = _userBox.get(_statisticsKey);
    if (statsData == null) return null;

    try {
      return UserStatisticsModel.fromJson(
        Map<String, dynamic>.from(statsData),
      );
    } catch (e) {
      return null;
    }
  }
}
