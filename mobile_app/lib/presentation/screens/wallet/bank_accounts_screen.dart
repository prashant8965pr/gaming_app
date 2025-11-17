import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/validators.dart';
import '../../widgets/custom_button.dart' as custom;
import '../../widgets/empty_state.dart';

/// Bank accounts management screen
class BankAccountsScreen extends StatefulWidget {
  const BankAccountsScreen({super.key});

  @override
  State<BankAccountsScreen> createState() => _BankAccountsScreenState();
}

class _BankAccountsScreenState extends State<BankAccountsScreen> {
  List<BankAccountModel> _bankAccounts = [];

  @override
  void initState() {
    super.initState();
    _loadBankAccounts();
  }

  void _loadBankAccounts() {
    // TODO: Load from BLoC
    setState(() {
      _bankAccounts = _getMockBankAccounts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Bank Accounts'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: _bankAccounts.isEmpty
          ? EmptyState(
              title: 'No Bank Accounts',
              message: 'Add a bank account to withdraw your winnings',
              icon: Icons.account_balance,
              actionText: 'Add Bank Account',
              onAction: _showAddBankAccountDialog,
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Info Card
                _buildInfoCard(),

                const SizedBox(height: 16),

                // Bank Accounts List
                ..._bankAccounts.map((account) => _buildBankAccountCard(account)),

                const SizedBox(height: 16),

                // Add Bank Account Button
                custom.CustomButton(
                  text: 'Add New Bank Account',
                  onPressed: _showAddBankAccountDialog,
                  icon: Icons.add,
                  buttonStyle: custom.ButtonStyle.outline,
                ),
              ],
            ),
    );
  }

