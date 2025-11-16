import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import 'custom_button.dart' as custom;

/// Empty state widget
class EmptyState extends StatelessWidget {
  final String title;
  final String message;
  final IconData? icon;
  final String? actionText;
  final VoidCallback? onAction;

  const EmptyState({
    super.key,
    required this.title,
    required this.message,
    this.icon,
    this.actionText,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon ?? Icons.inbox,
              size: 80,
              color: AppColors.textHint.withOpacity(0.5),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: AppTextStyles.heading2,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              message,
              style: AppTextStyles.body.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            if (actionText != null && onAction != null) ...[
              const SizedBox(height: 32),
              custom.CustomButton(
                text: actionText!,
                onPressed: onAction,
                isFullWidth: false,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// No games available state
class NoGamesAvailable extends StatelessWidget {
  const NoGamesAvailable({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      title: 'No Games Available',
      message: 'There are no games available at the moment.\nPlease check back later.',
      icon: Icons.games,
    );
  }
}

/// No transactions state
class NoTransactions extends StatelessWidget {
  const NoTransactions({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      title: 'No Transactions',
      message: 'You haven\'t made any transactions yet.\nStart playing to see your transaction history!',
      icon: Icons.receipt_long,
    );
  }
}

/// No game history state
class NoGameHistory extends StatelessWidget {
  const NoGameHistory({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      title: 'No Games Played',
      message: 'You haven\'t played any games yet.\nStart playing to build your gaming history!',
      icon: Icons.history,
    );
  }
}
