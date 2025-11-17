import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../../../core/error/exceptions.dart';
import '../../../core/utils/auth_storage.dart';
import '../../models/friend_model.dart';

abstract class FriendRemoteDataSource {
  Future<List<FriendshipModel>> getFriends();
  Future<void> sendFriendRequest(String receiverId, String? message);
  Future<List<FriendRequestModel>> getFriendRequests();
  Future<void> acceptFriendRequest(String requestId);
  Future<void> rejectFriendRequest(String requestId);
  Future<void> removeFriend(String friendId);
}

class FriendRemoteDataSourceImpl implements FriendRemoteDataSource {
  final http.Client client;
  final AuthStorage authStorage;

  FriendRemoteDataSourceImpl({
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
  Future<List<FriendshipModel>> getFriends() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/friends');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final friendsData = jsonResponse['data']['friends'] as List;
        return friendsData
            .map((friend) => FriendshipModel.fromJson(friend))
            .toList();
      } else {
        throw ServerException(message: 'Failed to load friends');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> sendFriendRequest(String receiverId, String? message) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/friends/request');
      final headers = await _getHeaders();
      final body = json.encode({
        'receiver_id': receiverId,
        'message': message,
      });

      final response = await client.post(uri, headers: headers, body: body);

      if (response.statusCode == 200) {
        return;
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(
          message: jsonResponse['detail'] ?? 'Cannot send friend request',
        );
      } else {
        throw ServerException(message: 'Failed to send friend request');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<List<FriendRequestModel>> getFriendRequests() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/friends/requests');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final requestsData = jsonResponse['data']['requests'] as List;
        return requestsData
            .map((request) => FriendRequestModel.fromJson(request))
            .toList();
      } else {
        throw ServerException(message: 'Failed to load friend requests');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> acceptFriendRequest(String requestId) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/friends/requests/$requestId/accept',
      );
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode == 200) {
        return;
      } else if (response.statusCode == 404) {
        throw NotFoundException(message: 'Friend request not found');
      } else {
        throw ServerException(message: 'Failed to accept friend request');
      }
    } catch (e) {
      if (e is NotFoundException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> rejectFriendRequest(String requestId) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/friends/requests/$requestId/reject',
      );
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode == 200) {
        return;
      } else if (response.statusCode == 404) {
        throw NotFoundException(message: 'Friend request not found');
      } else {
        throw ServerException(message: 'Failed to reject friend request');
      }
    } catch (e) {
      if (e is NotFoundException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<void> removeFriend(String friendId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/friends/$friendId');
      final headers = await _getHeaders();
      final response = await client.delete(uri, headers: headers);

      if (response.statusCode == 200) {
        return;
      } else if (response.statusCode == 404) {
        throw NotFoundException(message: 'Friend not found');
      } else {
        throw ServerException(message: 'Failed to remove friend');
      }
    } catch (e) {
      if (e is NotFoundException) rethrow;
      throw ServerException(message: e.toString());
    }
  }
}
