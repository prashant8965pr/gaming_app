import 'package:intl/intl.dart';

/// Formatting utilities for currency, dates, etc.
class Formatters {
  Formatters._();

  /// Format amount to Indian currency (₹)
  static String currency(double amount, {bool showSymbol = true}) {
    final formatter = NumberFormat.currency(
      locale: 'en_IN',
      symbol: showSymbol ? '₹' : '',
      decimalDigits: 2,
    );
    return formatter.format(amount);
  }

  /// Format amount without decimals
  static String currencyCompact(double amount, {bool showSymbol = true}) {
    final formatter = NumberFormat.currency(
      locale: 'en_IN',
      symbol: showSymbol ? '₹' : '',
      decimalDigits: 0,
    );
    return formatter.format(amount);
  }

  /// Format large numbers (1K, 1M, etc.)
  static String compactNumber(int number) {
    if (number < 1000) {
      return number.toString();
    } else if (number < 1000000) {
      final value = number / 1000;
      return '${value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1)}K';
    } else if (number < 1000000000) {
      final value = number / 1000000;
      return '${value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1)}M';
    } else {
      final value = number / 1000000000;
      return '${value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1)}B';
    }
  }

  /// Format phone number
  static String phoneNumber(String phone) {
    if (phone.length == 10) {
      return '+91 ${phone.substring(0, 5)} ${phone.substring(5)}';
    }
    return phone;
  }

  /// Format date to readable format
  static String date(DateTime date) {
    return DateFormat('dd MMM yyyy').format(date);
  }

  /// Format date with time
  static String dateTime(DateTime dateTime) {
    return DateFormat('dd MMM yyyy, hh:mm a').format(dateTime);
  }

  /// Format time only
  static String time(DateTime dateTime) {
    return DateFormat('hh:mm a').format(dateTime);
  }

  /// Format relative time (e.g., "2 hours ago")
  static String relativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 365) {
      final years = (difference.inDays / 365).floor();
      return '$years ${years == 1 ? 'year' : 'years'} ago';
    } else if (difference.inDays > 30) {
      final months = (difference.inDays / 30).floor();
      return '$months ${months == 1 ? 'month' : 'months'} ago';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} ${difference.inDays == 1 ? 'day' : 'days'} ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} ${difference.inHours == 1 ? 'hour' : 'hours'} ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} ${difference.inMinutes == 1 ? 'minute' : 'minutes'} ago';
    } else {
      return 'Just now';
    }
  }

  /// Format percentage
  static String percentage(double value, {int decimals = 0}) {
    return '${value.toStringAsFixed(decimals)}%';
  }

  /// Format account number (mask middle digits)
  static String maskAccountNumber(String accountNumber) {
    if (accountNumber.length <= 4) {
      return accountNumber;
    }
    final visible = accountNumber.length - 4;
    return 'X' * visible + accountNumber.substring(visible);
  }

  /// Format card number (mask middle digits)
  static String maskCardNumber(String cardNumber) {
    if (cardNumber.length < 4) {
      return cardNumber;
    }
    return '**** **** **** ${cardNumber.substring(cardNumber.length - 4)}';
  }

  /// Format duration (for game time)
  static String duration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    final seconds = duration.inSeconds.remainder(60);

    if (hours > 0) {
      return '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    } else {
      return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
  }

  /// Capitalize first letter
  static String capitalize(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  /// Title case
  static String titleCase(String text) {
    if (text.isEmpty) return text;
    return text.split(' ').map((word) => capitalize(word.toLowerCase())).join(' ');
  }

  /// Format file size
  static String fileSize(int bytes) {
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(2)} KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(2)} MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
    }
  }

  /// Format Aadhaar number
  static String aadhaar(String number) {
    if (number.length == 12) {
      return '${number.substring(0, 4)} ${number.substring(4, 8)} ${number.substring(8)}';
    }
    return number;
  }

  /// Format PAN number
  static String panNumber(String pan) {
    return pan.toUpperCase();
  }

  /// Format IFSC code
  static String ifscCode(String ifsc) {
    return ifsc.toUpperCase();
  }

  /// Remove special characters from string
  static String digitsOnly(String text) {
    return text.replaceAll(RegExp(r'\D'), '');
  }

  /// Format win/loss ratio
  static String winLossRatio(int wins, int losses) {
    if (losses == 0) {
      return wins > 0 ? '${wins}:0' : '0:0';
    }
    return '$wins:$losses';
  }

  /// Format win percentage
  static String winPercentage(int wins, int totalGames) {
    if (totalGames == 0) return '0%';
    final percentage = (wins / totalGames) * 100;
    return '${percentage.toStringAsFixed(1)}%';
  }
}
