import 'package:equatable/equatable.dart';
import '../../../data/models/friend_model.dart';

abstract class FriendState extends Equatable {
  const FriendState();

  @override
  List<Object?> get props => [];
}

class FriendInitial extends FriendState {}

class FriendLoading extends FriendState {}

class FriendsLoaded extends FriendState {
  final List<FriendshipModel> friends;

  const FriendsLoaded(this.friends);

  @override
  List<Object?> get props => [friends];
}

class FriendRequestSending extends FriendState {}

class FriendRequestSent extends FriendState {}

class FriendRequestsLoading extends FriendState {}

class FriendRequestsLoaded extends FriendState {
  final List<FriendRequestModel> requests;

  const FriendRequestsLoaded(this.requests);

  @override
  List<Object?> get props => [requests];
}

class FriendRequestAccepting extends FriendState {}

class FriendRequestAccepted extends FriendState {}

class FriendRequestRejecting extends FriendState {}

class FriendRequestRejected extends FriendState {}

class FriendRemoving extends FriendState {}

class FriendRemoved extends FriendState {}

class FriendError extends FriendState {
  final String message;

  const FriendError(this.message);

  @override
  List<Object?> get props => [message];
}
