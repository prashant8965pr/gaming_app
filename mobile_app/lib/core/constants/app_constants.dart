/// App-wide constants
class AppConstants {
  AppConstants._();

  // App Info
  static const String appName = 'Gaming Platform';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'Play. Win. Repeat.';

  // API Configuration
  static const String baseUrl = 'http://localhost:8000'; // Change to your backend URL
  static const String apiVersion = 'v1';
  static const String apiPrefix = '/api/$apiVersion';

  // WebSocket Configuration
  static const String wsUrl = 'ws://localhost:8000';

  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
  static const String userDataKey = 'user_data';
  static const String isLoggedInKey = 'is_logged_in';
  static const String themeMode Key = 'theme_mode';
  static const String languageKey = 'language';
  static const String onboardingCompletedKey = 'onboarding_completed';

  // Firebase Configuration
  static const String fcmTokenKey = 'fcm_token';

  // Payment Configuration
  static const String razorpayKeyId = 'YOUR_RAZORPAY_KEY'; // Replace with actual key
  static const String razorpayKeySecret = 'YOUR_RAZORPAY_SECRET';

  // Validation
  static const int minUsernameLength = 3;
  static const int maxUsernameLength = 20;
  static const int phoneNumberLength = 10;
  static const int otpLength = 6;
  static const int otpResendTime = 30; // seconds
  static const int passwordMinLength = 8;

  // Wallet
  static const double minDepositAmount = 100.0;
  static const double maxDepositAmount = 100000.0;
  static const double minWithdrawalAmount = 100.0;
  static const double maxWithdrawalAmount = 50000.0;

  // Game Configuration
  static const int maxPlayersLudo = 4;
  static const int maxPlayersRummy = 6;
  static const int maxPlayersPoker = 9;
  static const int gameWaitingTime = 30; // seconds
  static const int turnTimeLimit = 30; // seconds

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // Cache
  static const Duration cacheDuration = Duration(hours: 24);
  static const Duration tokenRefreshBuffer = Duration(minutes: 5);

  // Animation Durations
  static const Duration shortAnimationDuration = Duration(milliseconds: 150);
  static const Duration mediumAnimationDuration = Duration(milliseconds: 300);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);

  // UI
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double defaultBorderRadius = 12.0;
  static const double cardElevation = 2.0;

  // App Links
  static const String termsUrl = 'https://yourapp.com/terms';
  static const String privacyUrl = 'https://yourapp.com/privacy';
  static const String supportEmail = 'support@yourapp.com';
  static const String supportPhone = '+91-1234567890';

  // Social Media
  static const String facebookUrl = 'https://facebook.com/yourapp';
  static const String twitterUrl = 'https://twitter.com/yourapp';
  static const String instagramUrl = 'https://instagram.com/yourapp';

  // Error Messages
  static const String networkErrorMessage = 'No internet connection';
  static const String serverErrorMessage = 'Server error. Please try again later';
  static const String unknownErrorMessage = 'Something went wrong';
  static const String sessionExpiredMessage = 'Session expired. Please login again';
}
