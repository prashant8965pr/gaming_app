import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../widgets/empty_state.dart';

/// Game history screen showing past games
class GameHistoryScreen extends StatefulWidget {
  const GameHistoryScreen({super.key});

  @override
  State<GameHistoryScreen> createState() => _GameHistoryScreenState();
}

class _GameHistoryScreenState extends State<GameHistoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Game History'),
        backgroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Won'),
            Tab(text: 'Lost'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildGameList('all'),
          _buildGameList('won'),
          _buildGameList('lost'),
        ],
      ),
    );
  }

  Widget _buildGameList(String filter) {
    final games = _getFilteredGames(filter);

    if (games.isEmpty) {
      return EmptyState(
        title: 'No Games Found',
        message: filter == 'won'
            ? 'You haven\'t won any games yet'
            : filter == 'lost'
                ? 'No losses yet - keep it up!'
                : 'You haven\'t played any games yet',
        icon: Icons.sports_esports,
      );
    }

    return RefreshIndicator(
      onRefresh: _onRefresh,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: games.length,
        itemBuilder: (context, index) {
          final game = games[index];
          return _buildGameCard(game);
        },
      ),
    );
  }

  Widget _buildGameCard(GameHistoryModel game) {
    final isWon = game.result == 'won';
    final resultColor = isWon ? AppColors.success : AppColors.danger;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isWon
              ? AppColors.success.withOpacity(0.3)
              : AppColors.danger.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: resultColor.withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: resultColor.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    isWon ? Icons.emoji_events : Icons.close,
                    color: resultColor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        game.gameName,
                        style: AppTextStyles.bodyBold,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _formatDateTime(game.playedAt),
                        style: AppTextStyles.caption.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: resultColor,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        isWon ? 'WON' : 'LOST',
                        style: AppTextStyles.caption.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isWon
                          ? '+${Formatters.currency(game.winAmount ?? 0)}'
                          : '-${Formatters.currency(game.entryFee)}',
                      style: AppTextStyles.bodyBold.copyWith(
                        color: resultColor,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Details
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _buildDetailItem(
                        Icons.emoji_events_outlined,
                        'Position',
                        '${game.position}/${game.totalPlayers}',
                      ),
                    ),
                    Expanded(
                      child: _buildDetailItem(
                        Icons.currency_rupee,
                        'Entry Fee',
                        Formatters.currency(game.entryFee),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildDetailItem(
                        Icons.timer_outlined,
                        'Duration',
                        _formatDuration(game.duration),
                      ),
                    ),
                    Expanded(
                      child: _buildDetailItem(
                        Icons.stars_outlined,
                        'Points',
                        '${game.score}',
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // View Details Button
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: OutlinedButton(
              onPressed: () => _showGameDetails(game),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.primary,
                side: const BorderSide(color: AppColors.primary),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('View Details'),
                  const SizedBox(width: 8),
                  const Icon(Icons.arrow_forward_ios, size: 14),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailItem(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(
          icon,
          size: 18,
          color: AppColors.textSecondary,
        ),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
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
      ],
    );
  }

  void _showGameDetails(GameHistoryModel game) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.9,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) => Padding(
          padding: const EdgeInsets.all(24),
          child: ListView(
            controller: scrollController,
            children: [
              Text(
                'Game Details',
                style: AppTextStyles.heading2,
              ),
              const SizedBox(height: 24),

              // Game Info
              _buildDetailRow('Game', game.gameName),
              _buildDetailRow('Session ID', game.sessionId),
              _buildDetailRow('Played On', _formatDateTime(game.playedAt)),
              _buildDetailRow('Duration', _formatDuration(game.duration)),

              const Divider(height: 32),

              // Performance
              Text(
                'Performance',
                style: AppTextStyles.heading3,
              ),
              const SizedBox(height: 16),
              _buildDetailRow('Position', '${game.position}/${game.totalPlayers}'),
              _buildDetailRow('Score', '${game.score} points'),
              _buildDetailRow('Accuracy', '${(game.score / (game.totalPlayers * 10) * 100).toStringAsFixed(1)}%'),

              const Divider(height: 32),

              // Financial
              Text(
                'Financial Summary',
                style: AppTextStyles.heading3,
              ),
              const SizedBox(height: 16),
              _buildDetailRow('Entry Fee', Formatters.currency(game.entryFee)),
              _buildDetailRow(
                'Prize Pool',
                Formatters.currency(game.prizePool),
              ),
              if (game.result == 'won')
                _buildDetailRow(
                  'Winnings',
                  Formatters.currency(game.winAmount ?? 0),
                  valueColor: AppColors.success,
                ),
              _buildDetailRow(
                'Net Result',
                game.result == 'won'
                    ? '+${Formatters.currency((game.winAmount ?? 0) - game.entryFee)}'
                    : '-${Formatters.currency(game.entryFee)}',
                valueColor: game.result == 'won'
                    ? AppColors.success
                    : AppColors.danger,
              ),

              const SizedBox(height: 24),

              // Report Issue Button
              OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  _reportIssue(game);
                },
                icon: const Icon(Icons.report_problem),
                label: const Text('Report Issue'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.warning,
                  side: const BorderSide(color: AppColors.warning),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: AppTextStyles.body.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            value,
            style: AppTextStyles.bodyBold.copyWith(
              color: valueColor ?? AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return DateFormat('dd MMM yyyy, hh:mm a').format(dateTime);
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);

    if (hours > 0) {
      return '${hours}h ${minutes}m';
    } else {
      return '${minutes}m';
    }
  }

  List<GameHistoryModel> _getFilteredGames(String filter) {
    final allGames = _getMockGameHistory();

    if (filter == 'won') {
      return allGames.where((game) => game.result == 'won').toList();
    } else if (filter == 'lost') {
      return allGames.where((game) => game.result == 'lost').toList();
    }

    return allGames;
  }

  void _reportIssue(GameHistoryModel game) {
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

  Future<void> _onRefresh() async {
    // TODO: Reload game history
    await Future.delayed(const Duration(seconds: 1));
  }

  List<GameHistoryModel> _getMockGameHistory() {
    return [
      GameHistoryModel(
        id: '1',
        gameName: 'Ludo King',
        sessionId: 'LDO123456',
        entryFee: 100,
        prizePool: 400,
        result: 'won',
        winAmount: 200,
        position: 1,
        totalPlayers: 4,
        score: 450,
        duration: const Duration(minutes: 15),
        playedAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      GameHistoryModel(
        id: '2',
        gameName: 'Rummy',
        sessionId: 'RUM789012',
        entryFee: 500,
        prizePool: 2000,
        result: 'lost',
        winAmount: null,
        position: 3,
        totalPlayers: 4,
        score: 320,
        duration: const Duration(minutes: 25),
        playedAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
      GameHistoryModel(
        id: '3',
        gameName: 'Poker',
        sessionId: 'PKR345678',
        entryFee: 1000,
        prizePool: 5000,
        result: 'won',
        winAmount: 2500,
        position: 2,
        totalPlayers: 5,
        score: 880,
        duration: const Duration(minutes: 45),
        playedAt: DateTime.now().subtract(const Duration(days: 2)),
      ),
      GameHistoryModel(
        id: '4',
        gameName: 'Carrom',
        sessionId: 'CRM901234',
        entryFee: 50,
        prizePool: 200,
        result: 'lost',
        winAmount: null,
        position: 4,
        totalPlayers: 4,
        score: 180,
        duration: const Duration(minutes: 12),
        playedAt: DateTime.now().subtract(const Duration(days: 3)),
      ),
      GameHistoryModel(
        id: '5',
        gameName: 'Chess',
        sessionId: 'CHS567890',
        entryFee: 200,
        prizePool: 400,
        result: 'won',
        winAmount: 350,
        position: 1,
        totalPlayers: 2,
        score: 1000,
        duration: const Duration(minutes: 35),
        playedAt: DateTime.now().subtract(const Duration(days: 4)),
      ),
    ];
  }
}

/// Game History Model
class GameHistoryModel {
  final String id;
  final String gameName;
  final String sessionId;
  final double entryFee;
  final double prizePool;
  final String result; // 'won', 'lost'
  final double? winAmount;
  final int position;
  final int totalPlayers;
  final int score;
  final Duration duration;
  final DateTime playedAt;

  GameHistoryModel({
    required this.id,
    required this.gameName,
    required this.sessionId,
    required this.entryFee,
    required this.prizePool,
    required this.result,
    this.winAmount,
    required this.position,
    required this.totalPlayers,
    required this.score,
    required this.duration,
    required this.playedAt,
  });
}
