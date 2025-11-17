import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../../../core/error/exceptions.dart';
import '../../../core/utils/auth_storage.dart';
import '../../models/token_model.dart';

abstract class TokenRemoteDataSource {
  Future<TokenWalletModel> getBalance();
  Future<DailyBonusResponse> claimDailyBonus();
  Future<AdRewardResponse> earnFromAd();
}

class TokenRemoteDataSourceImpl implements TokenRemoteDataSource {
  final http.Client client;
  final AuthStorage authStorage;

  TokenRemoteDataSourceImpl({
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
  Future<TokenWalletModel> getBalance() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/tokens/balance');
      final headers = await _getHeaders();
      final response = await client.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return TokenWalletModel.fromJson(jsonResponse['data']['wallet']);
      } else {
        throw ServerException(message: 'Failed to load token balance');
      }
    } catch (e) {
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<DailyBonusResponse> claimDailyBonus() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/tokens/daily-bonus');
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return DailyBonusResponse.fromJson(jsonResponse['data']);
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(
          message: jsonResponse['detail'] ?? 'Cannot claim daily bonus',
        );
      } else {
        throw ServerException(message: 'Failed to claim daily bonus');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }

  @override
  Future<AdRewardResponse> earnFromAd() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/tokens/earn-from-ad');
      final headers = await _getHeaders();
      final response = await client.post(uri, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(response.body);
        return AdRewardResponse.fromJson(jsonResponse['data']);
      } else if (response.statusCode == 400) {
        final jsonResponse = json.decode(response.body);
        throw ValidationException(
          message: jsonResponse['detail'] ?? 'Cannot earn from ad',
        );
      } else {
        throw ServerException(message: 'Failed to earn tokens from ad');
      }
    } catch (e) {
      if (e is ValidationException) rethrow;
      throw ServerException(message: e.toString());
    }
  }
}
