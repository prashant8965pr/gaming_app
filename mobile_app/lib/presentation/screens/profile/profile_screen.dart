import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../bloc/auth/auth_bloc.dart';
import '../../bloc/auth/auth_event.dart';
import '../../bloc/user/user_bloc.dart';
import '../../bloc/user/user_event.dart';
import '../../bloc/user/user_state.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import 'edit_profile_screen.dart';
import 'kyc_verification_screen.dart';
import 'game_history_screen.dart';
import '../settings/settings_screen.dart';
import '../referral/referral_screen.dart';

/// Profile screen displaying user information and statistics
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() {
    context.read<UserBloc>().add(const LoadUserProfileEvent());
    context.read<UserBloc>().add(const LoadUserStatisticsEvent());
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

              // Profile Header
              _buildProfileHeader(),

              // Statistics
              _buildStatistics(),

              // Menu Items
              _buildMenuItems(),
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
      title: const Text('Profile'),
      actions: [
        IconButton(
          icon: const Icon(Icons.settings_outlined),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const SettingsScreen(),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildProfileHeader() {
    return SliverToBoxAdapter(
      child: BlocBuilder<UserBloc, UserState>(
        builder: (context, state) {
          if (state is UserLoading) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: ShimmerCard(height: 120),
            );
          }

          if (state is UserProfileLoaded) {
            final user = state.user;
            return Container(
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
              child: Row(
                children: [
                  // Avatar
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppColors.primary,
                        width: 3,
                      ),
                    ),
                    child: ClipOval(
                      child: user.avatarUrl != null
                          ? CachedNetworkImage(
                              imageUrl: user.avatarUrl!,
                              fit: BoxFit.cover,
                              placeholder: (context, url) => const Center(
                                child: CircularProgressIndicator(),
                              ),
                              errorWidget: (context, url, error) =>
                                  const Icon(Icons.person, size: 40),
                            )
                          : Container(
                              color: AppColors.primary.withOpacity(0.1),
                              child: const Icon(
                                Icons.person,
                                size: 40,
                                color: AppColors.primary,
                              ),
                            ),
                    ),
                  ),

                  const SizedBox(width: 16),

                  // User info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user.displayName ?? user.username,
                          style: AppTextStyles.heading2,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '@${user.username}',
                          style: AppTextStyles.body.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            _buildStatusChip(
                              user.kycStatus == 'verified' ? 'Verified' : 'Unverified',
                              user.kycStatus == 'verified'
                                  ? AppColors.success
                                  : AppColors.warning,
                            ),
                            const SizedBox(width: 8),
                            _buildStatusChip(
                              user.role.toUpperCase(),
                              AppColors.primary,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  // Edit button
                  IconButton(
                    icon: const Icon(Icons.edit_outlined),
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const EditProfileScreen(),
                        ),
                      );
                    },
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

  Widget _buildStatusChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: AppTextStyles.caption.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildStatistics() {
    return SliverToBoxAdapter(
      child: BlocBuilder<UserBloc, UserState>(
        builder: (context, state) {
          if (state is UserStatisticsLoaded) {
            final stats = state.statistics;
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Statistics',
                    style: AppTextStyles.heading3,
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatItem(
                          'Games Played',
                          '${stats.totalGamesPlayed}',
                          Icons.sports_esports,
                        ),
                      ),
                      Expanded(
                        child: _buildStatItem(
                          'Games Won',
                          '${stats.totalGamesWon}',
                          Icons.emoji_events,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatItem(
                          'Win Rate',
                          '${stats.winRate.toStringAsFixed(1)}%',
                          Icons.trending_up,
                        ),
                      ),
                      Expanded(
                        child: _buildStatItem(
                          'Total Winnings',
                          Formatters.currency(stats.totalWinnings),
                          Icons.currency_rupee,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatItem(
                          'Current Streak',
                          '${stats.currentStreak} days',
                          Icons.local_fire_department,
                        ),
                      ),
                      Expanded(
                        child: _buildStatItem(
                          'Best Streak',
                          '${stats.longestStreak} days',
                          Icons.star,
                        ),
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

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppColors.primary, size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.primary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildMenuItems() {
    final menuItems = [
      {
        'icon': Icons.emoji_events_outlined,
        'title': 'Achievements',
        'subtitle': 'View your achievements',
        'onTap': () {},
      },
      {
        'icon': Icons.history,
        'title': 'Game History',
        'subtitle': 'View your game history',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const GameHistoryScreen(),
            ),
          );
        },
      },
      {
        'icon': Icons.people_outline,
        'title': 'Referrals',
        'subtitle': 'Invite friends and earn',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ReferralScreen(),
            ),
          );
        },
      },
      {
        'icon': Icons.verified_user_outlined,
        'title': 'KYC Verification',
        'subtitle': 'Complete your KYC',
        'onTap': () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const KYCVerificationScreen(),
            ),
          );
        },
      },
      {
        'icon': Icons.notifications_outlined,
        'title': 'Notification Settings',
        'subtitle': 'Manage your notifications',
        'onTap': () {},
      },
      {
        'icon': Icons.help_outline,
        'title': 'Help & Support',
        'subtitle': 'Get help with your account',
        'onTap': () {},
      },
      {
        'icon': Icons.info_outline,
        'title': 'About',
        'subtitle': 'App version and info',
        'onTap': () {},
      },
      {
        'icon': Icons.logout,
        'title': 'Logout',
        'subtitle': 'Sign out of your account',
        'color': AppColors.error,
        'onTap': _handleLogout,
      },
    ];

    return SliverPadding(
      padding: const EdgeInsets.all(16),
      sliver: SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) {
            final item = menuItems[index];
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: ListTile(
                leading: Icon(
                  item['icon'] as IconData,
                  color: (item['color'] as Color?) ?? AppColors.primary,
                ),
                title: Text(
                  item['title'] as String,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: (item['color'] as Color?) ?? AppColors.textPrimary,
                  ),
                ),
                subtitle: Text(
                  item['subtitle'] as String,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                trailing: const Icon(
                  Icons.chevron_right,
                  color: AppColors.textSecondary,
                ),
                onTap: item['onTap'] as VoidCallback,
              ),
            );
          },
          childCount: menuItems.length,
        ),
      ),
    );
  }

  void _handleLogout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<AuthBloc>().add(const LogoutEvent());
            },
            child: const Text(
              'Logout',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _onRefresh() async {
    context.read<UserBloc>().add(const LoadUserProfileEvent());
    context.read<UserBloc>().add(const LoadUserStatisticsEvent());
  }
}
