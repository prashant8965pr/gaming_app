import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../widgets/custom_button.dart' as custom;

/// Referral screen with invite code and rewards
class ReferralScreen extends StatefulWidget {
  const ReferralScreen({super.key});

  @override
  State<ReferralScreen> createState() => _ReferralScreenState();
}

class _ReferralScreenState extends State<ReferralScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final String _referralCode = 'GAME2024XYZ'; // Mock referral code
  final int _totalReferrals = 12;
  final double _totalEarnings = 3500.0;
  final double _referralBonus = 100.0; // Bonus per referral

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
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
        title: const Text('Refer & Earn'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: _showHowItWorks,
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Referral Header Card
            _buildReferralHeaderCard(),

            // Stats Cards
            _buildStatsCards(),

            // Tabs
            _buildTabBar(),

            // Tab Content
            SizedBox(
              height: 400,
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildReferralsTab(),
                  _buildRewardsTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReferralHeaderCard() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6366F1).withOpacity(0.4),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          const Icon(
            Icons.card_giftcard,
            color: Colors.white,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            'Invite Friends & Earn',
            style: AppTextStyles.heading2.copyWith(
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Get ₹${_referralBonus.toStringAsFixed(0)} for each friend who joins!',
            style: AppTextStyles.body.copyWith(
              color: Colors.white.withOpacity(0.9),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),

          // Referral Code
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Colors.white.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Your Referral Code',
                      style: AppTextStyles.caption.copyWith(
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _referralCode,
                      style: AppTextStyles.heading2.copyWith(
                        color: Colors.white,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
                IconButton(
                  onPressed: _copyReferralCode,
                  icon: const Icon(
                    Icons.copy,
                    color: Colors.white,
                  ),
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Share Buttons
          Row(
            children: [
              Expanded(
                child: custom.CustomButton(
                  text: 'Share',
                  onPressed: _shareReferralCode,
                  icon: Icons.share,
                  buttonStyle: custom.ButtonStyle.secondary,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: custom.CustomButton(
                  text: 'WhatsApp',
                  onPressed: _shareViaWhatsApp,
                  icon: Icons.chat,
                  buttonStyle: custom.ButtonStyle.success,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: _buildStatCard(
              'Total Referrals',
              _totalReferrals.toString(),
              Icons.people,
              AppColors.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatCard(
              'Total Earnings',
              Formatters.currency(_totalEarnings),
              Icons.currency_rupee,
              AppColors.success,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: color,
              size: 24,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: AppTextStyles.heading2.copyWith(
              color: color,
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
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.all(16),
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
          Tab(text: 'My Referrals'),
          Tab(text: 'Rewards'),
        ],
      ),
    );
  }

  Widget _buildReferralsTab() {
    final referrals = _getMockReferrals();

    if (referrals.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.person_add,
                size: 64,
                color: AppColors.textHint.withOpacity(0.5),
              ),
              const SizedBox(height: 16),
              Text(
                'No Referrals Yet',
                style: AppTextStyles.heading3,
              ),
              const SizedBox(height: 8),
              Text(
                'Start inviting friends and earn rewards!',
                style: AppTextStyles.body.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: referrals.length,
      itemBuilder: (context, index) {
        final referral = referrals[index];
        return _buildReferralCard(referral);
      },
    );
  }

  Widget _buildReferralCard(Referral referral) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.primary.withOpacity(0.1),
            child: Text(
              referral.name[0].toUpperCase(),
              style: AppTextStyles.bodyBold.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  referral.name,
                  style: AppTextStyles.bodyBold,
                ),
                const SizedBox(height: 4),
                Text(
                  'Joined ${Formatters.date(referral.joinedDate)}',
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
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: referral.status == 'completed'
                      ? AppColors.success.withOpacity(0.1)
                      : AppColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  referral.status == 'completed' ? 'Earned' : 'Pending',
                  style: AppTextStyles.caption.copyWith(
                    color: referral.status == 'completed'
                        ? AppColors.success
                        : AppColors.warning,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '+${Formatters.currency(referral.reward)}',
                style: AppTextStyles.bodyBold.copyWith(
                  color: AppColors.success,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRewardsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Reward Tiers
        _buildRewardTierCard(
          'Bronze',
          '1-5 referrals',
          100,
          Icons.workspace_premium,
          const Color(0xFFCD7F32),
        ),
        const SizedBox(height: 12),
        _buildRewardTierCard(
          'Silver',
          '6-10 referrals',
          150,
          Icons.workspace_premium,
          const Color(0xFFC0C0C0),
        ),
        const SizedBox(height: 12),
        _buildRewardTierCard(
          'Gold',
          '11-20 referrals',
          200,
          Icons.workspace_premium,
          const Color(0xFFFFD700),
        ),
        const SizedBox(height: 12),
        _buildRewardTierCard(
          'Platinum',
          '20+ referrals',
          300,
          Icons.workspace_premium,
          const Color(0xFFE5E4E2),
        ),

        const SizedBox(height: 20),

        // Special Bonuses
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.info.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: AppColors.info.withOpacity(0.3),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: AppColors.info,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Special Bonuses',
                    style: AppTextStyles.bodyBold.copyWith(
                      color: AppColors.info,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildBonusItem(
                'When your friend makes first deposit',
                '₹50 bonus',
              ),
              _buildBonusItem(
                'When your friend plays 5 games',
                '₹25 bonus',
              ),
              _buildBonusItem(
                'When your friend wins first game',
                '₹30 bonus',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRewardTierCard(
    String tier,
    String requirement,
    double reward,
    IconData icon,
    Color color,
  ) {
    final isUnlocked = tier == 'Bronze' || tier == 'Silver';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isUnlocked ? color.withOpacity(0.5) : Colors.grey.shade200,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: color,
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$tier Tier',
                  style: AppTextStyles.bodyBold,
                ),
                const SizedBox(height: 4),
                Text(
                  requirement,
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
              Text(
                '+${Formatters.currency(reward)}',
                style: AppTextStyles.heading3.copyWith(
                  color: color,
                ),
              ),
              const SizedBox(height: 4),
              if (isUnlocked)
                const Icon(
                  Icons.check_circle,
                  color: AppColors.success,
                  size: 20,
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBonusItem(String description, String bonus) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(
            Icons.check_circle,
            color: AppColors.success,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              description,
              style: AppTextStyles.caption,
            ),
          ),
          Text(
            bonus,
            style: AppTextStyles.caption.copyWith(
              color: AppColors.success,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  void _copyReferralCode() {
    Clipboard.setData(ClipboardData(text: _referralCode));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Referral code copied to clipboard!'),
        backgroundColor: AppColors.success,
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: 'Share',
          textColor: Colors.white,
          onPressed: _shareReferralCode,
        ),
      ),
    );
  }

  void _shareReferralCode() {
    final message = '''
🎮 Join me on the best gaming platform!

Use my referral code: $_referralCode

Download now and get ₹100 bonus on signup!
    ''';

    Share.share(message);
  }

  void _shareViaWhatsApp() {
    final message = '''
🎮 Join me on the best gaming platform!

Use my referral code: *$_referralCode*

Download now and get ₹100 bonus on signup!
    ''';

    Share.share(message);
    // TODO: Implement WhatsApp specific sharing
  }

  void _showHowItWorks() {
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
                'How Referral Works',
                style: AppTextStyles.heading2,
              ),
              const SizedBox(height: 24),

              _buildHowItWorksStep(
                1,
                'Share Your Code',
                'Share your unique referral code with friends via WhatsApp, social media, or any other way.',
                Icons.share,
              ),
              const SizedBox(height: 16),

              _buildHowItWorksStep(
                2,
                'Friend Signs Up',
                'Your friend downloads the app and signs up using your referral code.',
                Icons.person_add,
              ),
              const SizedBox(height: 16),

              _buildHowItWorksStep(
                3,
                'Both Get Rewards',
                'You get ₹$_referralBonus and your friend gets ₹100 bonus instantly!',
                Icons.card_giftcard,
              ),
              const SizedBox(height: 16),

              _buildHowItWorksStep(
                4,
                'Earn More',
                'Earn additional bonuses when your friend makes deposits and plays games!',
                Icons.trending_up,
              ),

              const SizedBox(height: 24),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.lightbulb_outline,
                          color: AppColors.success,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Pro Tip',
                          style: AppTextStyles.bodyBold.copyWith(
                            color: AppColors.success,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'The more friends you refer, the higher your reward tier! Reach Platinum tier for maximum benefits.',
                      style: AppTextStyles.body.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHowItWorksStep(
    int step,
    String title,
    String description,
    IconData icon,
  ) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: AppColors.primary,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$step',
              style: AppTextStyles.bodyBold.copyWith(
                color: Colors.white,
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    icon,
                    size: 20,
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    title,
                    style: AppTextStyles.bodyBold,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: AppTextStyles.body.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // Mock data
  List<Referral> _getMockReferrals() {
    return [
      Referral(
        name: 'Rajesh Kumar',
        joinedDate: DateTime.now().subtract(const Duration(days: 5)),
        reward: 100,
        status: 'completed',
      ),
      Referral(
        name: 'Priya Sharma',
        joinedDate: DateTime.now().subtract(const Duration(days: 12)),
        reward: 100,
        status: 'completed',
      ),
      Referral(
        name: 'Amit Patel',
        joinedDate: DateTime.now().subtract(const Duration(days: 20)),
        reward: 100,
        status: 'completed',
      ),
      Referral(
        name: 'Sneha Reddy',
        joinedDate: DateTime.now().subtract(const Duration(days: 2)),
        reward: 100,
        status: 'pending',
      ),
    ];
  }
}

// Model
class Referral {
  final String name;
  final DateTime joinedDate;
  final double reward;
  final String status; // 'completed' or 'pending'

  Referral({
    required this.name,
    required this.joinedDate,
    required this.reward,
    required this.status,
  });
}
