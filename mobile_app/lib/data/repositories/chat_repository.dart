import 'package:dartz/dartz.dart';
import '../../core/error/exceptions.dart';
import '../../core/error/failures.dart';
import '../datasources/remote/chat_remote_datasource.dart';
import '../models/chat_model.dart';

abstract class ChatRepository {
  Future<Either<Failure, List<ConversationModel>>> getConversations({
    int skip = 0,
    int limit = 20,
  });

  Future<Either<Failure, ConversationModel>> getConversation(
    String conversationId,
  );

  Future<Either<Failure, MessageModel>> sendMessage(SendMessageRequest request);

  Future<Either<Failure, List<MessageModel>>> getMessages(
    String conversationId, {
    int skip = 0,
    int limit = 50,
  });

  Future<Either<Failure, void>> markMessagesAsRead(String conversationId);

  Future<Either<Failure, int>> getUnreadCount(String conversationId);

  Future<Either<Failure, MessageModel>> editMessage(
    String messageId,
    String newContent,
  );

  Future<Either<Failure, MessageModel>> deleteMessage(String messageId);

  Future<Either<Failure, void>> setTypingIndicator(String conversationId);

  Future<Either<Failure, List<TypingIndicator>>> getTypingUsers(
    String conversationId,
  );

  Future<Either<Failure, List<MessageModel>>> searchMessages(
    String query, {
    int limit = 20,
  });
}

class ChatRepositoryImpl implements ChatRepository {
  final ChatRemoteDataSource remoteDataSource;

  ChatRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, List<ConversationModel>>> getConversations({
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final conversations = await remoteDataSource.getConversations(
        skip: skip,
        limit: limit,
      );
      return Right(conversations);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load conversations'));
    }
  }

  @override
  Future<Either<Failure, ConversationModel>> getConversation(
    String conversationId,
  ) async {
    try {
      final conversation =
          await remoteDataSource.getConversation(conversationId);
      return Right(conversation);
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load conversation'));
    }
  }

  @override
  Future<Either<Failure, MessageModel>> sendMessage(
    SendMessageRequest request,
  ) async {
    try {
      final message = await remoteDataSource.sendMessage(request);
      return Right(message);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to send message'));
    }
  }

  @override
  Future<Either<Failure, List<MessageModel>>> getMessages(
    String conversationId, {
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final messages = await remoteDataSource.getMessages(
        conversationId,
        skip: skip,
        limit: limit,
      );
      return Right(messages);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load messages'));
    }
  }

  @override
  Future<Either<Failure, void>> markMessagesAsRead(
    String conversationId,
  ) async {
    try {
      await remoteDataSource.markMessagesAsRead(conversationId);
      return const Right(null);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to mark messages as read'));
    }
  }

  @override
  Future<Either<Failure, int>> getUnreadCount(String conversationId) async {
    try {
      final count = await remoteDataSource.getUnreadCount(conversationId);
      return Right(count);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to get unread count'));
    }
  }

  @override
  Future<Either<Failure, MessageModel>> editMessage(
    String messageId,
    String newContent,
  ) async {
    try {
      final message = await remoteDataSource.editMessage(messageId, newContent);
      return Right(message);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to edit message'));
    }
  }

  @override
  Future<Either<Failure, MessageModel>> deleteMessage(String messageId) async {
    try {
      final message = await remoteDataSource.deleteMessage(messageId);
      return Right(message);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to delete message'));
    }
  }

  @override
  Future<Either<Failure, void>> setTypingIndicator(
    String conversationId,
  ) async {
    try {
      await remoteDataSource.setTypingIndicator(conversationId);
      return const Right(null);
    } catch (e) {
      // Silently fail for typing indicators
      return const Right(null);
    }
  }

  @override
  Future<Either<Failure, List<TypingIndicator>>> getTypingUsers(
    String conversationId,
  ) async {
    try {
      final typingUsers =
          await remoteDataSource.getTypingUsers(conversationId);
      return Right(typingUsers);
    } catch (e) {
      // Return empty list on error
      return const Right([]);
    }
  }

  @override
  Future<Either<Failure, List<MessageModel>>> searchMessages(
    String query, {
    int limit = 20,
  }) async {
    try {
      final messages = await remoteDataSource.searchMessages(
        query,
        limit: limit,
      );
      return Right(messages);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to search messages'));
    }
  }
}
