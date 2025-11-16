import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../presentation/screens/splash/splash_screen.dart';
import '../../presentation/screens/onboarding/onboarding_screen.dart';
import '../../presentation/screens/auth/login_screen.dart';
import '../../presentation/screens/auth/otp_verification_screen.dart';
import '../../presentation/screens/auth/profile_setup_screen.dart';
import '../../presentation/screens/main/main_screen.dart';
import '../../presentation/screens/notifications/notifications_screen.dart';

/// App router configuration
class AppRouter {
  AppRouter._();

  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String otpVerification = '/otp-verification';
  static const String profileSetup = '/profile-setup';
  static const String main = '/main';
  static const String home = '/home';
  static const String games = '/games';
  static const String wallet = '/wallet';
  static const String rewards = '/rewards';
  static const String profile = '/profile';

  // Game routes
  static const String gameDetails = '/games/:gameId';
  static const String gameLobby = '/games/:gameId/lobby';
  static const String gameRoom = '/games/sessions/:sessionId/room';
  static const String liveGame = '/games/sessions/:sessionId/play';
  static const String gameResult = '/games/sessions/:sessionId/result';

  // Wallet routes
  static const String addMoney = '/wallet/add';
  static const String withdraw = '/wallet/withdraw';
  static const String transactions = '/wallet/transactions';
  static const String bankAccounts = '/wallet/bank-accounts';

  // Profile routes
  static const String editProfile = '/profile/edit';
  static const String kycVerification = '/profile/kyc';
  static const String gameHistory = '/profile/history';
  static const String statistics = '/profile/statistics';
  static const String settings = '/profile/settings';
  static const String twoFactorAuth = '/profile/2fa';
  static const String helpSupport = '/profile/help';
  static const String notifications = '/notifications';

  // Rewards routes
  static const String referral = '/rewards/referral';
  static const String achievements = '/rewards/achievements';
  static const String leaderboard = '/rewards/leaderboard';

  /// GoRouter configuration
  static final GoRouter router = GoRouter(
    initialLocation: splash,
    debugLogDiagnostics: true,
    routes: [
      // Splash Screen
      GoRoute(
        path: splash,
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),

      // Onboarding
      GoRoute(
        path: onboarding,
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),

      // Authentication Routes
      GoRoute(
        path: login,
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: otpVerification,
        name: 'otp-verification',
        builder: (context, state) {
          final phoneNumber = state.extra as String?;
          return OTPVerificationScreen(phoneNumber: phoneNumber ?? '');
        },
      ),
      GoRoute(
        path: profileSetup,
        name: 'profile-setup',
        builder: (context, state) => const ProfileSetupScreen(),
      ),

      // Main Screen with Bottom Navigation
      GoRoute(
        path: main,
        name: 'main',
        builder: (context, state) => const MainScreen(),
      ),

      // Game Routes
      GoRoute(
        path: gameDetails,
        name: 'game-details',
        builder: (context, state) {
          final gameId = state.pathParameters['gameId']!;
          return Container(); // GameDetailsScreen(gameId: gameId),
        },
      ),
      GoRoute(
        path: gameLobby,
        name: 'game-lobby',
        builder: (context, state) {
          final gameId = state.pathParameters['gameId']!;
          return Container(); // GameLobbyScreen(gameId: gameId),
        },
      ),
      GoRoute(
        path: gameRoom,
        name: 'game-room',
        builder: (context, state) {
          final sessionId = state.pathParameters['sessionId']!;
          return Container(); // GameRoomScreen(sessionId: sessionId),
        },
      ),
      GoRoute(
        path: liveGame,
        name: 'live-game',
        builder: (context, state) {
          final sessionId = state.pathParameters['sessionId']!;
          return Container(); // LiveGameScreen(sessionId: sessionId),
        },
      ),
      GoRoute(
        path: gameResult,
        name: 'game-result',
        builder: (context, state) {
          final sessionId = state.pathParameters['sessionId']!;
          return Container(); // GameResultScreen(sessionId: sessionId),
        },
      ),

      // Wallet Routes
      GoRoute(
        path: addMoney,
        name: 'add-money',
        builder: (context, state) => Container(), // AddMoneyScreen(),
      ),
      GoRoute(
        path: withdraw,
        name: 'withdraw',
        builder: (context, state) => Container(), // WithdrawScreen(),
      ),
      GoRoute(
        path: transactions,
        name: 'transactions',
        builder: (context, state) => Container(), // TransactionsScreen(),
      ),
      GoRoute(
        path: bankAccounts,
        name: 'bank-accounts',
        builder: (context, state) => Container(), // BankAccountsScreen(),
      ),

      // Profile Routes
      GoRoute(
        path: editProfile,
        name: 'edit-profile',
        builder: (context, state) => Container(), // EditProfileScreen(),
      ),
      GoRoute(
        path: kycVerification,
        name: 'kyc-verification',
        builder: (context, state) => Container(), // KYCVerificationScreen(),
      ),
      GoRoute(
        path: gameHistory,
        name: 'game-history',
        builder: (context, state) => Container(), // GameHistoryScreen(),
      ),
      GoRoute(
        path: statistics,
        name: 'statistics',
        builder: (context, state) => Container(), // StatisticsScreen(),
      ),
      GoRoute(
        path: settings,
        name: 'settings',
        builder: (context, state) => Container(), // SettingsScreen(),
      ),
      GoRoute(
        path: twoFactorAuth,
        name: '2fa',
        builder: (context, state) => Container(), // TwoFactorAuthScreen(),
      ),
      GoRoute(
        path: helpSupport,
        name: 'help-support',
        builder: (context, state) => Container(), // HelpSupportScreen(),
      ),
      GoRoute(
        path: notifications,
        name: 'notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),

      // Rewards Routes
      GoRoute(
        path: referral,
        name: 'referral',
        builder: (context, state) => Container(), // ReferralScreen(),
      ),
      GoRoute(
        path: achievements,
        name: 'achievements',
        builder: (context, state) => Container(), // AchievementsScreen(),
      ),
      GoRoute(
        path: leaderboard,
        name: 'leaderboard',
        builder: (context, state) => Container(), // LeaderboardScreen(),
      ),
    ],

    // Error page
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),

    // Redirect logic for authentication
    redirect: (context, state) {
      // TODO: Implement authentication redirect logic
      // Check if user is logged in
      // If not logged in and trying to access protected route, redirect to login
      return null; // No redirect for now
    },
  );
}
