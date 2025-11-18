import 'package:equatable/equatable.dart';
import '../../../data/models/chat_model.dart';

enum ChatStatus { initial, loading, loaded, sending, error }

class ChatState extends Equatable {
  final ChatStatus status;
  final List<ConversationModel> conversations;
  final Map<int, List<MessageModel>> messages; // conversationId -> messages
  final Map<int, int> unreadCounts; // conversationId -> unread count
  final String? errorMessage;
  final int? activeConversationId;

  const ChatState({
    this.status = ChatStatus.initial,
    this.conversations = const [],
    this.messages = const {},
    this.unreadCounts = const {},
    this.errorMessage,
    this.activeConversationId,
  });

  int get totalUnreadCount {
    return unreadCounts.values.fold(0, (sum, count) => sum + count);
  }

  List<MessageModel> getMessagesFor(int conversationId) {
    return messages[conversationId] ?? [];
  }

  int getUnreadCountFor(int conversationId) {
    return unreadCounts[conversationId] ?? 0;
  }

  ChatState copyWith({
    ChatStatus? status,
    List<ConversationModel>? conversations,
    Map<int, List<MessageModel>>? messages,
    Map<int, int>? unreadCounts,
    String? errorMessage,
    int? activeConversationId,
  }) {
    return ChatState(
      status: status ?? this.status,
      conversations: conversations ?? this.conversations,
      messages: messages ?? this.messages,
      unreadCounts: unreadCounts ?? this.unreadCounts,
      errorMessage: errorMessage,
      activeConversationId: activeConversationId ?? this.activeConversationId,
    );
  }

  @override
  List<Object?> get props => [
        status,
        conversations,
        messages,
        unreadCounts,
        errorMessage,
        activeConversationId,
      ];
}
