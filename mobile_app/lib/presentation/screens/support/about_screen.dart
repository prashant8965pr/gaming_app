import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// About screen with app information
class AboutScreen extends StatefulWidget {
  const AboutScreen({super.key});

  @override
  State<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends State<AboutScreen> {
  String _version = '1.0.0';
  String _buildNumber = '1';

  @override
  void initState() {
    super.initState();
    _loadAppInfo();
  }

  Future<void> _loadAppInfo() async {
    final packageInfo = await PackageInfo.fromPlatform();
    setState(() {
      _version = packageInfo.version;
      _buildNumber = packageInfo.buildNumber;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('About'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: 24),

            // App Logo and Name
            _buildAppHeader(),

            const SizedBox(height: 32),

            // Version Info
            _buildVersionInfo(),

            const SizedBox(height: 24),

            // App Description
            _buildDescription(),

            const SizedBox(height: 24),

            // Features
            _buildFeatures(),

            const SizedBox(height: 24),

            // Social Links
            _buildSocialLinks(),

            const SizedBox(height: 24),

            // Legal
            _buildLegal(),

            const SizedBox(height: 24),

            // Credits
            _buildCredits(),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildAppHeader() {
    return Column(
      children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.primary, Color(0xFFFF8C5F)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Icon(
            Icons.games,
            size: 56,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Gaming Platform',
          style: AppTextStyles.heading1,
        ),
        const SizedBox(height: 4),
        Text(
          'Play. Win. Earn.',
          style: AppTextStyles.body.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildVersionInfo() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildInfoItem('Version', _version),
          Container(
            width: 1,
            height: 40,
            color: Colors.grey.shade300,
          ),
          _buildInfoItem('Build', _buildNumber),
        ],
      ),
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Column(
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
          style: AppTextStyles.heading3,
        ),
      ],
    );
  }

  Widget _buildDescription() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'About Us',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 12),
          Text(
            'Welcome to India\'s most trusted gaming platform! Play your favorite games, compete with players across the country, and win real money.',
            style: AppTextStyles.body.copyWith(
              color: AppColors.textSecondary,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'We are committed to providing a fair, secure, and entertaining gaming experience for all our users. All our games are skill-based and comply with Indian gaming regulations.',
            style: AppTextStyles.body.copyWith(
              color: AppColors.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatures() {
    final features = [
      {'icon': Icons.security, 'title': 'Secure & Safe', 'desc': '100% secure payments'},
      {'icon': Icons.flash_on, 'title': 'Instant Withdrawals', 'desc': 'Withdraw anytime'},
      {'icon': Icons.people, 'title': '10M+ Players', 'desc': 'Join the community'},
      {'icon': Icons.emoji_events, 'title': 'Daily Tournaments', 'desc': 'Win big prizes'},
    ];

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Why Choose Us',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          ...features.map((feature) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        feature['icon'] as IconData,
                        color: AppColors.primary,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            feature['title'] as String,
                            style: AppTextStyles.bodyBold,
                          ),
                          Text(
                            feature['desc'] as String,
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildSocialLinks() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Connect With Us',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSocialButton(
                Icons.facebook,
                const Color(0xFF1877F2),
                'Facebook',
                () => _openUrl('https://facebook.com'),
              ),
              _buildSocialButton(
                Icons.camera_alt,
                const Color(0xFFE4405F),
                'Instagram',
                () => _openUrl('https://instagram.com'),
              ),
              _buildSocialButton(
                Icons.send,
                const Color(0xFF1DA1F2),
                'Twitter',
                () => _openUrl('https://twitter.com'),
              ),
              _buildSocialButton(
                Icons.public,
                AppColors.primary,
                'Website',
                () => _openUrl('https://gameapp.com'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSocialButton(
    IconData icon,
    Color color,
    String label,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: color,
              size: 28,
            ),
          ),
          const SizedBox(height: 8),
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

  Widget _buildLegal() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Legal',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 12),
          _buildLegalLink('Terms & Conditions', Icons.description),
          _buildLegalLink('Privacy Policy', Icons.privacy_tip),
          _buildLegalLink('Refund Policy', Icons.money_off),
          _buildLegalLink('Responsible Gaming', Icons.favorite),
          _buildLegalLink('Licenses', Icons.verified),
        ],
      ),
    );
  }

  Widget _buildLegalLink(String title, IconData icon) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon, color: AppColors.primary, size: 20),
      title: Text(
        title,
        style: AppTextStyles.body,
      ),
      trailing: const Icon(
        Icons.arrow_forward_ios,
        size: 16,
        color: AppColors.textSecondary,
      ),
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Opening $title...')),
        );
      },
    );
  }

  Widget _buildCredits() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.info.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.info_outline,
            color: AppColors.info,
            size: 32,
          ),
          const SizedBox(height: 12),
          Text(
            'This game involves an element of financial risk and may be addictive. Please play responsibly and at your own risk.',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            '© 2024 Gaming Platform. All rights reserved.',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Future<void> _openUrl(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not open link'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }
}
