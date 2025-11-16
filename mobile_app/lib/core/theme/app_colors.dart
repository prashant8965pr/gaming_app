import 'package:flutter/material.dart';

/// Application color palette
class AppColors {
  AppColors._();

  // Primary Colors
  static const Color primary = Color(0xFFFF6B35); // Orange
  static const Color primaryDark = Color(0xFFE55A2B);
  static const Color primaryLight = Color(0xFFFF8C5F);

  // Secondary Colors
  static const Color secondary = Color(0xFF004E89); // Blue
  static const Color secondaryDark = Color(0xFF003A68);
  static const Color secondaryLight = Color(0xFF1A6BA0);

  // Success, Warning, Error
  static const Color success = Color(0xFF2ECC71); // Green
  static const Color warning = Color(0xFFF39C12); // Amber
  static const Color error = Color(0xFFE74C3C); // Red

  // Background Colors
  static const Color backgroundLight = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF1A1A1A);

  // Surface Colors
  static const Color surfaceLight = Color(0xFFF5F5F5);
  static const Color surfaceDark = Color(0xFF2C2C2C);

  // Text Colors
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color textHint = Color(0xFFBDBDBD);
  static const Color textWhite = Color(0xFFFFFFFF);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFFFF6B35), Color(0xFFFF8C5F)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient secondaryGradient = LinearGradient(
    colors: [Color(0xFF004E89), Color(0xFF1A6BA0)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFFFD700), Color(0xFFFFA500)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient walletGradient = LinearGradient(
    colors: [Color(0xFF00B4DB), Color(0xFF0083B0)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient achievementGradient = LinearGradient(
    colors: [Color(0xFF667eea), Color(0xFF764ba2)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Game-specific Colors
  static const Color ludoRed = Color(0xFFE74C3C);
  static const Color ludoBlue = Color(0xFF3498DB);
  static const Color ludoGreen = Color(0xFF2ECC71);
  static const Color ludoYellow = Color(0xFFF39C12);

  // Wallet Colors
  static const Color cashWallet = Color(0xFF2ECC71); // Green
  static const Color bonusWallet = Color(0xFFF39C12); // Amber
  static const Color winningsWallet = Color(0xFF9B59B6); // Purple

  // Notification Colors
  static const Color notificationInfo = Color(0xFF3498DB);
  static const Color notificationSuccess = Color(0xFF2ECC71);
  static const Color notificationWarning = Color(0xFFF39C12);
  static const Color notificationError = Color(0xFFE74C3C);

  // Additional Colors
  static const Color divider = Color(0xFFE0E0E0);
  static const Color shadow = Color(0x1A000000);
  static const Color overlay = Color(0x80000000);
  static const Color transparent = Colors.transparent;

  // Shimmer Colors
  static const Color shimmerBase = Color(0xFFE0E0E0);
  static const Color shimmerHighlight = Color(0xFFF5F5F5);
  static const Color shimmerBaseDark = Color(0xFF2C2C2C);
  static const Color shimmerHighlightDark = Color(0xFF3A3A3A);
}
