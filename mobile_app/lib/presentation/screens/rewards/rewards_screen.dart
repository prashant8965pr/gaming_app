import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

/// Rewards and achievements screen
class RewardsScreen extends StatefulWidget {
  const RewardsScreen({super.key});

  @override
  State<RewardsScreen> createState() => _RewardsScreenState();
}

class _RewardsScreenState extends State<RewardsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadRewards();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadRewards() {
    // TODO: Load rewards via BLoC
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // App Bar
            _buildAppBar(),

            // Reward Points Card
            _buildRewardPointsCard(),

            // Tabs
            _buildTabBar(),

            // Content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildAchievementsTab(),
                  _buildChallengesTab(),
                  _buildLeaderboardTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Rewards & Achievements',
                  style: AppTextStyles.heading2,
                ),
                Text(
                  'Track your gaming journey',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.card_giftcard),
            onPressed: () {
              // TODO: Navigate to rewards shop
            },
          ),
        ],
      ),
    );
  }

  Widget _buildRewardPointsCard() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFA726), Color(0xFFFF7043)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFFFA726).withOpacity(0.3),
            blurRadius: 12,
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
                Row(
                  children: [
                    const Icon(
                      Icons.stars,
                      color: Colors.white,
                      size: 24,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Reward Points',
                      style: AppTextStyles.body.copyWith(
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  '2,450',
                  style: AppTextStyles.heading1.copyWith(
                    color: Colors.white,
                    fontSize: 32,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '250 points to next level',
                  style: AppTextStyles.caption.copyWith(
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'Level',
                    style: AppTextStyles.caption.copyWith(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 10,
                    ),
                  ),
                  Text(
                    '12',
                    style: AppTextStyles.heading1.copyWith(
                      color: Colors.white,
                      fontSize: 28,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
          Tab(text: 'Achievements'),
          Tab(text: 'Challenges'),
          Tab(text: 'Leaderboard'),
        ],
      ),
    );
  }

  Widget _buildAchievementsTab() {
    final achievements = _getMockAchievements();

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: achievements.length,
      itemBuilder: (context, index) {
        final achievement = achievements[index];
        return _buildAchievementCard(achievement);
      },
    );
  }

  Widget _buildAchievementCard(Achievement achievement) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: achievement.isUnlocked
              ? AppColors.success.withOpacity(0.3)
              : Colors.grey.shade200,
        ),
      ),
      child: Row(
        children: [
          // Icon
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: achievement.isUnlocked
                  ? AppColors.warning.withOpacity(0.2)
                  : Colors.grey.shade100,
              shape: BoxShape.circle,
            ),
            child: Icon(
              achievement.icon,
              color: achievement.isUnlocked
                  ? AppColors.warning
                  : AppColors.textHint,
              size: 30,
            ),
          ),
          const SizedBox(width: 16),

          // Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        achievement.title,
                        style: AppTextStyles.bodyBold.copyWith(
                          color: achievement.isUnlocked
                              ? AppColors.textPrimary
                              : AppColors.textSecondary,
                        ),
                      ),
                    ),
                    if (achievement.isUnlocked)
                      const Icon(
                        Icons.check_circle,
                        color: AppColors.success,
                        size: 20,
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  achievement.description,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 8),

                // Progress bar
                if (!achievement.isUnlocked) ...[
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: achievement.progress,
                      backgroundColor: Colors.grey.shade200,
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        AppColors.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${(achievement.progress * 100).toInt()}% Complete',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],

                // Reward
                if (achievement.isUnlocked)
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.stars,
                          size: 14,
                          color: AppColors.warning,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '+${achievement.rewardPoints} points',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.warning,
                            fontWeight: FontWeight.w600,
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
    );
  }

  Widget _buildChallengesTab() {
    final challenges = _getMockChallenges();

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: challenges.length,
      itemBuilder: (context, index) {
        final challenge = challenges[index];
        return _buildChallengeCard(challenge);
      },
    );
  }

  Widget _buildChallengeCard(Challenge challenge) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: _getChallengeTypeColor(challenge.type).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  challenge.type.toUpperCase(),
                  style: AppTextStyles.caption.copyWith(
                    color: _getChallengeTypeColor(challenge.type),
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              ),
              const Spacer(),
              Icon(
                Icons.timer_outlined,
                size: 14,
                color: AppColors.textSecondary,
              ),
              const SizedBox(width: 4),
              Text(
                challenge.expiresIn,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            challenge.title,
            style: AppTextStyles.bodyBold,
          ),
          const SizedBox(height: 4),
          Text(
            challenge.description,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 12),

          // Progress
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: challenge.progress,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          _getChallengeTypeColor(challenge.type),
                        ),
                        minHeight: 6,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${challenge.current}/${challenge.target}',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.stars,
                      color: AppColors.warning,
                      size: 18,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '+${challenge.rewardPoints}',
                      style: AppTextStyles.bodyBold.copyWith(
                        color: AppColors.warning,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLeaderboardTab() {
    final leaderboard = _getMockLeaderboard();

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: leaderboard.length,
      itemBuilder: (context, index) {
        final entry = leaderboard[index];
        final rank = index + 1;
        final isCurrentUser = rank == 8; // Mock current user position

        return _buildLeaderboardEntry(entry, rank, isCurrentUser);
      },
    );
  }

  Widget _buildLeaderboardEntry(
    LeaderboardEntry entry,
    int rank,
    bool isCurrentUser,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isCurrentUser
            ? AppColors.primary.withOpacity(0.1)
            : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isCurrentUser
              ? AppColors.primary.withOpacity(0.3)
              : Colors.grey.shade200,
        ),
      ),
      child: Row(
        children: [
          // Rank
          SizedBox(
            width: 40,
            child: rank <= 3
                ? Icon(
                    Icons.emoji_events,
                    color: rank == 1
                        ? const Color(0xFFFFD700)
                        : rank == 2
                            ? const Color(0xFFC0C0C0)
                            : const Color(0xFFCD7F32),
                    size: 32,
                  )
                : Text(
                    '#$rank',
                    style: AppTextStyles.heading3.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
          ),
          const SizedBox(width: 16),

          // Avatar
          CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.primary.withOpacity(0.2),
            child: Text(
              entry.username[0].toUpperCase(),
              style: AppTextStyles.bodyBold.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),

          // Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.username,
                  style: AppTextStyles.bodyBold,
                ),
                const SizedBox(height: 2),
                Text(
                  '${entry.gamesWon} wins • ${entry.winRate.toStringAsFixed(0)}% win rate',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),

          // Points
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.stars,
                    color: AppColors.warning,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    Formatters.number(entry.points),
                    style: AppTextStyles.bodyBold.copyWith(
                      color: AppColors.warning,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(
                Formatters.currency(entry.totalWinnings),
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.success,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getChallengeTypeColor(String type) {
    switch (type) {
      case 'daily':
        return AppColors.info;
      case 'weekly':
        return AppColors.primary;
      case 'special':
        return AppColors.warning;
      default:
        return AppColors.textSecondary;
    }
  }

  // Mock data
  List<Achievement> _getMockAchievements() {
    return [
      Achievement(
        title: 'First Victory',
        description: 'Win your first game',
        icon: Icons.emoji_events,
        isUnlocked: true,
        progress: 1.0,
        rewardPoints: 100,
      ),
      Achievement(
        title: 'Winning Streak',
        description: 'Win 5 games in a row',
        icon: Icons.whatshot,
        isUnlocked: false,
        progress: 0.6,
        rewardPoints: 500,
      ),
      Achievement(
        title: 'High Roller',
        description: 'Win a game with entry fee over ₹1000',
        icon: Icons.diamond,
        isUnlocked: true,
        progress: 1.0,
        rewardPoints: 750,
      ),
      Achievement(
        title: 'Social Player',
        description: 'Invite 10 friends',
        icon: Icons.people,
        isUnlocked: false,
        progress: 0.3,
        rewardPoints: 300,
      ),
      Achievement(
        title: 'Game Master',
        description: 'Play 100 games',
        icon: Icons.stars,
        isUnlocked: false,
        progress: 0.42,
        rewardPoints: 1000,
      ),
    ];
  }

  List<Challenge> _getMockChallenges() {
    return [
      Challenge(
        title: 'Daily Champion',
        description: 'Win 3 games today',
        type: 'daily',
        current: 1,
        target: 3,
        progress: 0.33,
        rewardPoints: 150,
        expiresIn: '18h',
      ),
      Challenge(
        title: 'Weekly Warrior',
        description: 'Win 20 games this week',
        type: 'weekly',
        current: 12,
        target: 20,
        progress: 0.6,
        rewardPoints: 800,
        expiresIn: '4d',
      ),
      Challenge(
        title: 'Special Event',
        description: 'Participate in tournament',
        type: 'special',
        current: 0,
        target: 1,
        progress: 0.0,
        rewardPoints: 2000,
        expiresIn: '2d',
      ),
    ];
  }

  List<LeaderboardEntry> _getMockLeaderboard() {
    return List.generate(
      20,
      (index) => LeaderboardEntry(
        username: 'Player${index + 1}',
        points: 10000 - (index * 500),
        gamesWon: 150 - (index * 5),
        totalWinnings: 50000.0 - (index * 2000),
        winRate: 75.0 - (index * 2),
      ),
    );
  }
}

// Models
class Achievement {
  final String title;
  final String description;
  final IconData icon;
  final bool isUnlocked;
  final double progress;
  final int rewardPoints;

  Achievement({
    required this.title,
    required this.description,
    required this.icon,
    required this.isUnlocked,
    required this.progress,
    required this.rewardPoints,
  });
}

class Challenge {
  final String title;
  final String description;
  final String type;
  final int current;
  final int target;
  final double progress;
  final int rewardPoints;
  final String expiresIn;

  Challenge({
    required this.title,
    required this.description,
    required this.type,
    required this.current,
    required this.target,
    required this.progress,
    required this.rewardPoints,
    required this.expiresIn,
  });
}

class LeaderboardEntry {
  final String username;
  final int points;
  final int gamesWon;
  final double totalWinnings;
  final double winRate;

  LeaderboardEntry({
    required this.username,
    required this.points,
    required this.gamesWon,
    required this.totalWinnings,
    required this.winRate,
  });
}
