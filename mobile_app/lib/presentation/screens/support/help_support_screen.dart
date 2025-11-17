import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

/// Help & Support screen
class HelpSupportScreen extends StatefulWidget {
  const HelpSupportScreen({super.key});

  @override
  State<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends State<HelpSupportScreen> {
  int? _expandedFaqIndex;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Help & Support'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header Card
            _buildHeaderCard(),

            // Contact Options
            _buildContactOptions(),

            // FAQs
            _buildFAQs(),

            // Quick Links
            _buildQuickLinks(),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard() {
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
      ),
      child: Column(
        children: [
          const Icon(
            Icons.support_agent,
            color: Colors.white,
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            'How can we help you?',
            style: AppTextStyles.heading2.copyWith(
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'We\'re here 24/7 to assist you with any questions or issues',
            style: AppTextStyles.body.copyWith(
              color: Colors.white.withOpacity(0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildContactOptions() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Contact Us',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 12),
          _buildContactCard(
            'Live Chat',
            'Get instant support from our team',
            Icons.chat_bubble,
            AppColors.primary,
            _openLiveChat,
          ),
          const SizedBox(height: 12),
          _buildContactCard(
            'Email Support',
            'support@gameapp.com',
            Icons.email,
            AppColors.success,
            _openEmail,
          ),
          const SizedBox(height: 12),
          _buildContactCard(
            'Call Us',
            '+91 1800-XXX-XXXX (Toll Free)',
            Icons.phone,
            AppColors.info,
            _openPhone,
          ),
          const SizedBox(height: 12),
          _buildContactCard(
            'WhatsApp',
            'Chat with us on WhatsApp',
            Icons.chat,
            const Color(0xFF25D366),
            _openWhatsApp,
          ),
        ],
      ),
    );
  }

  Widget _buildContactCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
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
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.bodyBold,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppColors.textSecondary,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFAQs() {
    return Container(
      margin: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Frequently Asked Questions',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 12),
          ..._getFAQs().asMap().entries.map((entry) {
            final index = entry.key;
            final faq = entry.value;
            return _buildFAQItem(faq, index);
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildFAQItem(FAQ faq, int index) {
    final isExpanded = _expandedFaqIndex == index;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isExpanded
              ? AppColors.primary.withOpacity(0.3)
              : Colors.grey.shade200,
        ),
      ),
      child: Column(
        children: [
          ListTile(
            title: Text(
              faq.question,
              style: AppTextStyles.bodyBold,
            ),
            trailing: Icon(
              isExpanded ? Icons.expand_less : Icons.expand_more,
              color: AppColors.primary,
            ),
            onTap: () {
              setState(() {
                _expandedFaqIndex = isExpanded ? null : index;
              });
            },
          ),
          if (isExpanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Text(
                faq.answer,
                style: AppTextStyles.body.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildQuickLinks() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quick Links',
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 12),
          _buildQuickLinkCard(
            'Terms & Conditions',
            Icons.description,
            _openTerms,
          ),
          const SizedBox(height: 8),
          _buildQuickLinkCard(
            'Privacy Policy',
            Icons.privacy_tip,
            _openPrivacy,
          ),
          const SizedBox(height: 8),
          _buildQuickLinkCard(
            'Responsible Gaming',
            Icons.favorite,
            _openResponsibleGaming,
          ),
          const SizedBox(height: 8),
          _buildQuickLinkCard(
            'Community Guidelines',
            Icons.people,
            _openGuidelines,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickLinkCard(String title, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: AppColors.primary,
              size: 24,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: AppTextStyles.bodyMedium,
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppColors.textSecondary,
            ),
          ],
        ),
      ),
    );
  }

  void _openLiveChat() {
    // TODO: Implement live chat
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Opening live chat...'),
      ),
    );
  }

  void _openEmail() async {
    final Uri emailUri = Uri(
      scheme: 'mailto',
      path: 'support@gameapp.com',
      query: 'subject=Support Request',
    );

    if (await canLaunchUrl(emailUri)) {
      await launchUrl(emailUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not open email client'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  void _openPhone() async {
    final Uri phoneUri = Uri(scheme: 'tel', path: '1800XXXXXXX');

    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not open phone dialer'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  void _openWhatsApp() async {
    final Uri whatsappUri = Uri.parse('https://wa.me/911800XXXXXXX');

    if (await canLaunchUrl(whatsappUri)) {
      await launchUrl(whatsappUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Could not open WhatsApp'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  void _openTerms() {
    // TODO: Navigate to terms screen or open web view
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening Terms & Conditions...')),
    );
  }

  void _openPrivacy() {
    // TODO: Navigate to privacy screen or open web view
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening Privacy Policy...')),
    );
  }

  void _openResponsibleGaming() {
    // TODO: Navigate to responsible gaming screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening Responsible Gaming...')),
    );
  }

  void _openGuidelines() {
    // TODO: Navigate to guidelines screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening Community Guidelines...')),
    );
  }

  List<FAQ> _getFAQs() {
    return [
      FAQ(
        question: 'How do I add money to my wallet?',
        answer:
            'You can add money to your wallet by tapping on the "Add Money" button in the Wallet tab. Choose your preferred payment method (UPI, Card, or Net Banking) and enter the amount. You can also use promo codes to get bonus credits.',
      ),
      FAQ(
        question: 'How do I withdraw my winnings?',
        answer:
            'To withdraw your winnings, go to the Wallet tab and tap on "Withdraw". Enter the amount you want to withdraw and select your bank account. Please note that only your winnings balance can be withdrawn, not bonus amounts. KYC verification is required for withdrawals.',
      ),
      FAQ(
        question: 'What is KYC verification and why is it required?',
        answer:
            'KYC (Know Your Customer) verification is a mandatory process required by law for all gaming platforms. It helps ensure the security of your account and enables you to withdraw your winnings. You need to submit your PAN card and Aadhaar card for verification.',
      ),
      FAQ(
        question: 'How long does withdrawal take?',
        answer:
            'Withdrawal processing typically takes 1-3 business days. The exact time depends on your bank and the verification status of your account. You can track the status of your withdrawal in the transaction history.',
      ),
      FAQ(
        question: 'What happens to my bonus balance?',
        answer:
            'Bonus balance can be used to enter games and tournaments. Any winnings earned using bonus balance will be credited to your winnings balance, which can be withdrawn. However, bonus amounts themselves cannot be withdrawn directly.',
      ),
      FAQ(
        question: 'How do I refer friends and earn rewards?',
        answer:
            'Go to the Referrals section in your profile and share your unique referral code with friends. When they sign up using your code and play games, both you and your friend will receive bonus rewards. The more friends you refer, the higher your reward tier!',
      ),
      FAQ(
        question: 'Is my money safe?',
        answer:
            'Yes! We use bank-grade encryption and secure payment gateways to protect your money and personal information. All transactions are processed through PCI-DSS compliant payment partners. Your data is never shared with third parties without your consent.',
      ),
      FAQ(
        question: 'What if I face issues during a game?',
        answer:
            'If you face any technical issues during a game, please report it immediately using the "Report Issue" option in the game details or contact our 24/7 support team. We will investigate and resolve the issue as quickly as possible.',
      ),
      FAQ(
        question: 'Can I cancel a withdrawal request?',
        answer:
            'Yes, you can cancel a pending withdrawal request before it is processed. Go to your transaction history, find the withdrawal transaction, and tap on "Cancel". Once the withdrawal is processed, it cannot be cancelled.',
      ),
      FAQ(
        question: 'How do I change my registered phone number?',
        answer:
            'For security reasons, you cannot change your registered phone number directly. Please contact our support team with your KYC documents and they will assist you with the process.',
      ),
    ];
  }
}

/// FAQ Model
class FAQ {
  final String question;
  final String answer;

  FAQ({
    required this.question,
    required this.answer,
  });
}
