import 'package:shared_preferences/shared_preferences.dart';

/// Local storage wrapper for app settings and preferences
class LocalStorage {
  final SharedPreferences _prefs;

  LocalStorage(this._prefs);

  // Onboarding
  static const String _onboardingCompletedKey = 'onboarding_completed';

  Future<void> setOnboardingCompleted(bool completed) async {
    await _prefs.setBool(_onboardingCompletedKey, completed);
  }

  bool isOnboardingCompleted() {
    return _prefs.getBool(_onboardingCompletedKey) ?? false;
  }

  // Theme
  static const String _themeKey = 'theme_mode';

  Future<void> setThemeMode(String mode) async {
    await _prefs.setString(_themeKey, mode);
  }

  String getThemeMode() {
    return _prefs.getString(_themeKey) ?? 'system';
  }

  // Language
  static const String _languageKey = 'language';

  Future<void> setLanguage(String languageCode) async {
    await _prefs.setString(_languageKey, languageCode);
  }

  String getLanguage() {
    return _prefs.getString(_languageKey) ?? 'en';
  }

  // Notifications
  static const String _notificationsEnabledKey = 'notifications_enabled';

  Future<void> setNotificationsEnabled(bool enabled) async {
    await _prefs.setBool(_notificationsEnabledKey, enabled);
  }

  bool areNotificationsEnabled() {
    return _prefs.getBool(_notificationsEnabledKey) ?? true;
  }

  // Sound effects
  static const String _soundEnabledKey = 'sound_enabled';

  Future<void> setSoundEnabled(bool enabled) async {
    await _prefs.setBool(_soundEnabledKey, enabled);
  }

  bool isSoundEnabled() {
    return _prefs.getBool(_soundEnabledKey) ?? true;
  }

  // Vibration
  static const String _vibrationEnabledKey = 'vibration_enabled';

  Future<void> setVibrationEnabled(bool enabled) async {
    await _prefs.setBool(_vibrationEnabledKey, enabled);
  }

  bool isVibrationEnabled() {
    return _prefs.getBool(_vibrationEnabledKey) ?? true;
  }

  // FCM Token
  static const String _fcmTokenKey = 'fcm_token';

  Future<void> saveFCMToken(String token) async {
    await _prefs.setString(_fcmTokenKey, token);
  }

  String? getFCMToken() {
    return _prefs.getString(_fcmTokenKey);
  }

  // Last sync time
  static const String _lastSyncKey = 'last_sync';

  Future<void> setLastSyncTime(DateTime time) async {
    await _prefs.setInt(_lastSyncKey, time.millisecondsSinceEpoch);
  }

  DateTime? getLastSyncTime() {
    final timestamp = _prefs.getInt(_lastSyncKey);
    return timestamp != null
        ? DateTime.fromMillisecondsSinceEpoch(timestamp)
        : null;
  }

  // App version
  static const String _appVersionKey = 'app_version';

  Future<void> setAppVersion(String version) async {
    await _prefs.setString(_appVersionKey, version);
  }

  String? getAppVersion() {
    return _prefs.getString(_appVersionKey);
  }

  // First install time
  static const String _firstInstallKey = 'first_install_time';

  Future<void> setFirstInstallTime(DateTime time) async {
    final existing = _prefs.getInt(_firstInstallKey);
    if (existing == null) {
      await _prefs.setInt(_firstInstallKey, time.millisecondsSinceEpoch);
    }
  }

  DateTime? getFirstInstallTime() {
    final timestamp = _prefs.getInt(_firstInstallKey);
    return timestamp != null
        ? DateTime.fromMillisecondsSinceEpoch(timestamp)
        : null;
  }

  // Clear all preferences
  Future<void> clearAll() async {
    await _prefs.clear();
  }
}
