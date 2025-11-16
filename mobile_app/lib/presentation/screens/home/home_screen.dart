import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../bloc/game/game_bloc.dart';
import '../../bloc/game/game_event.dart';
import '../../bloc/game/game_state.dart';
import '../../bloc/wallet/wallet_bloc.dart';
import '../../bloc/wallet/wallet_event.dart';
import '../../bloc/wallet/wallet_state.dart';
import '../../widgets/game_card.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/empty_state.dart';
import '../../../data/models/game_model.dart';
import '../../../core/utils/formatters.dart';
import '../../widgets/dialogs/add_money_dialog.dart';

/// Home screen displaying game catalog and wallet balance
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _selectedCategory = 'all';

  @override
  void initState() {
    super.initState();
    // Load games and wallet balance
    context.read<GameBloc>().add(const LoadGamesEvent());
    context.read<WalletBloc>().add(const LoadWalletBalanceEvent());
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
              _buildWalletBalance(),

              // Category Filters
              _buildCategoryFilters(),

              // Games List
              _buildGamesList(),
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
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Welcome Back!',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            'Play & Win',
            style: AppTextStyles.heading2,
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.notifications_outlined),
          onPressed: () {
            // TODO: Navigate to notifications
          },
        ),
      ],
    );
  }

  Widget _buildWalletBalance() {
    return SliverToBoxAdapter(
      child: BlocBuilder<WalletBloc, WalletState>(
        builder: (context, state) {
          if (state is WalletBalanceLoaded) {
            return Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Total Balance',
                          style: AppTextStyles.caption.copyWith(
                            color: Colors.white.withOpacity(0.8),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          Formatters.currency(state.balance.totalBalance),
                          style: AppTextStyles.heading1.copyWith(
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            _buildBalanceChip(
                              'Cash',
                              state.balance.cashBalance,
                            ),
                            const SizedBox(width: 8),
                            _buildBalanceChip(
                              'Bonus',
                              state.balance.bonusBalance,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (context) => const AddMoneyDialog(),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('Add Money'),
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

  Widget _buildBalanceChip(String label, double amount) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        '$label: ${Formatters.currency(amount)}',
        style: AppTextStyles.caption.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildCategoryFilters() {
    final categories = [
      {'id': 'all', 'name': 'All Games', 'icon': Icons.apps},
      {'id': 'card', 'name': 'Card', 'icon': Icons.style},
      {'id': 'board', 'name': 'Board', 'icon': Icons.dashboard},
      {'id': 'sports', 'name': 'Sports', 'icon': Icons.sports_cricket},
      {'id': 'quiz', 'name': 'Quiz', 'icon': Icons.quiz},
    ];

    return SliverToBoxAdapter(
      child: Container(
        height: 100,
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12),
          itemCount: categories.length,
          itemBuilder: (context, index) {
            final category = categories[index];
            final isSelected = _selectedCategory == category['id'];

            return GestureDetector(
              onTap: () {
                setState(() {
                  _selectedCategory = category['id'] as String;
                });
              },
              child: Container(
                width: 80,
                margin: const EdgeInsets.symmetric(horizontal: 4),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primary : Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isSelected ? AppColors.primary : Colors.grey.shade300,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      category['icon'] as IconData,
                      color: isSelected ? Colors.white : AppColors.textSecondary,
                      size: 28,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      category['name'] as String,
                      style: AppTextStyles.caption.copyWith(
                        color: isSelected ? Colors.white : AppColors.textSecondary,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildGamesList() {
    return BlocBuilder<GameBloc, GameState>(
      builder: (context, state) {
        if (state is GameLoading) {
          return const SliverFillRemaining(
            child: ShimmerList(itemCount: 3, itemHeight: 200),
          );
        }

        if (state is GameError) {
          return SliverFillRemaining(
            child: ErrorDisplay(
              message: state.message,
              onRetry: () {
                context.read<GameBloc>().add(const LoadGamesEvent());
              },
            ),
          );
        }

        if (state is GamesLoaded) {
          if (state.games.isEmpty) {
            return const SliverFillRemaining(
              child: NoGamesAvailable(),
            );
          }

          // Filter games by category
          final filteredGames = _filterGames(state.games);

          if (filteredGames.isEmpty) {
            return SliverFillRemaining(
              child: EmptyState(
                title: 'No Games Found',
                message: 'No games available in this category.',
                icon: Icons.search_off,
                actionText: 'View All Games',
                onAction: () {
                  setState(() {
                    _selectedCategory = 'all';
                  });
                },
              ),
            );
          }

          return SliverPadding(
            padding: const EdgeInsets.all(16),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final game = filteredGames[index];
                  return GameCard(
                    game: game,
                    onTap: () {
                      // TODO: Navigate to game details
                    },
                  );
                },
                childCount: filteredGames.length,
              ),
            ),
          );
        }

        return const SliverFillRemaining(
          child: Center(child: Text('Load games to get started')),
        );
      },
    );
  }

  List<GameModel> _filterGames(List<GameModel> games) {
    if (_selectedCategory == 'all') {
      return games;
    }
    return games.where((game) => game.gameType == _selectedCategory).toList();
  }

  Future<void> _onRefresh() async {
    context.read<GameBloc>().add(const LoadGamesEvent());
    context.read<WalletBloc>().add(const LoadWalletBalanceEvent(forceRefresh: true));
  }
}
