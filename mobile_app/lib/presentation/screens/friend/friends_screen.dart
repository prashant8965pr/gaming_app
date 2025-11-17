import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../bloc/friend/friend_bloc.dart';
import '../../bloc/friend/friend_event.dart';
import '../../bloc/friend/friend_state.dart';
import '../../../data/models/friend_model.dart';

class FriendsScreen extends StatefulWidget {
  const FriendsScreen({Key? key}) : super(key: key);

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadFriends();
    _loadFriendRequests();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadFriends() {
    context.read<FriendBloc>().add(const LoadFriends(refresh: true));
  }

  void _loadFriendRequests() {
    context.read<FriendBloc>().add(const LoadFriendRequests(refresh: true));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Friends'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'My Friends'),
            Tab(text: 'Requests'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_add),
            onPressed: () {
              Navigator.pushNamed(context, '/add-friend');
            },
            tooltip: 'Add Friend',
          ),
        ],
      ),
      body: BlocConsumer<FriendBloc, FriendState>(
        listener: (context, state) {
          if (state is FriendError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          } else if (state is FriendRequestAccepted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Friend request accepted!'),
                backgroundColor: Colors.green,
              ),
            );
            _loadFriends();
            _loadFriendRequests();
          } else if (state is FriendRequestRejected) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Friend request rejected'),
              ),
            );
            _loadFriendRequests();
          } else if (state is FriendRemoved) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Friend removed'),
              ),
            );
            _loadFriends();
          }
        },
        builder: (context, state) {
          return TabBarView(
            controller: _tabController,
            children: [
              _buildFriendsTab(state),
              _buildRequestsTab(state),
            ],
          );
        },
      ),
    );
  }

  Widget _buildFriendsTab(FriendState state) {
    if (state is FriendLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state is FriendsLoaded) {
      if (state.friends.isEmpty) {
        return _buildEmptyState(
          icon: Icons.people_outline,
          title: 'No friends yet',
          subtitle: 'Add friends to start playing together!',
          actionLabel: 'Add Friends',
          onAction: () => Navigator.pushNamed(context, '/add-friend'),
        );
      }

      return RefreshIndicator(
        onRefresh: () async {
          _loadFriends();
        },
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: state.friends.length,
          itemBuilder: (context, index) {
            final friend = state.friends[index];
            return _buildFriendCard(friend);
          },
        ),
      );
    }

    return _buildEmptyState(
      icon: Icons.people_outline,
      title: 'No friends',
      subtitle: 'Start adding friends to play together!',
    );
  }

  Widget _buildRequestsTab(FriendState state) {
    if (state is FriendRequestsLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state is FriendRequestsLoaded) {
      if (state.requests.isEmpty) {
        return _buildEmptyState(
          icon: Icons.inbox,
          title: 'No pending requests',
          subtitle: 'Friend requests will appear here',
        );
      }

      return RefreshIndicator(
        onRefresh: () async {
          _loadFriendRequests();
        },
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: state.requests.length,
          itemBuilder: (context, index) {
            final request = state.requests[index];
            return _buildRequestCard(request);
          },
        ),
      );
    }

    return _buildEmptyState(
      icon: Icons.inbox,
      title: 'No requests',
      subtitle: 'Friend requests will appear here',
    );
  }

  Widget _buildFriendCard(FriendshipModel friend) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: Stack(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).primaryColor,
              child: friend.friendAvatar != null
                  ? ClipOval(
                      child: Image.network(
                        friend.friendAvatar!,
                        width: 56,
                        height: 56,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(Icons.person, color: Colors.white);
                        },
                      ),
                    )
                  : const Icon(Icons.person, color: Colors.white, size: 32),
            ),
            if (friend.isOnline)
              Positioned(
                right: 0,
                bottom: 0,
                child: Container(
                  width: 14,
                  height: 14,
                  decoration: BoxDecoration(
                    color: Colors.green,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                ),
              ),
          ],
        ),
        title: Text(
          friend.friendUsername,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Text(
          friend.onlineStatus,
          style: TextStyle(
            color: friend.isOnline ? Colors.green : Colors.grey,
            fontSize: 13,
          ),
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            if (value == 'invite') {
              _showInviteDialog(friend);
            } else if (value == 'remove') {
              _showRemoveDialog(friend);
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'invite',
              child: Row(
                children: [
                  Icon(Icons.gamepad),
                  SizedBox(width: 8),
                  Text('Invite to Game'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'remove',
              child: Row(
                children: [
                  Icon(Icons.person_remove, color: Colors.red),
                  SizedBox(width: 8),
                  Text('Remove Friend', style: TextStyle(color: Colors.red)),
                ],
              ),
            ),
          ],
        ),
        onTap: () {
          // Navigate to friend profile
          Navigator.pushNamed(
            context,
            '/friend-profile',
            arguments: friend.friendId,
          );
        },
      ),
    );
  }

  Widget _buildRequestCard(FriendRequestModel request) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: Theme.of(context).primaryColor,
                  child: request.senderAvatar != null
                      ? ClipOval(
                          child: Image.network(
                            request.senderAvatar!,
                            width: 48,
                            height: 48,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return const Icon(Icons.person,
                                  color: Colors.white);
                            },
                          ),
                        )
                      : const Icon(Icons.person, color: Colors.white),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        request.senderUsername,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        'Sent ${_formatDate(request.createdAt)}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (request.message != null && request.message!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  request.message!,
                  style: const TextStyle(fontSize: 14),
                ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      context
                          .read<FriendBloc>()
                          .add(AcceptFriendRequest(request.id));
                    },
                    icon: const Icon(Icons.check),
                    label: const Text('Accept'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      context
                          .read<FriendBloc>()
                          .add(RejectFriendRequest(request.id));
                    },
                    icon: const Icon(Icons.close),
                    label: const Text('Decline'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState({
    required IconData icon,
    required String title,
    required String subtitle,
    String? actionLabel,
    VoidCallback? onAction,
  }) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 80, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              title,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: onAction,
                child: Text(actionLabel),
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _showInviteDialog(FriendshipModel friend) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Invite ${friend.friendUsername}'),
        content: const Text('Game invitation feature coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showRemoveDialog(FriendshipModel friend) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remove Friend'),
        content: Text(
            'Are you sure you want to remove ${friend.friendUsername} from your friends list?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<FriendBloc>().add(RemoveFriend(friend.friendId));
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Remove'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        return '${difference.inMinutes}m ago';
      }
      return '${difference.inHours}h ago';
    } else if (difference.inDays == 1) {
      return 'yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}
