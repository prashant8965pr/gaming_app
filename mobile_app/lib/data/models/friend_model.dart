import 'package:equatable/equatable.dart';

class FriendshipModel extends Equatable {
  final String id;
  final String userId;
  final String friendId;
  final String friendUsername;
  final String? friendAvatar;
  final String status;
  final bool isOnline;
  final DateTime? lastSeen;
  final DateTime createdAt;

  const FriendshipModel({
    required this.id,
    required this.userId,
    required this.friendId,
    required this.friendUsername,
    this.friendAvatar,
    required this.status,
    required this.isOnline,
    this.lastSeen,
    required this.createdAt,
  });

  factory FriendshipModel.fromJson(Map<String, dynamic> json) {
    return FriendshipModel(
      id: json['id'],
      userId: json['user_id'],
      friendId: json['friend_id'],
      friendUsername: json['friend_username'] ?? 'Unknown',
      friendAvatar: json['friend_avatar'],
      status: json['status'],
      isOnline: json['is_online'] ?? false,
      lastSeen: json['last_seen'] != null
          ? DateTime.parse(json['last_seen'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'friend_id': friendId,
      'friend_username': friendUsername,
      'friend_avatar': friendAvatar,
      'status': status,
      'is_online': isOnline,
      'last_seen': lastSeen?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
    };
  }

  String get onlineStatus {
    if (isOnline) return 'Online';
    if (lastSeen == null) return 'Offline';

    final now = DateTime.now();
    final difference = now.difference(lastSeen!);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return 'Long time ago';
    }
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        friendId,
        friendUsername,
        friendAvatar,
        status,
        isOnline,
        lastSeen,
        createdAt,
      ];
}

class FriendRequestModel extends Equatable {
  final String id;
  final String senderId;
  final String receiverId;
  final String senderUsername;
  final String? senderAvatar;
  final String status;
  final String? message;
  final DateTime createdAt;
  final DateTime? respondedAt;

  const FriendRequestModel({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.senderUsername,
    this.senderAvatar,
    required this.status,
    this.message,
    required this.createdAt,
    this.respondedAt,
  });

