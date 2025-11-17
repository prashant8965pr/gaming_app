import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../../../core/error/exceptions.dart';
import '../../../core/utils/auth_storage.dart';
import '../../models/chat_model.dart';

abstract class ChatRemoteDataSource {
  Future<List<ConversationModel>> getConversations({int skip = 0, int limit = 20});
  Future<ConversationModel> getConversation(String conversationId);
  Future<MessageModel> sendMessage(SendMessageRequest request);
  Future<List<MessageModel>> getMessages(String conversationId, {int skip = 0, int limit = 50});
  Future<void> markMessagesAsRead(String conversationId);
  Future<int> getUnreadCount(String conversationId);
  Future<MessageModel> editMessage(String messageId, String newContent);
  Future<MessageModel> deleteMessage(String messageId);
  Future<void> setTypingIndicator(String conversationId);
  Future<List<TypingIndicator>> getTypingUsers(String conversationId);
  Future<List<MessageModel>> searchMessages(String query, {int limit = 20});
}

class ChatRemoteDataSourceImpl implements ChatRemoteDataSource {
  final http.Client client;
  final AuthStorage authStorage;

  ChatRemoteDataSourceImpl({
    required this.client,
    required this.authStorage,
  });

  Future<Map<String, String>> _getHeaders() async {
    final token = await authStorage.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  @override
  Future<List<ConversationModel>> getConversations({
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/conversations')
          .replace(queryParameters: {
        'skip': skip.toString(),
        'limit': limit.toString(),
      });

      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final conversationsData = jsonResponse['data']['conversations'] as List;
        return conversationsData
            .map((conv) => ConversationModel.fromJson(conv))
            .toList();
      } else {
        throw ServerException(message: 'Failed to load conversations');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<ConversationModel> getConversation(String conversationId) async {
    try {
      final uri =
          Uri.parse('${ApiConfig.baseUrl}/chat/conversations/$conversationId');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return ConversationModel.fromJson(jsonResponse['data']['conversation']);
      } else if (response.statusCode == 404) {
        throw NotFoundException(message: 'Conversation not found');
      } else {
        throw ServerException(message: 'Failed to load conversation');
      }
    } catch (e) {
      if (e is NotFoundException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<MessageModel> sendMessage(SendMessageRequest request) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/send');
      final headers = await _getHeaders();
      final body = json.encode(request.toJson());

      final response = await client.post(uri, headers: headers, body: body);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return MessageModel.fromJson(jsonResponse['data']['message']);
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(
          message: jsonResponse['detail'] ?? 'Failed to send message',
        );
      } else {
        throw ServerException(message: 'Failed to send message');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<List<MessageModel>> getMessages(
    String conversationId, {
    int skip = 0,
    int limit = 50,
  }) async {
    try {
      final uri =
          Uri.parse('${ApiConfig.baseUrl}/chat/messages/$conversationId')
              .replace(queryParameters: {
        'skip': skip.toString(),
        'limit': limit.toString(),
      });

      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final messagesData = jsonResponse['data']['messages'] as List;
        return messagesData
            .map((message) => MessageModel.fromJson(message))
            .toList();
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(message: jsonResponse['detail']);
      } else {
        throw ServerException(message: 'Failed to load messages');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> markMessagesAsRead(String conversationId) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/chat/messages/$conversationId/mark-read',
      );
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode != 200) {
        throw ServerException(message: 'Failed to mark messages as read');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<int> getUnreadCount(String conversationId) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/chat/messages/$conversationId/unread-count',
      );
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return jsonResponse['data']['unread_count'];
      } else {
        throw ServerException(message: 'Failed to get unread count');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<MessageModel> editMessage(String messageId, String newContent) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/messages/$messageId');
      final headers = await _getHeaders();
      final body = json.encode({'content': newContent});

      final response = await client.put(uri, headers: headers, body: body);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return MessageModel.fromJson(jsonResponse['data']['message']);
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(message: jsonResponse['detail']);
      } else {
        throw ServerException(message: 'Failed to edit message');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<MessageModel> deleteMessage(String messageId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/messages/$messageId');
      final headers = await _getHeaders();

      final response = await client.delete(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return MessageModel.fromJson(jsonResponse['data']['message']);
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(message: jsonResponse['detail']);
      } else {
        throw ServerException(message: 'Failed to delete message');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> setTypingIndicator(String conversationId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/typing');
      final headers = await _getHeaders();
      final body = json.encode({'conversation_id': conversationId});

      final response = await client.post(uri, headers: headers, body: body);

      if (response.statusCode != 200) {
        // Don't throw error for typing indicator failure
        print('Failed to set typing indicator');
      }
    } catch (e) {
      // Silently fail for typing indicators
      print('Error setting typing indicator: $e');
    }
  }

  @override
  Future<List<TypingIndicator>> getTypingUsers(String conversationId) async {
    try {
      final uri =
          Uri.parse('${ApiConfig.baseUrl}/chat/typing/$conversationId');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final typingData = jsonResponse['data']['typing_users'] as List;
        return typingData
            .map((user) => TypingIndicator.fromJson(user))
            .toList();
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  @override
  Future<List<MessageModel>> searchMessages(
    String query, {
    int limit = 20,
  }) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/chat/search')
          .replace(queryParameters: {
        'query': query,
        'limit': limit.toString(),
      });

      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final resultsData = jsonResponse['data']['results'] as List;
        return resultsData
            .map((message) => MessageModel.fromJson(message))
            .toList();
      } else {
        throw ServerException(message: 'Failed to search messages');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }
}
