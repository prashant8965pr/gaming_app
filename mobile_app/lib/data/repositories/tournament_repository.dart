import 'package:dartz/dartz.dart';
import '../../core/error/exceptions.dart';
import '../../core/error/failures.dart';
import '../datasources/remote/tournament_remote_datasource.dart';
import '../models/tournament_model.dart';

abstract class TournamentRepository {
  Future<Either<Failure, List<TournamentModel>>> getTournaments({
    String? status,
    String? gameId,
    bool? isFeatured,
    int skip = 0,
    int limit = 20,
  });

  Future<Either<Failure, TournamentModel>> getTournamentById(
    String tournamentId,
  );

  Future<Either<Failure, TournamentRegistrationModel>> registerForTournament(
    String tournamentId,
  );

  Future<Either<Failure, TournamentBracketModel>> getTournamentBracket(
    String tournamentId,
  );

  Future<Either<Failure, List<TournamentRegistrationModel>>>
      getMyTournaments();
}

class TournamentRepositoryImpl implements TournamentRepository {
  final TournamentRemoteDataSource remoteDataSource;

  TournamentRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, List<TournamentModel>>> getTournaments({
    String? status,
    String? gameId,
    bool? isFeatured,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final tournaments = await remoteDataSource.getTournaments(
        status: status,
        gameId: gameId,
        isFeatured: isFeatured,
        skip: skip,
        limit: limit,
      );
      return Right(tournaments);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load tournaments'));
    }
  }

  @override
  Future<Either<Failure, TournamentModel>> getTournamentById(
    String tournamentId,
  ) async {
    try {
      final tournament = await remoteDataSource.getTournamentById(tournamentId);
      return Right(tournament);
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load tournament'));
    }
  }

  @override
  Future<Either<Failure, TournamentRegistrationModel>> registerForTournament(
    String tournamentId,
  ) async {
    try {
      final registration = await remoteDataSource.registerForTournament(
        tournamentId,
      );
      return Right(registration);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to register for tournament'));
    }
  }

  @override
  Future<Either<Failure, TournamentBracketModel>> getTournamentBracket(
    String tournamentId,
  ) async {
    try {
      final bracket = await remoteDataSource.getTournamentBracket(tournamentId);
      return Right(bracket);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load bracket'));
    }
  }

  @override
  Future<Either<Failure, List<TournamentRegistrationModel>>>
      getMyTournaments() async {
    try {
      final registrations = await remoteDataSource.getMyTournaments();
      return Right(registrations);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load my tournaments'));
    }
  }
}
