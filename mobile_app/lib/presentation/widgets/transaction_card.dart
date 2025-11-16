import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import '../../core/utils/formatters.dart';
import '../../data/models/wallet_model.dart';

/// Transaction card widget for displaying transaction information
class TransactionCard extends StatelessWidget {
  final TransactionModel transaction;
  final VoidCallback? onTap;

  const TransactionCard({
    super.key,
    required this.transaction,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            // Transaction icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _getTransactionColor().withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getTransactionIcon(),
                color: _getTransactionColor(),
                size: 24,
              ),
            ),

            const SizedBox(width: 12),

            // Transaction details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _getTransactionTitle(),
                    style: AppTextStyles.bodyMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    Formatters.dateTime(transaction.createdAt),
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  if (transaction.paymentMethod != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      transaction.paymentMethod!.toUpperCase(),
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textHint,
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Amount and status
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${transaction.type == 'deposit' ? '+' : '-'} ${Formatters.currency(transaction.amount)}',
                  style: AppTextStyles.bodyBold.copyWith(
                    color: transaction.type == 'deposit'
                        ? AppColors.success
                        : AppColors.error,
                  ),
                ),
                const SizedBox(height: 4),
                _buildStatusChip(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip() {
    Color color;
    String text;

    switch (transaction.status) {
      case 'completed':
        color = AppColors.success;
        text = 'Completed';
        break;
      case 'pending':
        color = AppColors.warning;
        text = 'Pending';
        break;
      case 'failed':
        color = AppColors.error;
        text = 'Failed';
        break;
      default:
        color = AppColors.textHint;
        text = transaction.status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: AppTextStyles.caption.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  IconData _getTransactionIcon() {
    switch (transaction.type) {
      case 'deposit':
        return Icons.add_circle;
      case 'withdrawal':
        return Icons.remove_circle;
      case 'game_entry':
        return Icons.sports_esports;
      case 'game_winning':
        return Icons.emoji_events;
      case 'refund':
        return Icons.refresh;
      case 'bonus':
        return Icons.card_giftcard;
      default:
        return Icons.account_balance_wallet;
    }
  }

  Color _getTransactionColor() {
    switch (transaction.type) {
      case 'deposit':
      case 'game_winning':
      case 'bonus':
        return AppColors.success;
      case 'withdrawal':
      case 'game_entry':
        return AppColors.error;
      case 'refund':
        return AppColors.warning;
      default:
        return AppColors.textSecondary;
    }
  }

  String _getTransactionTitle() {
    switch (transaction.type) {
      case 'deposit':
        return 'Money Added';
      case 'withdrawal':
        return 'Money Withdrawn';
      case 'game_entry':
        return 'Game Entry Fee';
      case 'game_winning':
        return 'Game Winnings';
      case 'refund':
        return 'Refund';
      case 'bonus':
        return 'Bonus Credit';
      default:
        return transaction.type.replaceAll('_', ' ').toUpperCase();
    }
  }
}
