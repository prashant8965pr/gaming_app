import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../widgets/empty_state.dart';

/// Notifications screen
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadNotifications();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadNotifications() {
    // TODO: Load notifications via BLoC
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Notifications'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'mark_all_read') {
                _markAllAsRead();
              } else if (value == 'clear_all') {
                _clearAllNotifications();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'mark_all_read',
                child: Text('Mark all as read'),
              ),
              const PopupMenuItem(
                value: 'clear_all',
                child: Text('Clear all'),
              ),
            ],
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          indicatorColor: AppColors.primary,
          isScrollable: true,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Games'),
            Tab(text: 'Transactions'),
            Tab(text: 'Updates'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildNotificationsList('all'),
          _buildNotificationsList('game'),
          _buildNotificationsList('transaction'),
          _buildNotificationsList('update'),
        ],
      ),
    );
  }

  Widget _buildNotificationsList(String type) {
    final notifications = _getFilteredNotifications(type);

    if (notifications.isEmpty) {
      return const EmptyState(
        title: 'No Notifications',
        message: 'You don\'t have any notifications yet.',
        icon: Icons.notifications_none,
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: notifications.length,
      itemBuilder: (context, index) {
        final notification = notifications[index];
        return _buildNotificationCard(notification);
      },
    );
  }

  Widget _buildNotificationCard(NotificationItem notification) {
    return Dismissible(
      key: Key(notification.id),
      background: Container(
        margin: const EdgeInsets.only(bottom: 8),
        decoration: BoxDecoration(
          color: AppColors.danger,
          borderRadius: BorderRadius.circular(12),
        ),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Icon(
          Icons.delete,
          color: Colors.white,
        ),
      ),
      direction: DismissDirection.endToStart,
      onDismissed: (direction) {
        _deleteNotification(notification.id);
      },
      child: GestureDetector(
        onTap: () => _handleNotificationTap(notification),
        child: Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: notification.isRead
                ? Colors.white
                : AppColors.primary.withOpacity(0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: notification.isRead
                  ? Colors.grey.shade200
                  : AppColors.primary.withOpacity(0.2),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: _getNotificationColor(notification.type).withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _getNotificationIcon(notification.type),
                  color: _getNotificationColor(notification.type),
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            notification.title,
                            style: AppTextStyles.bodyBold.copyWith(
                              color: notification.isRead
                                  ? AppColors.textPrimary
                                  : AppColors.textPrimary,
                            ),
                          ),
                        ),
                        if (!notification.isRead)
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppColors.primary,
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      notification.message,
                      style: AppTextStyles.body.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 12,
                          color: AppColors.textHint,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _formatTimestamp(notification.timestamp),
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.textHint,
                          ),
                        ),
                      ],
                    ),

                    // Action buttons
                    if (notification.actionButtons != null &&
                        notification.actionButtons!.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: notification.actionButtons!
                            .map((action) => Padding(
                                  padding: const EdgeInsets.only(right: 8),
                                  child: OutlinedButton(
                                    onPressed: () => _handleAction(action),
                                    style: OutlinedButton.styleFrom(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16,
                                        vertical: 8,
                                      ),
                                      side: BorderSide(
                                        color: action.isPrimary
                                            ? AppColors.primary
                                            : Colors.grey.shade300,
                                      ),
                                    ),
                                    child: Text(
                                      action.label,
                                      style: TextStyle(
                                        color: action.isPrimary
                                            ? AppColors.primary
                                            : AppColors.textSecondary,
                                      ),
                                    ),
                                  ),
                                ))
                            .toList(),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getNotificationIcon(String type) {
    switch (type) {
      case 'game':
        return Icons.sports_esports;
      case 'transaction':
        return Icons.account_balance_wallet;
      case 'achievement':
        return Icons.emoji_events;
      case 'update':
        return Icons.info;
      case 'promotion':
        return Icons.local_offer;
      default:
        return Icons.notifications;
    }
  }

  Color _getNotificationColor(String type) {
    switch (type) {
      case 'game':
        return AppColors.primary;
      case 'transaction':
        return AppColors.success;
      case 'achievement':
        return AppColors.warning;
      case 'update':
        return AppColors.info;
      case 'promotion':
        return const Color(0xFFE91E63);
      default:
        return AppColors.textSecondary;
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return DateFormat('MMM d, yyyy').format(timestamp);
    }
  }

  List<NotificationItem> _getFilteredNotifications(String type) {
    final allNotifications = _getMockNotifications();

    if (type == 'all') {
      return allNotifications;
    }

    return allNotifications.where((n) => n.type == type).toList();
  }

  void _handleNotificationTap(NotificationItem notification) {
    // Mark as read
    setState(() {
      notification.isRead = true;
    });

    // Navigate based on notification type
    // TODO: Implement navigation
  }

  void _handleAction(NotificationAction action) {
    // TODO: Handle action
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Action: ${action.label}')),
    );
  }

  void _deleteNotification(String id) {
    // TODO: Delete notification via BLoC
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Notification deleted')),
    );
  }

  void _markAllAsRead() {
    setState(() {
      // TODO: Mark all as read via BLoC
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('All notifications marked as read')),
    );
  }

  void _clearAllNotifications() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear All Notifications'),
        content: const Text(
          'Are you sure you want to clear all notifications? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                // TODO: Clear all notifications via BLoC
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('All notifications cleared')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.danger,
            ),
            child: const Text('Clear All'),
          ),
        ],
      ),
    );
  }

  // Mock data
  List<NotificationItem> _getMockNotifications() {
    return [
      NotificationItem(
        id: '1',
        type: 'game',
        title: 'Game Invite',
        message: 'Player123 invited you to join Ludo King session',
        timestamp: DateTime.now().subtract(const Duration(minutes: 5)),
        isRead: false,
        actionButtons: [
          NotificationAction(label: 'Accept', isPrimary: true),
          NotificationAction(label: 'Decline', isPrimary: false),
        ],
      ),
      NotificationItem(
        id: '2',
        type: 'transaction',
        title: 'Deposit Successful',
        message: 'Your deposit of ₹1,000 has been credited to your wallet',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        isRead: false,
      ),
      NotificationItem(
        id: '3',
        type: 'achievement',
        title: 'Achievement Unlocked!',
        message: 'Congratulations! You\'ve unlocked "First Victory" achievement',
        timestamp: DateTime.now().subtract(const Duration(hours: 5)),
        isRead: true,
      ),
      NotificationItem(
        id: '4',
        type: 'game',
        title: 'You Won!',
        message: 'Congratulations! You won ₹2,500 in Rummy game',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        isRead: true,
      ),
      NotificationItem(
        id: '5',
        type: 'promotion',
        title: 'Special Offer!',
        message: 'Get 50% bonus on deposits above ₹500 today only!',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        isRead: false,
        actionButtons: [
          NotificationAction(label: 'Add Money', isPrimary: true),
        ],
      ),
      NotificationItem(
        id: '6',
        type: 'update',
        title: 'New Games Available',
        message: 'Check out our newly added Fantasy Cricket game!',
        timestamp: DateTime.now().subtract(const Duration(days: 2)),
        isRead: true,
      ),
      NotificationItem(
        id: '7',
        type: 'transaction',
        title: 'Withdrawal Initiated',
        message: 'Your withdrawal request of ₹5,000 is being processed',
        timestamp: DateTime.now().subtract(const Duration(days: 3)),
        isRead: true,
      ),
      NotificationItem(
        id: '8',
        type: 'game',
        title: 'Tournament Starting Soon',
        message: 'Mega Poker Tournament starts in 30 minutes',
        timestamp: DateTime.now().subtract(const Duration(days: 4)),
        isRead: true,
      ),
    ];
  }
}

// Models
class NotificationItem {
  final String id;
  final String type;
  final String title;
  final String message;
  final DateTime timestamp;
  bool isRead;
  final List<NotificationAction>? actionButtons;

  NotificationItem({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.timestamp,
    this.isRead = false,
    this.actionButtons,
  });
}

class NotificationAction {
  final String label;
  final bool isPrimary;

  NotificationAction({
    required this.label,
    this.isPrimary = false,
  });
}
