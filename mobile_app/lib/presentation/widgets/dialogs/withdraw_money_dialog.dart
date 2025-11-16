import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../core/utils/validators.dart';
import '../../../data/models/wallet_model.dart';
import '../../bloc/wallet/wallet_bloc.dart';
import '../../bloc/wallet/wallet_event.dart';
import '../../bloc/wallet/wallet_state.dart';
import '../custom_button.dart' as custom;

/// Dialog for withdrawing money from wallet
class WithdrawMoneyDialog extends StatefulWidget {
  final WalletBalanceModel balance;

  const WithdrawMoneyDialog({
    super.key,
    required this.balance,
  });

  @override
  State<WithdrawMoneyDialog> createState() => _WithdrawMoneyDialogState();
}

class _WithdrawMoneyDialogState extends State<WithdrawMoneyDialog> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();

  String? _selectedBankAccountId;
  final List<BankAccount> _bankAccounts = []; // Will be loaded from user profile

  final double _processingFeePercentage = 2.0; // 2% processing fee
  final double _minWithdrawalAmount = 200;

  double get _withdrawableBalance => widget.balance.winningsBalance;

  double get _enteredAmount {
    final value = _amountController.text.trim();
    if (value.isEmpty) return 0;
    return double.tryParse(value) ?? 0;
  }

  double get _processingFee {
    return (_enteredAmount * _processingFeePercentage) / 100;
  }

  double get _finalAmount {
    return _enteredAmount - _processingFee;
  }

  @override
  void initState() {
    super.initState();
    _loadBankAccounts();
  }

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  void _loadBankAccounts() {
    // TODO: Load bank accounts from user profile
    // For now, using mock data
    _bankAccounts.addAll([
      BankAccount(
        id: '1',
        accountHolderName: 'John Doe',
        bankName: 'HDFC Bank',
        accountNumber: '****1234',
        ifscCode: 'HDFC0001234',
        isVerified: true,
      ),
    ]);

    if (_bankAccounts.isNotEmpty) {
      _selectedBankAccountId = _bankAccounts.first.id;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.success.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.arrow_upward,
                        color: AppColors.success,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Withdraw Money',
                            style: AppTextStyles.heading3,
                          ),
                          Text(
                            'Transfer to your bank account',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // Available Balance
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppColors.success.withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Available for Withdrawal',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            Formatters.currency(_withdrawableBalance),
                            style: AppTextStyles.heading2.copyWith(
                              color: AppColors.success,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.info.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.info_outline,
                              size: 16,
                              color: AppColors.info,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              'Winnings Only',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.info,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // Amount Input
                Text(
                  'Enter Amount',
                  style: AppTextStyles.bodyMedium,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _amountController,
                  keyboardType: TextInputType.number,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                  ],
                  decoration: InputDecoration(
                    hintText: 'Enter amount to withdraw',
                    prefixIcon: const Icon(Icons.currency_rupee),
                    suffixIcon: _withdrawableBalance > 0
                        ? TextButton(
                            onPressed: () {
                              _amountController.text =
                                  _withdrawableBalance.toStringAsFixed(0);
                              setState(() {});
                            },
                            child: Text(
                              'MAX',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          )
                        : null,
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter amount';
                    }
                    final amount = double.tryParse(value);
                    if (amount == null || amount < _minWithdrawalAmount) {
                      return 'Minimum withdrawal is ${Formatters.currency(_minWithdrawalAmount)}';
                    }
                    if (amount > _withdrawableBalance) {
                      return 'Insufficient balance';
                    }
                    return null;
                  },
                  onChanged: (value) {
                    setState(() {}); // Rebuild to show updated fees
                  },
                ),

                const SizedBox(height: 20),

                // Bank Account Selection
                Text(
                  'Select Bank Account',
                  style: AppTextStyles.bodyMedium,
                ),
                const SizedBox(height: 12),

                if (_bankAccounts.isEmpty)
                  _buildNoBankAccountCard()
                else
                  ..._bankAccounts.map((account) => _buildBankAccountCard(account)),

                const SizedBox(height: 20),

                // Fee Breakdown
                if (_enteredAmount > 0) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Withdrawal Amount',
                              style: AppTextStyles.body.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            Text(
                              Formatters.currency(_enteredAmount),
                              style: AppTextStyles.bodyMedium,
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Processing Fee ($_processingFeePercentage%)',
                              style: AppTextStyles.body.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            Text(
                              '- ${Formatters.currency(_processingFee)}',
                              style: AppTextStyles.bodyMedium.copyWith(
                                color: AppColors.danger,
                              ),
                            ),
                          ],
                        ),
                        const Divider(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'You will receive',
                              style: AppTextStyles.bodyBold,
                            ),
                            Text(
                              Formatters.currency(_finalAmount),
                              style: AppTextStyles.heading3.copyWith(
                                color: AppColors.success,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // Submit Button
                custom.CustomButton(
                  text: 'Withdraw Money',
                  onPressed: _bankAccounts.isEmpty ? null : _handleSubmit,
                  icon: Icons.send,
                  buttonStyle: custom.ButtonStyle.success,
                ),

                const SizedBox(height: 12),

                // Info Note
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.info.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.info_outline,
                        color: AppColors.info,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Withdrawal takes 1-3 business days',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.info,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Only winnings can be withdrawn. Bonus and deposit amounts cannot be withdrawn directly.',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBankAccountCard(BankAccount account) {
    final isSelected = _selectedBankAccountId == account.id;

    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedBankAccountId = account.id;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.success.withOpacity(0.1) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? AppColors.success : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.success
                    : AppColors.textSecondary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.account_balance,
                color: isSelected ? Colors.white : AppColors.textSecondary,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        account.bankName,
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: isSelected
                              ? AppColors.success
                              : AppColors.textPrimary,
                        ),
                      ),
                      if (account.isVerified) ...[
                        const SizedBox(width: 4),
                        const Icon(
                          Icons.verified,
                          size: 16,
                          color: AppColors.success,
                        ),
                      ],
                    ],
                  ),
                  Text(
                    '${account.accountHolderName} • ${account.accountNumber}',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              const Icon(
                Icons.check_circle,
                color: AppColors.success,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoBankAccountCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.warning.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.warning.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.account_balance,
            color: AppColors.warning,
            size: 40,
          ),
          const SizedBox(height: 12),
          Text(
            'No Bank Account Added',
            style: AppTextStyles.bodyBold,
          ),
          const SizedBox(height: 4),
          Text(
            'Please add a bank account to withdraw money',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _navigateToAddBankAccount,
            icon: const Icon(Icons.add),
            label: const Text('Add Bank Account'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.warning,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToAddBankAccount() {
    Navigator.pop(context);
    // TODO: Navigate to add bank account screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Add bank account feature coming soon!'),
      ),
    );
  }

  void _handleSubmit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedBankAccountId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a bank account'),
        ),
      );
      return;
    }

    final amount = double.parse(_amountController.text);

    // Show confirmation dialog
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Confirm Withdrawal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'You are withdrawing ${Formatters.currency(amount)} to your bank account.',
              style: AppTextStyles.body,
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildConfirmationRow('Amount:', Formatters.currency(amount)),
                  _buildConfirmationRow(
                    'Processing Fee:',
                    Formatters.currency(_processingFee),
                  ),
                  const Divider(),
                  _buildConfirmationRow(
                    'You will receive:',
                    Formatters.currency(_finalAmount),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Processing time: 1-3 business days',
              style: AppTextStyles.caption.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              _confirmWithdrawal(amount);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.success,
            ),
            child: const Text('Confirm'),
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmationRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            value,
            style: AppTextStyles.bodyMedium,
          ),
        ],
      ),
    );
  }

  void _confirmWithdrawal(double amount) {
    // Trigger withdraw money event
    context.read<WalletBloc>().add(
          WithdrawMoneyEvent(
            amount: amount,
            bankAccountId: _selectedBankAccountId!,
          ),
        );

    Navigator.pop(context);

    // Show processing message
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Withdrawal of ${Formatters.currency(_finalAmount)} initiated successfully',
        ),
        backgroundColor: AppColors.success,
        duration: const Duration(seconds: 3),
      ),
    );
  }
}

/// Bank account model (temporary - should be in data/models)
class BankAccount {
  final String id;
  final String accountHolderName;
  final String bankName;
  final String accountNumber;
  final String ifscCode;
  final bool isVerified;

  BankAccount({
    required this.id,
    required this.accountHolderName,
    required this.bankName,
    required this.accountNumber,
    required this.ifscCode,
    required this.isVerified,
  });
}
