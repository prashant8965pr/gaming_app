import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import '../../bloc/token/token_bloc.dart';
import '../../bloc/token/token_event.dart';
import '../../bloc/token/token_state.dart';
import '../../../data/models/token_model.dart';

class TokenWalletScreen extends StatefulWidget {
  const TokenWalletScreen({Key? key}) : super(key: key);

  @override
  State<TokenWalletScreen> createState() => _TokenWalletScreenState();
}

class _TokenWalletScreenState extends State<TokenWalletScreen> {
  @override
  void initState() {
    super.initState();
    _loadBalance();
  }

  void _loadBalance() {
    context.read<TokenBloc>().add(const LoadTokenBalance(refresh: true));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Token Wallet'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.pushNamed(context, '/token-history');
            },
            tooltip: 'Transaction History',
          ),
        ],
      ),
      body: BlocConsumer<TokenBloc, TokenState>(
        listener: (context, state) {
          if (state is TokenError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          } else if (state is DailyBonusClaimed) {
            _showSuccessDialog(
              'Daily Bonus Claimed!',
              'You earned ${state.response.tokensEarned} tokens!\n'
                  'Current streak: ${state.response.currentStreak} days',
            );
            _loadBalance();
          } else if (state is AdRewardEarned) {
            _showSuccessDialog(
              'Ad Reward Earned!',
              'You earned ${state.response.tokensEarned} tokens!\n'
                  'Ads watched today: ${state.response.adsWatchedToday}/5',
            );
            _loadBalance();
          }
        },
        builder: (context, state) {
          if (state is TokenLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is TokenLoaded || state is DailyBonusClaimed || state is AdRewardEarned) {
            TokenWalletModel? wallet;

            if (state is TokenLoaded) {
              wallet = state.wallet;
            } else if (state is DailyBonusClaimed) {
              wallet = state.wallet;
            } else if (state is AdRewardEarned) {
              wallet = state.wallet;
            }

            if (wallet == null) {
              return const Center(child: Text('Failed to load wallet'));
            }

            return RefreshIndicator(
              onRefresh: () async {
                _loadBalance();
              },
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildBalanceCard(wallet),
                      const SizedBox(height: 24),
                      _buildStatsSection(wallet),
                      const SizedBox(height: 24),
                      _buildEarnSection(wallet),
                    ],
                  ),
                ),
              ),
            );
          }

          return const Center(child: Text('Failed to load token balance'));
        },
      ),
    );
  }

  Widget _buildBalanceCard(TokenWalletModel wallet) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.deepPurple, Colors.purple],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.purple.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.account_balance_wallet,
                  color: Colors.white, size: 32),
              SizedBox(width: 12),
              Text(
                'Token Balance',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 18,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            '${NumberFormat('#,###').format(wallet.balance)} Tokens',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsSection(TokenWalletModel wallet) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Statistics',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                icon: Icons.trending_up,
                label: 'Total Earned',
                value: NumberFormat('#,###').format(wallet.totalEarned),
                color: Colors.green,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                icon: Icons.trending_down,
                label: 'Total Spent',
                value: NumberFormat('#,###').format(wallet.totalSpent),
                color: Colors.orange,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildStreakCard(wallet),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStreakCard(TokenWalletModel wallet) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.amber, Colors.orange],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.local_fire_department, color: Colors.white, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Daily Login Streak',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
                Text(
                  '${wallet.dailyClaimStreak} Days',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Text(
                'Next Bonus',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                ),
              ),
              Text(
                '${wallet.nextDailyBonusAmount} tokens',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEarnSection(TokenWalletModel wallet) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Earn Tokens',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        _buildEarnCard(
          icon: Icons.card_giftcard,
          title: 'Daily Login Bonus',
          subtitle: 'Earn ${wallet.nextDailyBonusAmount} tokens',
          buttonText: wallet.canClaimDailyBonus ? 'Claim Now' : 'Claimed Today',
          buttonEnabled: wallet.canClaimDailyBonus,
          onTap: wallet.canClaimDailyBonus
              ? () => context.read<TokenBloc>().add(const ClaimDailyBonus())
              : null,
        ),
        const SizedBox(height: 12),
        _buildEarnCard(
          icon: Icons.play_circle_filled,
          title: 'Watch Ads',
          subtitle: 'Earn 50 tokens per ad (${wallet.adsRemaining}/5 remaining)',
          buttonText: wallet.canWatchAd ? 'Watch Ad' : 'Limit Reached',
          buttonEnabled: wallet.canWatchAd,
          onTap: wallet.canWatchAd
              ? () => context.read<TokenBloc>().add(const WatchAdForTokens())
              : null,
        ),
        const SizedBox(height: 12),
        _buildEarnCard(
          icon: Icons.emoji_events,
          title: 'Win Tournaments',
          subtitle: 'Compete and earn big prizes',
          buttonText: 'Browse',
          buttonEnabled: true,
          onTap: () => Navigator.pushNamed(context, '/tournaments'),
        ),
      ],
    );
  }

  Widget _buildEarnCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required String buttonText,
    required bool buttonEnabled,
    required VoidCallback? onTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              icon,
              color: Theme.of(context).primaryColor,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: buttonEnabled ? onTap : null,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            ),
            child: Text(buttonText),
          ),
        ],
      ),
    );
  }

  void _showSuccessDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.green, size: 32),
            const SizedBox(width: 12),
            Text(title),
          ],
        ),
        content: Text(message),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Awesome!'),
          ),
        ],
      ),
    );
  }
}
