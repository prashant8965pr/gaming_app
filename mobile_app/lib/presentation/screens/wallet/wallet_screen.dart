import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../bloc/wallet/wallet_bloc.dart';
import '../../bloc/wallet/wallet_event.dart';
import '../../bloc/wallet/wallet_state.dart';
import '../../widgets/transaction_card.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/custom_button.dart' as custom;

/// Wallet screen displaying balance and transactions
class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadData() {
    context.read<WalletBloc>().add(const LoadWalletBalanceEvent());
    context.read<WalletBloc>().add(const LoadTransactionsEvent(limit: 50));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _onRefresh,
          child: CustomScrollView(
            slivers: [
              // App Bar
              _buildAppBar(),

              // Wallet Balance Card
              _buildBalanceCard(),

              // Quick Actions
              _buildQuickActions(),

              // Tabs and Transactions
              _buildTabBar(),
              _buildTransactionsList(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      floating: true,
      backgroundColor: Colors.white,
      elevation: 0,
      title: const Text('My Wallet'),
      actions: [
        IconButton(
          icon: const Icon(Icons.history),
          onPressed: () {
            // TODO: Navigate to full transaction history
          },
        ),
      ],
    );
  }

  Widget _buildBalanceCard() {
    return SliverToBoxAdapter(
      child: BlocBuilder<WalletBloc, WalletState>(
        builder: (context, state) {
          if (state is WalletLoading) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: ShimmerCard(height: 180),
            );
          }

          if (state is WalletBalanceLoaded) {
            final balance = state.balance;
            return Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Total Balance',
                    style: AppTextStyles.body.copyWith(
                      color: Colors.white.withOpacity(0.9),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    Formatters.currency(balance.totalBalance),
                    style: AppTextStyles.heading1.copyWith(
                      color: Colors.white,
                      fontSize: 36,
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Divider(color: Colors.white24),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildBalanceItem(
                        'Cash',
                        balance.cashBalance,
                        Icons.account_balance_wallet,
                      ),
                      Container(
                        width: 1,
                        height: 40,
                        color: Colors.white24,
                      ),
                      _buildBalanceItem(
                        'Bonus',
                        balance.bonusBalance,
                        Icons.card_giftcard,
                      ),
                      Container(
                        width: 1,
                        height: 40,
                        color: Colors.white24,
                      ),
                      _buildBalanceItem(
                        'Winnings',
                        balance.winningsBalance,
                        Icons.emoji_events,
                      ),
                    ],
                  ),
                ],
              ),
            );
          }

          return const SizedBox.shrink();
        },
      ),
    );
  }

  Widget _buildBalanceItem(String label, double amount, IconData icon) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, color: Colors.white.withOpacity(0.8), size: 20),
          const SizedBox(height: 8),
          Text(
            label,
            style: AppTextStyles.caption.copyWith(
              color: Colors.white.withOpacity(0.8),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            Formatters.currency(amount),
            style: AppTextStyles.bodyBold.copyWith(
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Row(
          children: [
            Expanded(
              child: custom.CustomButton(
                text: 'Add Money',
                onPressed: _showAddMoneyDialog,
                icon: Icons.add,
                buttonStyle: custom.ButtonStyle.primary,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: custom.CustomButton(
                text: 'Withdraw',
                onPressed: _showWithdrawDialog,
                icon: Icons.arrow_upward,
                buttonStyle: custom.ButtonStyle.outline,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBar() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
        ),
        child: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          indicatorWeight: 3,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Credits'),
            Tab(text: 'Debits'),
          ],
        ),
      ),
    );
  }

  Widget _buildTransactionsList() {
    return BlocBuilder<WalletBloc, WalletState>(
      builder: (context, state) {
        if (state is WalletLoading) {
          return const SliverFillRemaining(
            child: ShimmerList(itemCount: 5, itemHeight: 80),
          );
        }

        if (state is WalletError) {
          return SliverFillRemaining(
            child: ErrorDisplay(
              message: state.message,
              onRetry: () {
                context.read<WalletBloc>().add(const LoadTransactionsEvent());
              },
            ),
          );
        }

        if (state is TransactionsLoaded) {
          if (state.transactions.isEmpty) {
            return const SliverFillRemaining(
              child: NoTransactions(),
            );
          }

          // Filter by tab
          final filteredTransactions = _filterTransactions(state.transactions);

          if (filteredTransactions.isEmpty) {
            return const SliverFillRemaining(
              child: EmptyState(
                title: 'No Transactions',
                message: 'No transactions found in this category.',
                icon: Icons.receipt_long,
              ),
            );
          }

          return SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final transaction = filteredTransactions[index];
                  return TransactionCard(
                    transaction: transaction,
                    onTap: () {
                      _showTransactionDetails(transaction.id);
                    },
                  );
                },
                childCount: filteredTransactions.length,
              ),
            ),
          );
        }

        return const SliverFillRemaining(
          child: Center(child: Text('Load transactions')),
        );
      },
    );
  }

  List _filterTransactions(List transactions) {
    final currentTab = _tabController.index;
    if (currentTab == 0) return transactions; // All
    if (currentTab == 1) {
      // Credits
      return transactions
          .where((t) => ['deposit', 'game_winning', 'bonus', 'refund']
              .contains(t.type))
          .toList();
    }
    // Debits
    return transactions
        .where((t) => ['withdrawal', 'game_entry'].contains(t.type))
        .toList();
  }

  void _showAddMoneyDialog() {
    // TODO: Show add money dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Add money feature coming soon!')),
    );
  }

  void _showWithdrawDialog() {
    // TODO: Show withdraw dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Withdraw feature coming soon!')),
    );
  }

  void _showTransactionDetails(String transactionId) {
    // TODO: Navigate to transaction details
  }

  Future<void> _onRefresh() async {
    context.read<WalletBloc>().add(const LoadWalletBalanceEvent(forceRefresh: true));
    context.read<WalletBloc>().add(const LoadTransactionsEvent(limit: 50));
  }
}
