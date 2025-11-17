import 'package:dartz/dartz.dart';
import '../../core/error/exceptions.dart';
import '../../core/error/failures.dart';
import '../datasources/remote/token_remote_datasource.dart';
import '../models/token_model.dart';

abstract class TokenRepository {
  Future<Either<Failure, TokenWalletModel>> getBalance();
  Future<Either<Failure, DailyBonusResponse>> claimDailyBonus();
  Future<Either<Failure, AdRewardResponse>> earnFromAd();
}

class TokenRepositoryImpl implements TokenRepository {
  final TokenRemoteDataSource remoteDataSource;

  TokenRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, TokenWalletModel>> getBalance() async {
    try {
      final wallet = await remoteDataSource.getBalance();
      return Right(wallet);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load token balance'));
    }
  }

  @override
  Future<Either<Failure, DailyBonusResponse>> claimDailyBonus() async {
    try {
      final response = await remoteDataSource.claimDailyBonus();
      return Right(response);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to claim daily bonus'));
    }
  }

  @override
  Future<Either<Failure, AdRewardResponse>> earnFromAd() async {
    try {
      final response = await remoteDataSource.earnFromAd();
      return Right(response);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to earn tokens from ad'));
    }
  }
}
