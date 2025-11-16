/// API endpoint constants
class ApiEndpoints {
  ApiEndpoints._();

  // Base
  static const String baseUrl = '/api/v1';

  // Authentication
  static const String sendOtp = '$baseUrl/auth/send-otp';
  static const String verifyOtp = '$baseUrl/auth/verify-otp';
  static const String refreshToken = '$baseUrl/auth/refresh';
  static const String logout = '$baseUrl/auth/logout';
  static const String socialLogin = '$baseUrl/auth/social-login';

  // User
  static const String userProfile = '$baseUrl/users/me';
  static const String updateProfile = '$baseUrl/users/me';
  static const String userStatistics = '$baseUrl/users/me/statistics';
  static const String gameHistory = '$baseUrl/users/me/game-history';
  static const String deleteAccount = '$baseUrl/users/me';

  // KYC
  static const String kycStatus = '$baseUrl/kyc/status';
  static const String uploadKycDocument = '$baseUrl/kyc/upload';
  static const String submitKyc = '$baseUrl/kyc/submit';

  // Wallet
  static const String walletBalance = '$baseUrl/wallet/balance';
  static const String walletTransactions = '$baseUrl/wallet/transactions';
  static const String addMoney = '$baseUrl/wallet/deposit';
  static const String withdraw = '$baseUrl/wallet/withdraw';
  static const String applyPromoCode = '$baseUrl/promo-codes/apply';
  static const String validatePromoCode = '$baseUrl/promo-codes/validate';
  static const String availablePromoCodes = '$baseUrl/promo-codes';
  static const String myPromoUsages = '$baseUrl/promo-codes/my-usages';

  // Bank Accounts
  static const String bankAccounts = '$baseUrl/bank/accounts';
  static String bankAccount(String id) => '$baseUrl/bank/accounts/$id';
  static const String addBankAccount = '$baseUrl/bank/accounts';
  static String deleteBankAccount(String id) => '$baseUrl/bank/accounts/$id';
  static String setPrimaryBankAccount(String id) =>
      '$baseUrl/bank/accounts/$id/set-primary';

  // Games
  static const String gameCatalog = '$baseUrl/games/catalog';
  static String gameDetails(String gameId) => '$baseUrl/games/$gameId';
  static String gameSessions(String gameId) => '$baseUrl/games/$gameId/sessions';
  static String joinGameSession(String sessionId) =>
      '$baseUrl/games/sessions/$sessionId/join';
  static String createGameSession = '$baseUrl/games/sessions';
  static String gameSessionDetails(String sessionId) =>
      '$baseUrl/games/sessions/$sessionId';

  // Tournaments
  static const String tournaments = '$baseUrl/games/tournaments';
  static String tournamentDetails(String tournamentId) =>
      '$baseUrl/games/tournaments/$tournamentId';
  static String registerTournament(String tournamentId) =>
      '$baseUrl/games/tournaments/$tournamentId/register';

  // Rewards
  static const String achievements = '$baseUrl/rewards/achievements';
  static const String myAchievements = '$baseUrl/rewards/my-achievements';
  static const String claimAchievement = '$baseUrl/rewards/achievements/claim';
  static const String leaderboard = '$baseUrl/rewards/leaderboard';
  static const String dailyBonus = '$baseUrl/rewards/daily-bonus';
  static const String claimDailyBonus = '$baseUrl/rewards/daily-bonus/claim';

  // Referral
  static const String referralCode = '$baseUrl/rewards/referral/my-code';
  static const String referralStats = '$baseUrl/rewards/referral/stats';
  static const String referralHistory = '$baseUrl/rewards/referral/history';

  // Notifications
  static const String notifications = '$baseUrl/users/notifications';
  static String markNotificationRead(String id) =>
      '$baseUrl/users/notifications/$id/read';
  static const String markAllNotificationsRead =
      '$baseUrl/users/notifications/read-all';
  static String deleteNotification(String id) =>
      '$baseUrl/users/notifications/$id';

  // Two-Factor Authentication
  static const String setup2FA = '$baseUrl/2fa/setup';
  static const String enable2FA = '$baseUrl/2fa/enable';
  static const String verify2FA = '$baseUrl/2fa/verify';
  static const String verifyBackupCode = '$baseUrl/2fa/verify-backup-code';
  static const String disable2FA = '$baseUrl/2fa/disable';
  static const String regenerateBackupCodes = '$baseUrl/2fa/regenerate-backup-codes';
  static const String get2FAStatus = '$baseUrl/2fa/status';

  // WebSocket
  static String gameWebSocket(String sessionId) => '/ws/game/$sessionId';
  static const String notificationsWebSocket = '/ws/notifications';

  // Support
  static const String supportTickets = '$baseUrl/support/tickets';
  static const String createSupportTicket = '$baseUrl/support/tickets';
  static String supportTicketDetails(String ticketId) =>
      '$baseUrl/support/tickets/$ticketId';

  // App Configuration
  static const String appConfig = '$baseUrl/config';
  static const String checkVersion = '$baseUrl/config/version';
}