  factory FriendRequestModel.fromJson(Map<String, dynamic> json) {
    return FriendRequestModel(
      id: json['id'],
      senderId: json['sender_id'],
      receiverId: json['receiver_id'],
      senderUsername: json['sender_username'] ?? 'Unknown',
      senderAvatar: json['sender_avatar'],
      status: json['status'],
      message: json['message'],
      createdAt: DateTime.parse(json['created_at']),
      respondedAt: json['responded_at'] != null
          ? DateTime.parse(json['responded_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'sender_username': senderUsername,
      'sender_avatar': senderAvatar,
      'status': status,
      'message': message,
      'created_at': createdAt.toIso8601String(),
      'responded_at': respondedAt?.toIso8601String(),
    };
  }

  bool get isPending => status == 'pending';
  bool get isAccepted => status == 'accepted';
  bool get isRejected => status == 'rejected';

  String get statusDisplay {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'accepted':
        return 'Accepted';
      case 'rejected':
        return 'Declined';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  @override
  List<Object?> get props => [
        id,
        senderId,
        receiverId,
        senderUsername,
        senderAvatar,
        status,
        message,
        createdAt,
        respondedAt,
      ];
}

class GameInvitationModel extends Equatable {
  final String id;
  final String senderId;
  final String receiverId;
  final String senderUsername;
  final String? senderAvatar;
  final String gameSessionId;
  final String gameId;
  final String gameName;
  final String? gameIcon;
  final String status;
  final DateTime expiresAt;
  final DateTime createdAt;

  const GameInvitationModel({
    required this.id,
    required this.senderId,
    required this.receiverId,
    required this.senderUsername,
    this.senderAvatar,
    required this.gameSessionId,
    required this.gameId,
    required this.gameName,
    this.gameIcon,
    required this.status,
    required this.expiresAt,
    required this.createdAt,
  });

  factory GameInvitationModel.fromJson(Map<String, dynamic> json) {
    return GameInvitationModel(
      id: json['id'],
      senderId: json['sender_id'],
      receiverId: json['receiver_id'],
      senderUsername: json['sender_username'] ?? 'Unknown',
      senderAvatar: json['sender_avatar'],
      gameSessionId: json['game_session_id'],
      gameId: json['game_id'],
      gameName: json['game_name'] ?? 'Game',
      gameIcon: json['game_icon'],
      status: json['status'],
      expiresAt: DateTime.parse(json['expires_at']),
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sender_id': senderId,
      'receiver_id': receiverId,
      'sender_username': senderUsername,
      'sender_avatar': senderAvatar,
      'game_session_id': gameSessionId,
      'game_id': gameId,
      'game_name': gameName,
      'game_icon': gameIcon,
      'status': status,
      'expires_at': expiresAt.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
    };
  }

  bool get isExpired => DateTime.now().isAfter(expiresAt);
  bool get isPending => status == 'pending' && !isExpired;
  bool get isAccepted => status == 'accepted';
  bool get isRejected => status == 'rejected';

  Duration get timeRemaining {
    if (isExpired) return Duration.zero;
    return expiresAt.difference(DateTime.now());
  }

  String get timeRemainingDisplay {
    if (isExpired) return 'Expired';

    final remaining = timeRemaining;
    if (remaining.inMinutes < 1) {
      return '${remaining.inSeconds}s left';
    } else if (remaining.inMinutes < 60) {
      return '${remaining.inMinutes}m left';
    } else {
      return '${remaining.inHours}h ${remaining.inMinutes % 60}m left';
    }
  }

  @override
  List<Object?> get props => [
        id,
        senderId,
        receiverId,
        senderUsername,
        senderAvatar,
        gameSessionId,
        gameId,
        gameName,
        gameIcon,
        status,
        expiresAt,
        createdAt,
      ];
}

class FriendSearchResult extends Equatable {
  final String id;
  final String username;
  final String? avatar;
  final int level;
  final int totalWins;
  final bool isOnline;
  final bool isFriend;
  final bool hasPendingRequest;

  const FriendSearchResult({
    required this.id,
    required this.username,
    this.avatar,
    required this.level,
    required this.totalWins,
    required this.isOnline,
    required this.isFriend,
    required this.hasPendingRequest,
  });

  factory FriendSearchResult.fromJson(Map<String, dynamic> json) {
    return FriendSearchResult(
      id: json['id'],
      username: json['username'],
      avatar: json['avatar'],
      level: json['level'] ?? 1,
      totalWins: json['total_wins'] ?? 0,
      isOnline: json['is_online'] ?? false,
      isFriend: json['is_friend'] ?? false,
      hasPendingRequest: json['has_pending_request'] ?? false,
    );
  }

  @override
  List<Object?> get props => [
        id,
        username,
        avatar,
        level,
        totalWins,
        isOnline,
        isFriend,
        hasPendingRequest,
      ];
}

class FriendLeaderboardEntry extends Equatable {
  final int rank;
  final String userId;
  final String username;
  final String? avatar;
  final int score;
  final int totalWins;
  final int totalGames;
  final bool isCurrentUser;
  final bool isOnline;

  const FriendLeaderboardEntry({
    required this.rank,
    required this.userId,
    required this.username,
    this.avatar,
    required this.score,
    required this.totalWins,
    required this.totalGames,
    required this.isCurrentUser,
    required this.isOnline,
  });

  factory FriendLeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return FriendLeaderboardEntry(
      rank: json['rank'],
      userId: json['user_id'],
      username: json['username'],
      avatar: json['avatar'],
      score: json['score'],
      totalWins: json['total_wins'],
      totalGames: json['total_games'],
      isCurrentUser: json['is_current_user'] ?? false,
      isOnline: json['is_online'] ?? false,
    );
  }

  double get winRate =>
      totalGames > 0 ? (totalWins / totalGames) * 100 : 0.0;

  @override
  List<Object?> get props => [
        rank,
        userId,
        username,
        avatar,
        score,
        totalWins,
        totalGames,
        isCurrentUser,
        isOnline,
      ];
}
