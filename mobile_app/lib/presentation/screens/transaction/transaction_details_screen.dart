import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/wallet_model.dart';

/// Transaction details screen
class TransactionDetailsScreen extends StatelessWidget {
  final String transactionId;

  const TransactionDetailsScreen({
    super.key,
    required this.transactionId,
  });

  @override
  Widget build(BuildContext context) {
    // TODO: Load transaction details from BLoC
    final transaction = _getMockTransaction();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Transaction Details'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _shareTransaction(transaction),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Status Card
            _buildStatusCard(transaction),

            // Transaction Details
            _buildDetailsSection(transaction),

            // Payment Details
            if (transaction.paymentMethod != null)
              _buildPaymentDetailsSection(transaction),

            // Additional Info
            _buildAdditionalInfoSection(transaction),

            // Actions
            _buildActionsSection(context, transaction),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard(TransactionModel transaction) {
    final isCredit = ['deposit', 'game_winning', 'bonus', 'refund']
        .contains(transaction.type);
    final statusColor = _getStatusColor(transaction.status);

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isCredit
              ? [AppColors.success, AppColors.success.withOpacity(0.8)]
              : [AppColors.primary, AppColors.primary.withOpacity(0.8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: (isCredit ? AppColors.success : AppColors.primary)
                .withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            isCredit ? Icons.arrow_downward : Icons.arrow_upward,
            color: Colors.white,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            isCredit ? '+${Formatters.currency(transaction.amount)}' : '${Formatters.currency(transaction.amount)}',
            style: AppTextStyles.heading1.copyWith(
              color: Colors.white,
              fontSize: 36,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 6,
            ),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              _getTransactionTypeLabel(transaction.type),
              style: AppTextStyles.body.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 8,
            ),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: Colors.white.withOpacity(0.5),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _getStatusIcon(transaction.status),
                  color: Colors.white,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  transaction.status.toUpperCase(),
                  style: AppTextStyles.bodyBold.copyWith(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailsSection(TransactionModel transaction) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Transaction Details',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          _buildDetailRow(
            'Transaction ID',
            transaction.id.substring(0, 16),
            canCopy: true,
            copyValue: transaction.id,
          ),
          _buildDivider(),
          _buildDetailRow(
            'Date & Time',
            DateFormat('dd MMM yyyy, hh:mm a').format(transaction.createdAt),
          ),
          _buildDivider(),
          _buildDetailRow(
            'Type',
            _getTransactionTypeLabel(transaction.type),
          ),
          if (transaction.description != null) ...[
            _buildDivider(),
            _buildDetailRow(
              'Description',
              transaction.description!,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPaymentDetailsSection(TransactionModel transaction) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Payment Details',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          _buildDetailRow(
            'Payment Method',
            _getPaymentMethodLabel(transaction.paymentMethod ?? ''),
          ),
          if (transaction.utrNumber != null) ...[
            _buildDivider(),
            _buildDetailRow(
              'UTR Number',
              transaction.utrNumber!,
              canCopy: true,
              copyValue: transaction.utrNumber!,
            ),
          ],
          if (transaction.processingFee != null && transaction.processingFee! > 0) ...[
            _buildDivider(),
            _buildDetailRow(
              'Processing Fee',
              Formatters.currency(transaction.processingFee!),
            ),
          ],
          if (transaction.closingBalance != null) ...[
            _buildDivider(),
            _buildDetailRow(
              'Closing Balance',
              Formatters.currency(transaction.closingBalance!),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAdditionalInfoSection(TransactionModel transaction) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Additional Information',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          if (transaction.gameId != null)
            _buildDetailRow(
              'Game ID',
              transaction.gameId!,
            ),
          if (transaction.sessionId != null) ...[
            _buildDivider(),
            _buildDetailRow(
              'Session ID',
              transaction.sessionId!,
            ),
          ],
          if (transaction.metadata != null && transaction.metadata!.isNotEmpty) ...[
            _buildDivider(),
            ...transaction.metadata!.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _buildDetailRow(
                  entry.key.replaceAll('_', ' ').toUpperCase(),
                  entry.value.toString(),
                ),
              );
            }).toList(),
          ],
        ],
      ),
    );
  }

  Widget _buildActionsSection(BuildContext context, TransactionModel transaction) {
    return Container(
      margin: const EdgeInsets.all(16),
      child: Column(
        children: [
          if (transaction.status == 'failed')
            _buildActionButton(
              'Retry Transaction',
              Icons.refresh,
              AppColors.primary,
              () => _retryTransaction(context, transaction),
            ),
          if (transaction.status == 'pending' && transaction.type == 'withdrawal')
            _buildActionButton(
              'Cancel Withdrawal',
              Icons.cancel,
              AppColors.danger,
              () => _cancelTransaction(context, transaction),
            ),
          _buildActionButton(
            'Download Receipt',
            Icons.download,
            AppColors.success,
            () => _downloadReceipt(context, transaction),
          ),
          const SizedBox(height: 12),
          _buildActionButton(
            'Report Issue',
            Icons.report_problem,
            AppColors.warning,
            () => _reportIssue(context, transaction),
          ),
          const SizedBox(height: 12),
          _buildActionButton(
            'Contact Support',
            Icons.support_agent,
            AppColors.info,
            () => _contactSupport(context, transaction),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(
    String label,
    String value, {
    bool canCopy = false,
    String? copyValue,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: AppTextStyles.body.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    value,
                    style: AppTextStyles.bodyBold,
                    textAlign: TextAlign.right,
                  ),
                ),
                if (canCopy) ...[
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: () {
                      Clipboard.setData(
                        ClipboardData(text: copyValue ?? value),
                      );
                      // Show snackbar (would need BuildContext)
                    },
                    child: const Icon(
                      Icons.copy,
                      size: 16,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(height: 24);
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onPressed,
  ) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 20),
        label: Text(label),
        style: OutlinedButton.styleFrom(
          foregroundColor: color,
          side: BorderSide(color: color),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return AppColors.success;
      case 'pending':
        return AppColors.warning;
      case 'failed':
        return AppColors.danger;
      case 'cancelled':
        return AppColors.textSecondary;
      default:
        return AppColors.info;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return Icons.check_circle;
      case 'pending':
        return Icons.access_time;
      case 'failed':
        return Icons.error;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.info;
    }
  }

  String _getTransactionTypeLabel(String type) {
    switch (type) {
      case 'deposit':
        return 'Money Added';
      case 'withdrawal':
        return 'Withdrawal';
      case 'game_entry':
        return 'Game Entry Fee';
      case 'game_winning':
        return 'Game Winning';
      case 'bonus':
        return 'Bonus Credit';
      case 'refund':
        return 'Refund';
      case 'referral_bonus':
        return 'Referral Bonus';
      default:
        return type.replaceAll('_', ' ').toUpperCase();
    }
  }

  String _getPaymentMethodLabel(String method) {
    switch (method.toLowerCase()) {
      case 'upi':
        return 'UPI Payment';
      case 'card':
        return 'Debit/Credit Card';
      case 'netbanking':
        return 'Net Banking';
      case 'wallet':
        return 'Wallet Transfer';
      default:
        return method.toUpperCase();
    }
  }

  void _shareTransaction(TransactionModel transaction) {
    // TODO: Implement share functionality
  }

  void _retryTransaction(BuildContext context, TransactionModel transaction) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Retry Transaction'),
        content: const Text(
          'Would you like to retry this transaction?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement retry logic
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Retrying transaction...'),
                ),
              );
            },
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  void _cancelTransaction(BuildContext context, TransactionModel transaction) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Transaction'),
        content: const Text(
          'Are you sure you want to cancel this transaction?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('No'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement cancel logic
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Transaction cancelled'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.danger,
            ),
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }

  void _downloadReceipt(BuildContext context, TransactionModel transaction) {
    // TODO: Implement download receipt
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Downloading receipt...'),
      ),
    );
  }

  void _reportIssue(BuildContext context, TransactionModel transaction) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Report Issue',
                style: AppTextStyles.heading3,
              ),
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(
                  hintText: 'Describe the issue...',
                  border: OutlineInputBorder(),
                ),
                maxLines: 4,
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Issue reported successfully'),
                        backgroundColor: AppColors.success,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('Submit Report'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _contactSupport(BuildContext context, TransactionModel transaction) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Contact Support',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.email, color: AppColors.primary),
              title: const Text('Email Support'),
              subtitle: const Text('support@gameapp.com'),
              onTap: () {
                // TODO: Open email client
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.phone, color: AppColors.success),
              title: const Text('Call Support'),
              subtitle: const Text('+91 1800-XXX-XXXX'),
              onTap: () {
                // TODO: Open dialer
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.chat, color: AppColors.info),
              title: const Text('Live Chat'),
              subtitle: const Text('Available 24/7'),
              onTap: () {
                // TODO: Open live chat
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  // Mock data
  TransactionModel _getMockTransaction() {
    return TransactionModel(
      id: 'TXN${DateTime.now().millisecondsSinceEpoch}',
      userId: 'user123',
      type: 'deposit',
      amount: 1000.0,
      status: 'completed',
      description: 'Money added to wallet via UPI',
      paymentMethod: 'upi',
      utrNumber: 'UTR123456789012',
      processingFee: 0.0,
      closingBalance: 5500.0,
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      updatedAt: DateTime.now().subtract(const Duration(hours: 2)),
      metadata: {
        'payment_app': 'Google Pay',
        'transaction_note': 'Quick deposit',
      },
    );
  }
}
