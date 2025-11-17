import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../../../core/error/exceptions.dart';
import '../../../core/utils/auth_storage.dart';
import '../../models/tournament_model.dart';

abstract class TournamentRemoteDataSource {
  Future<List<TournamentModel>> getTournaments({
    String? status,
    String? gameId,
    bool? isFeatured,
    int skip = 0,
    int limit = 20,
  });

  Future<TournamentModel> getTournamentById(String tournamentId);

  Future<TournamentRegistrationModel> registerForTournament(String tournamentId);

  Future<TournamentBracketModel> getTournamentBracket(String tournamentId);

  Future<List<TournamentRegistrationModel>> getMyTournaments();
}

class TournamentRemoteDataSourceImpl implements TournamentRemoteDataSource {
  final http.Client client;
  final AuthStorage authStorage;

  TournamentRemoteDataSourceImpl({
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
  Future<List<TournamentModel>> getTournaments({
    String? status,
    String? gameId,
    bool? isFeatured,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final queryParams = <String, String>{
        'skip': skip.toString(),
        'limit': limit.toString(),
      };

      if (status != null) queryParams['status'] = status;
      if (gameId != null) queryParams['game_id'] = gameId;
      if (isFeatured != null) queryParams['is_featured'] = isFeatured.toString();

      final uri = Uri.parse('${ApiConfig.baseUrl}/tournaments')
          .replace(queryParameters: queryParams);

      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final tournamentsData = jsonResponse['data']['tournaments'] as List;
        return tournamentsData
            .map((tournament) => TournamentModel.fromJson(tournament))
            .toList();
      } else {
        throw ServerException(message: 'Failed to load tournaments');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<TournamentModel> getTournamentById(String tournamentId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/tournaments/$tournamentId');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return TournamentModel.fromJson(jsonResponse['data']['tournament']);
      } else if (response.statusCode == 404) {
        throw NotFoundException(message: 'Tournament not found');
      } else {
        throw ServerException(message: 'Failed to load tournament');
      }
    } catch (e) {
      if (e is NotFoundException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<TournamentRegistrationModel> registerForTournament(
    String tournamentId,
  ) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/tournaments/$tournamentId/register',
      );
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return TournamentRegistrationModel.fromJson(
          jsonResponse['data']['registration'],
        );
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(
          message: jsonResponse['detail'] ?? 'Registration failed',
        );
      } else {
        throw ServerException(message: 'Failed to register for tournament');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<TournamentBracketModel> getTournamentBracket(
    String tournamentId,
  ) async {
    try {
      final uri = Uri.parse(
        '${ApiConfig.baseUrl}/tournaments/$tournamentId/bracket',
      );
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final bracketData = jsonResponse['data']['bracket'];

        if (bracketData == null) {
          throw ValidationException(message: 'Bracket not generated yet');
        }

        return TournamentBracketModel.fromJson(bracketData);
      } else {
        throw ServerException(message: 'Failed to load bracket');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<List<TournamentRegistrationModel>> getMyTournaments() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/tournaments/my/tournaments');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        final registrationsData =
            jsonResponse['data']['registrations'] as List;
        return registrationsData
            .map((reg) => TournamentRegistrationModel.fromJson(reg))
            .toList();
      } else {
        throw ServerException(message: 'Failed to load my tournaments');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }
}
