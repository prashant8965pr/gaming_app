import 'package:equatable/equatable.dart';

abstract class ChatEvent extends Equatable {
  const ChatEvent();

  @override
  List<Object?> get props => [];
}

class LoadConversations extends ChatEvent {
  const LoadConversations();
}

class LoadMessages extends ChatEvent {
  final int conversationId;
  final int page;

  const LoadMessages({
    required this.conversationId,
    this.page = 1,
  });

  @override
  List<Object?> get props => [conversationId, page];
}

class SendMessage extends ChatEvent {
  final int receiverId;
  final String message;
  final String? imageUrl;
  final String? gameInviteData;

  const SendMessage({
    required this.receiverId,
    required this.message,
    this.imageUrl,
    this.gameInviteData,
  });

  @override
  List<Object?> get props => [receiverId, message, imageUrl, gameInviteData];
}

class MarkMessageAsRead extends ChatEvent {
  final int messageId;

  const MarkMessageAsRead(this.messageId);

  @override
  List<Object?> get props => [messageId];
}

class DeleteMessage extends ChatEvent {
  final int messageId;

  const DeleteMessage(this.messageId);

  @override
  List<Object?> get props => [messageId];
}

class SendTypingIndicator extends ChatEvent {
  final int receiverId;

  const SendTypingIndicator(this.receiverId);

  @override
  List<Object?> get props => [receiverId];
}

class SearchMessages extends ChatEvent {
  final String query;

  const SearchMessages(this.query);

  @override
  List<Object?> get props => [query];
}
