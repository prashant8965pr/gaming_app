import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/chat_repository.dart';
import 'chat_event.dart';
import 'chat_state.dart';

class ChatBloc extends Bloc<ChatEvent, ChatState> {
  final ChatRepository chatRepository;

  ChatBloc({required this.chatRepository}) : super(const ChatState()) {
    on<LoadConversations>(_onLoadConversations);
    on<LoadMessages>(_onLoadMessages);
    on<SendMessage>(_onSendMessage);
    on<MarkMessageAsRead>(_onMarkMessageAsRead);
    on<DeleteMessage>(_onDeleteMessage);
    on<SendTypingIndicator>(_onSendTypingIndicator);
    on<SearchMessages>(_onSearchMessages);
  }

  Future<void> _onLoadConversations(
    LoadConversations event,
    Emitter<ChatState> emit,
  ) async {
    emit(state.copyWith(status: ChatStatus.loading));

    try {
      final result = await chatRepository.getConversations();

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: ChatStatus.error,
            errorMessage: failure.message,
          ));
        },
        (conversations) {
          emit(state.copyWith(
            status: ChatStatus.loaded,
            conversations: conversations,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: ChatStatus.error,
        errorMessage: 'Failed to load conversations: $e',
      ));
    }
  }

  Future<void> _onLoadMessages(
    LoadMessages event,
    Emitter<ChatState> emit,
  ) async {
    emit(state.copyWith(
      status: ChatStatus.loading,
      activeConversationId: event.conversationId,
    ));

    try {
      final result = await chatRepository.getMessages(
        conversationId: event.conversationId,
        page: event.page,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: ChatStatus.error,
            errorMessage: failure.message,
          ));
        },
        (newMessages) {
          final currentMessages = state.getMessagesFor(event.conversationId);
          final updatedMessages = event.page == 1
              ? newMessages
              : [...currentMessages, ...newMessages];

          final updatedMessagesMap =
              Map<int, List<MessageModel>>.from(state.messages);
          updatedMessagesMap[event.conversationId] = updatedMessages;

          emit(state.copyWith(
            status: ChatStatus.loaded,
            messages: updatedMessagesMap,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: ChatStatus.error,
        errorMessage: 'Failed to load messages: $e',
      ));
    }
  }

  Future<void> _onSendMessage(
    SendMessage event,
    Emitter<ChatState> emit,
  ) async {
    emit(state.copyWith(status: ChatStatus.sending));

    try {
      final result = await chatRepository.sendMessage(
        receiverId: event.receiverId,
        message: event.message,
        imageUrl: event.imageUrl,
        gameInviteData: event.gameInviteData,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: ChatStatus.error,
            errorMessage: failure.message,
          ));
        },
        (sentMessage) {
          emit(state.copyWith(status: ChatStatus.loaded));
          // Reload conversations to update latest message
          add(const LoadConversations());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: ChatStatus.error,
        errorMessage: 'Failed to send message: $e',
      ));
    }
  }

  Future<void> _onMarkMessageAsRead(
    MarkMessageAsRead event,
    Emitter<ChatState> emit,
  ) async {
    try {
      await chatRepository.markAsRead(messageId: event.messageId);
      // Update unread counts
      add(const LoadConversations());
    } catch (e) {
      // Silent fail
    }
  }

  Future<void> _onDeleteMessage(
    DeleteMessage event,
    Emitter<ChatState> emit,
  ) async {
    try {
      final result = await chatRepository.deleteMessage(messageId: event.messageId);

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: ChatStatus.error,
            errorMessage: failure.message,
          ));
        },
        (_) {
          // Reload messages for active conversation
          if (state.activeConversationId != null) {
            add(LoadMessages(conversationId: state.activeConversationId!));
          }
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: ChatStatus.error,
        errorMessage: 'Failed to delete message: $e',
      ));
    }
  }

  Future<void> _onSendTypingIndicator(
    SendTypingIndicator event,
    Emitter<ChatState> emit,
  ) async {
    try {
      await chatRepository.sendTypingIndicator(receiverId: event.receiverId);
    } catch (e) {
      // Silent fail
    }
  }

  Future<void> _onSearchMessages(
    SearchMessages event,
    Emitter<ChatState> emit,
  ) async {
    emit(state.copyWith(status: ChatStatus.loading));

    try {
      final result = await chatRepository.searchMessages(query: event.query);

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: ChatStatus.error,
            errorMessage: failure.message,
          ));
        },
        (searchResults) {
          emit(state.copyWith(status: ChatStatus.loaded));
          // Handle search results
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: ChatStatus.error,
        errorMessage: 'Failed to search messages: $e',
      ));
    }
  }
}