  Widget _buildInfoCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.info.withOpacity(0.3),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(
            Icons.info_outline,
            color: AppColors.info,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Withdraw to your bank account',
                  style: AppTextStyles.bodyBold.copyWith(
                    color: AppColors.info,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Add your bank account details to withdraw your winnings. All accounts are verified for security.',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBankAccountCard(BankAccountModel account) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: account.isPrimary
              ? AppColors.primary.withOpacity(0.3)
              : Colors.grey.shade200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.account_balance,
                  color: AppColors.primary,
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
                          style: AppTextStyles.bodyBold,
                        ),
                        if (account.isPrimary) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              'PRIMARY',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.bold,
                                fontSize: 10,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      account.accountHolderName,
                      style: AppTextStyles.body.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              PopupMenuButton<String>(
                onSelected: (value) {
                  if (value == 'set_primary') {
                    _setPrimaryAccount(account);
                  } else if (value == 'delete') {
                    _confirmDeleteAccount(account);
                  }
                },
                itemBuilder: (context) => [
                  if (!account.isPrimary)
                    const PopupMenuItem(
                      value: 'set_primary',
                      child: Row(
                        children: [
                          Icon(Icons.star, size: 20),
                          SizedBox(width: 8),
                          Text('Set as Primary'),
                        ],
                      ),
                    ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: Row(
                      children: [
                        Icon(Icons.delete, size: 20, color: AppColors.danger),
                        SizedBox(width: 8),
                        Text('Delete', style: TextStyle(color: AppColors.danger)),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildAccountDetail(
                  'Account Number',
                  account.accountNumber,
                ),
              ),
              Expanded(
                child: _buildAccountDetail(
                  'IFSC Code',
                  account.ifscCode,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Icon(
                account.isVerified ? Icons.verified : Icons.pending,
                size: 16,
                color: account.isVerified ? AppColors.success : AppColors.warning,
              ),
              const SizedBox(width: 4),
              Text(
                account.isVerified ? 'Verified' : 'Pending Verification',
                style: AppTextStyles.caption.copyWith(
                  color: account.isVerified
                      ? AppColors.success
                      : AppColors.warning,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAccountDetail(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTextStyles.bodyMedium,
        ),
      ],
    );
  }

  void _showAddBankAccountDialog() {
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
        child: const AddBankAccountForm(),
      ),
    );
  }

  void _setPrimaryAccount(BankAccountModel account) {
    setState(() {
      for (var acc in _bankAccounts) {
        acc.isPrimary = false;
      }
      account.isPrimary = true;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${account.bankName} set as primary account'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  void _confirmDeleteAccount(BankAccountModel account) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Bank Account'),
        content: Text(
          'Are you sure you want to delete ${account.bankName} account?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _deleteAccount(account);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.danger,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _deleteAccount(BankAccountModel account) {
    setState(() {
      _bankAccounts.remove(account);
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Bank account deleted'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  List<BankAccountModel> _getMockBankAccounts() {
    return [
      BankAccountModel(
        id: '1',
        accountHolderName: 'John Doe',
        bankName: 'HDFC Bank',
        accountNumber: '****1234',
        ifscCode: 'HDFC0001234',
        isVerified: true,
        isPrimary: true,
      ),
      BankAccountModel(
        id: '2',
        accountHolderName: 'John Doe',
        bankName: 'ICICI Bank',
        accountNumber: '****5678',
        ifscCode: 'ICIC0005678',
        isVerified: true,
        isPrimary: false,
      ),
    ];
  }
}

/// Add bank account form
class AddBankAccountForm extends StatefulWidget {
  const AddBankAccountForm({super.key});

  @override
  State<AddBankAccountForm> createState() => _AddBankAccountFormState();
}

class _AddBankAccountFormState extends State<AddBankAccountForm> {
  final _formKey = GlobalKey<FormState>();
  final _accountHolderNameController = TextEditingController();
  final _accountNumberController = TextEditingController();
  final _confirmAccountNumberController = TextEditingController();
  final _ifscCodeController = TextEditingController();
  final _bankNameController = TextEditingController();

  bool _isLoading = false;

  @override
  void dispose() {
    _accountHolderNameController.dispose();
    _accountNumberController.dispose();
    _confirmAccountNumberController.dispose();
    _ifscCodeController.dispose();
    _bankNameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Add Bank Account',
                style: AppTextStyles.heading2,
              ),
              const SizedBox(height: 24),

              // Account Holder Name
              TextFormField(
                controller: _accountHolderNameController,
                decoration: const InputDecoration(
                  labelText: 'Account Holder Name',
                  hintText: 'Enter account holder name',
                  prefixIcon: Icon(Icons.person),
                ),
                textCapitalization: TextCapitalization.words,
                validator: Validators.required,
              ),

              const SizedBox(height: 16),

              // Account Number
              TextFormField(
                controller: _accountNumberController,
                decoration: const InputDecoration(
                  labelText: 'Account Number',
                  hintText: 'Enter account number',
                  prefixIcon: Icon(Icons.numbers),
                ),
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(18),
                ],
                validator: Validators.required,
              ),

              const SizedBox(height: 16),

              // Confirm Account Number
              TextFormField(
                controller: _confirmAccountNumberController,
                decoration: const InputDecoration(
                  labelText: 'Confirm Account Number',
                  hintText: 'Re-enter account number',
                  prefixIcon: Icon(Icons.numbers),
                ),
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(18),
                ],
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please confirm account number';
                  }
                  if (value != _accountNumberController.text) {
                    return 'Account numbers do not match';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 16),

              // IFSC Code
              TextFormField(
                controller: _ifscCodeController,
                decoration: const InputDecoration(
                  labelText: 'IFSC Code',
                  hintText: 'Enter IFSC code',
                  prefixIcon: Icon(Icons.code),
                ),
                textCapitalization: TextCapitalization.characters,
                inputFormatters: [
                  LengthLimitingTextInputFormatter(11),
                ],
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter IFSC code';
                  }
                  if (value.length != 11) {
                    return 'IFSC code must be 11 characters';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 16),

              // Bank Name
              TextFormField(
                controller: _bankNameController,
                decoration: const InputDecoration(
                  labelText: 'Bank Name',
                  hintText: 'Enter bank name',
                  prefixIcon: Icon(Icons.account_balance),
                ),
                textCapitalization: TextCapitalization.words,
                validator: Validators.required,
              ),

              const SizedBox(height: 24),

              // Note
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.warning_amber,
                      color: AppColors.warning,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Ensure all details are correct. Incorrect details may cause withdrawal failures.',
                        style: AppTextStyles.caption.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Submit Button
              custom.CustomButton(
                text: 'Add Bank Account',
                onPressed: _handleSubmit,
                icon: Icons.add,
                buttonStyle: custom.ButtonStyle.primary,
                isLoading: _isLoading,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _handleSubmit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // TODO: Add bank account via BLoC
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bank account added successfully. Verification pending.'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    });
  }
}

/// Bank Account Model (temporary - should be in data/models)
class BankAccountModel {
  final String id;
  final String accountHolderName;
  final String bankName;
  final String accountNumber;
  final String ifscCode;
  final bool isVerified;
  bool isPrimary;

  BankAccountModel({
    required this.id,
    required this.accountHolderName,
    required this.bankName,
    required this.accountNumber,
    required this.ifscCode,
    required this.isVerified,
    required this.isPrimary,
  });
}
