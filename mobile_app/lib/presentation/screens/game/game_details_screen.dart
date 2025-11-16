import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../bloc/game/game_bloc.dart';
import '../../bloc/game/game_event.dart';
import '../../bloc/game/game_state.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/custom_button.dart' as custom;
import '../../../data/models/game_model.dart';

/// Game details screen showing game info and active sessions
class GameDetailsScreen extends StatefulWidget {
  final String gameId;

  const GameDetailsScreen({
    super.key,
    required this.gameId,
  });

  @override
  State<GameDetailsScreen> createState() => _GameDetailsScreenState();
}

class _GameDetailsScreenState extends State<GameDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadData() {
    context.read<GameBloc>().add(LoadGameDetailsEvent(gameId: widget.gameId));
    context.read<GameBloc>().add(LoadActiveSessionsEvent(gameId: widget.gameId));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: BlocBuilder<GameBloc, GameState>(
        builder: (context, state) {
          if (state is GameLoading) {
            return const LoadingIndicator(message: 'Loading game details...');
          }

          if (state is GameError) {
            return ErrorDisplay(
              message: state.message,
              onRetry: _loadData,
            );
          }

          if (state is GameDetailsLoaded) {
            return _buildGameDetails(state.game);
          }

          return const Center(child: Text('Unable to load game details'));
        },
      ),
    );
  }

  Widget _buildGameDetails(GameModel game) {
    return CustomScrollView(
      slivers: [
        // App Bar with Game Image
        _buildAppBar(game),

        // Game Info Card
        _buildGameInfo(game),

        // Tab Bar
        _buildTabBar(),

        // Tab Content
        _buildTabContent(game),
      ],
    );
  }

  Widget _buildAppBar(GameModel game) {
    return SliverAppBar(
      expandedHeight: 200,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Text(
          game.name,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            shadows: [
              Shadow(
                color: Colors.black54,
                blurRadius: 4,
                offset: Offset(0, 2),
              ),
            ],
          ),
        ),
        background: Stack(
          fit: StackFit.expand,
          children: [
            game.thumbnailUrl != null
                ? CachedNetworkImage(
                    imageUrl: game.thumbnailUrl!,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(
                      color: Colors.grey.shade300,
                    ),
                    errorWidget: (context, url, error) => Container(
                      color: Colors.grey.shade300,
                      child: const Icon(Icons.games, size: 80),
                    ),
                  )
                : Container(
                    color: Colors.grey.shade300,
                    child: const Icon(Icons.games, size: 80),
                  ),
            // Gradient overlay
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.7),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGameInfo(GameModel game) {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Description
            Text(
              game.description,
              style: AppTextStyles.body,
            ),
            const SizedBox(height: 20),

            // Game Stats
            Row(
              children: [
                Expanded(
                  child: _buildStatChip(
                    icon: Icons.people,
                    label: 'Players',
                    value: '${game.minPlayers}-${game.maxPlayers}',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatChip(
                    icon: Icons.currency_rupee,
                    label: 'Entry Fee',
                    value: Formatters.currency(game.minEntryFee),
                  ),
                ),
              ],
            ),

            if (game.activePlayers != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.person,
                      color: AppColors.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${game.activePlayers} players online',
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: AppColors.primary, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: AppTextStyles.bodyBold,
          ),
          Text(
            label,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return SliverToBoxAdapter(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16),
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
            Tab(text: 'Active Sessions'),
            Tab(text: 'How to Play'),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent(GameModel game) {
    return SliverFillRemaining(
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildActiveSessionsTab(),
          _buildHowToPlayTab(game),
        ],
      ),
    );
  }

  Widget _buildActiveSessionsTab() {
    return BlocBuilder<GameBloc, GameState>(
      builder: (context, state) {
        if (state is ActiveSessionsLoaded) {
          if (state.sessions.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.inbox,
                    size: 80,
                    color: AppColors.textHint,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No Active Sessions',
                    style: AppTextStyles.heading3,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Be the first to create a session!',
                    style: AppTextStyles.body.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 24),
                  custom.CustomButton(
                    text: 'Create Session',
                    onPressed: _showCreateSessionDialog,
                    isFullWidth: false,
                    icon: Icons.add,
                  ),
                ],
              ),
            );
          }

          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: state.sessions.length,
                  itemBuilder: (context, index) {
                    final session = state.sessions[index];
                    return _buildSessionCard(session);
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: custom.CustomButton(
                  text: 'Create New Session',
                  onPressed: _showCreateSessionDialog,
                  icon: Icons.add,
                ),
              ),
            ],
          );
        }

        return const LoadingIndicator(message: 'Loading sessions...');
      },
    );
  }

  Widget _buildSessionCard(GameSessionModel session) {
    final canJoin = session.canJoin;
    final isFull = session.isFull;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: canJoin ? AppColors.success.withOpacity(0.3) : Colors.grey.shade300,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Session #${session.id.substring(0, 8)}',
                style: AppTextStyles.bodyBold,
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _getStatusColor(session.status).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  session.status.toUpperCase(),
                  style: AppTextStyles.caption.copyWith(
                    color: _getStatusColor(session.status),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildSessionInfo(
                Icons.currency_rupee,
                'Entry Fee',
                Formatters.currency(session.entryFee),
              ),
              const SizedBox(width: 16),
              _buildSessionInfo(
                Icons.emoji_events,
                'Prize Pool',
                Formatters.currency(session.prizePool),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Row(
                  children: [
                    const Icon(Icons.people, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 4),
                    Text(
                      '${session.currentPlayers}/${session.maxPlayers} Players',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              if (canJoin)
                ElevatedButton(
                  onPressed: () => _joinSession(session.id),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.success,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                  ),
                  child: const Text('Join Now'),
                )
              else if (isFull)
                Text(
                  'Full',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.error,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSessionInfo(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 4),
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

  Color _getStatusColor(String status) {
    switch (status) {
      case 'waiting':
        return AppColors.warning;
      case 'playing':
        return AppColors.primary;
      case 'completed':
        return AppColors.success;
      default:
        return AppColors.textSecondary;
    }
  }

  Widget _buildHowToPlayTab(GameModel game) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Game Rules',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 16),
            Text(
              game.rules ?? 'No rules available for this game.',
              style: AppTextStyles.body,
            ),
            const SizedBox(height: 24),
            Text(
              'How to Play',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 16),
            _buildStep(1, 'Join or create a game session'),
            _buildStep(2, 'Wait for other players to join'),
            _buildStep(3, 'Mark yourself as ready when all players join'),
            _buildStep(4, 'Play the game and compete for prizes'),
            _buildStep(5, 'Winners receive prize money in their wallet'),
          ],
        ),
      ),
    );
  }

  Widget _buildStep(int number, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.primary,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                '$number',
                style: AppTextStyles.bodyBold.copyWith(
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Text(
                text,
                style: AppTextStyles.body,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showCreateSessionDialog() {
    // TODO: Show create session dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Create session feature coming soon!')),
    );
  }

  void _joinSession(String sessionId) {
    context.read<GameBloc>().add(JoinSessionEvent(sessionId: sessionId));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Joining session...')),
    );
  }
}
