import 'package:dartz/dartz.dart';
import '../../core/error/exceptions.dart';
import '../../core/error/failures.dart';
import '../datasources/remote/friend_remote_datasource.dart';
import '../models/friend_model.dart';

abstract class FriendRepository {
  Future<Either<Failure, List<FriendshipModel>>> getFriends();
  Future<Either<Failure, void>> sendFriendRequest(
    String receiverId,
    String? message,
  );
  Future<Either<Failure, List<FriendRequestModel>>> getFriendRequests();
  Future<Either<Failure, void>> acceptFriendRequest(String requestId);
  Future<Either<Failure, void>> rejectFriendRequest(String requestId);
  Future<Either<Failure, void>> removeFriend(String friendId);
}

class FriendRepositoryImpl implements FriendRepository {
  final FriendRemoteDataSource remoteDataSource;

  FriendRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, List<FriendshipModel>>> getFriends() async {
    try {
      final friends = await remoteDataSource.getFriends();
      return Right(friends);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load friends'));
    }
  }

  @override
  Future<Either<Failure, void>> sendFriendRequest(
    String receiverId,
    String? message,
  ) async {
    try {
      await remoteDataSource.sendFriendRequest(receiverId, message);
      return const Right(null);
    } on ValidationException catch (e) {
      return Left(ValidationFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to send friend request'));
    }
  }

  @override
  Future<Either<Failure, List<FriendRequestModel>>> getFriendRequests() async {
    try {
      final requests = await remoteDataSource.getFriendRequests();
      return Right(requests);
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to load friend requests'));
    }
  }

  @override
  Future<Either<Failure, void>> acceptFriendRequest(String requestId) async {
    try {
      await remoteDataSource.acceptFriendRequest(requestId);
      return const Right(null);
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to accept friend request'));
    }
  }

  @override
  Future<Either<Failure, void>> rejectFriendRequest(String requestId) async {
    try {
      await remoteDataSource.rejectFriendRequest(requestId);
      return const Right(null);
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to reject friend request'));
    }
  }

  @override
  Future<Either<Failure, void>> removeFriend(String friendId) async {
    try {
      await remoteDataSource.removeFriend(friendId);
      return const Right(null);
    } on NotFoundException catch (e) {
      return Left(NotFoundFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message));
    } catch (e) {
      return Left(ServerFailure(message: 'Failed to remove friend'));
    }
  }
}
