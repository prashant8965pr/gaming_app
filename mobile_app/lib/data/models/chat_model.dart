import 'package:equatable/equatable.dart';

class ConversationModel extends Equatable {
  final String id;
  final String conversationType;
  final String? user1Id;
  final String? user2Id;
  final String? name;
  final String? avatar;
  final DateTime? lastMessageAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  // Additional fields from API
  final UserPreview? otherUser;
  final int unreadCount;
  final MessageModel? lastMessage;

  const ConversationModel({
    required this.id,
    required this.conversationType,
    this.user1Id,
    this.user2Id,
    this.name,
    this.avatar,
    this.lastMessageAt,
    required this.createdAt,
    required this.updatedAt,
    this.otherUser,
    this.unreadCount = 0,
    this.lastMessage,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id'],
      conversationType: json['conversation_type'],
      user1Id: json['user1_id'],
      user2Id: json['user2_id'],
      name: json['name'],
      avatar: json['avatar'],
      lastMessageAt: json['last_message_at'] != null
          ? DateTime.parse(json['last_message_at'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      otherUser: json['other_user'] != null
          ? UserPreview.fromJson(json['other_user'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
      lastMessage: json['last_message'] != null
          ? MessageModel.fromJson(json['last_message'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversation_type': conversationType,
      'user1_id': user1Id,
      'user2_id': user2Id,
      'name': name,
      'avatar': avatar,
      'last_message_at': lastMessageAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [
        id,
        conversationType,
        user1Id,
        user2Id,
        name,
        avatar,
        lastMessageAt,
        createdAt,
        updatedAt,
        otherUser,
        unreadCount,
        lastMessage,
      ];
}

class MessageModel extends Equatable {
  final String id;
  final String conversationId;
  final String senderId;
  final String messageType;
  final String content;
  final Map<String, dynamic>? metadata;
  final bool isEdited;
  final bool isDeleted;
  final DateTime sentAt;
  final DateTime? editedAt;

  // Additional fields
  final bool? isRead;
  final String? senderUsername;
  final String? senderAvatar;

  const MessageModel({
    required this.id,
    required this.conversationId,
    required this.senderId,
    required this.messageType,
    required this.content,
    this.metadata,
    required this.isEdited,
    required this.isDeleted,
    required this.sentAt,
    this.editedAt,
    this.isRead,
    this.senderUsername,
    this.senderAvatar,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'],
      conversationId: json['conversation_id'],
      senderId: json['sender_id'],
      messageType: json['message_type'],
      content: json['content'],
      metadata: json['metadata'],
      isEdited: json['is_edited'] ?? false,
      isDeleted: json['is_deleted'] ?? false,
      sentAt: DateTime.parse(json['sent_at']),
      editedAt:
          json['edited_at'] != null ? DateTime.parse(json['edited_at']) : null,
      isRead: json['is_read'],
      senderUsername: json['sender_username'],
      senderAvatar: json['sender_avatar'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversation_id': conversationId,
      'sender_id': senderId,
      'message_type': messageType,
      'content': content,
      'metadata': metadata,
      'is_edited': isEdited,
      'is_deleted': isDeleted,
      'sent_at': sentAt.toIso8601String(),
      'edited_at': editedAt?.toIso8601String(),
    };
  }

  bool get isTextMessage => messageType == 'text';
  bool get isImageMessage => messageType == 'image';
  bool get isGameInvite => messageType == 'game_invite';
  bool get isSystemMessage => messageType == 'system';

  String get displayContent {
    if (isDeleted) return '[Message deleted]';
    if (isImageMessage) return '📷 Image';
    if (isGameInvite) return '🎮 Game Invitation';
    return content;
  }

  @override
  List<Object?> get props => [
        id,
        conversationId,
        senderId,
        messageType,
        content,
        metadata,
        isEdited,
        isDeleted,
        sentAt,
        editedAt,
        isRead,
        senderUsername,
        senderAvatar,
      ];
}

class UserPreview extends Equatable {
  final String id;
  final String username;
  final String? avatar;
  final bool? isOnline;

  const UserPreview({
    required this.id,
    required this.username,
    this.avatar,
    this.isOnline,
  });

  factory UserPreview.fromJson(Map<String, dynamic> json) {
    return UserPreview(
      id: json['id'],
      username: json['username'],
      avatar: json['avatar'],
      isOnline: json['is_online'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'avatar': avatar,
      'is_online': isOnline,
    };
  }

  @override
  List<Object?> get props => [id, username, avatar, isOnline];
}

class TypingIndicator extends Equatable {
  final String userId;
  final String username;

  const TypingIndicator({
    required this.userId,
    required this.username,
  });

  factory TypingIndicator.fromJson(Map<String, dynamic> json) {
    return TypingIndicator(
      userId: json['user_id'],
      username: json['username'],
    );
  }

  @override
  List<Object?> get props => [userId, username];
}

class SendMessageRequest extends Equatable {
  final String receiverId;
  final String content;
  final String messageType;
  final Map<String, dynamic>? metadata;

  const SendMessageRequest({
    required this.receiverId,
    required this.content,
    this.messageType = 'text',
    this.metadata,
  });

  Map<String, dynamic> toJson() {
    return {
      'receiver_id': receiverId,
      'content': content,
      'message_type': messageType,
      'metadata': metadata,
    };
  }

  @override
  List<Object?> get props => [receiverId, content, messageType, metadata];
}
