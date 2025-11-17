import 'package:equatable/equatable.dart';

abstract class FriendEvent extends Equatable {
  const FriendEvent();

  @override
  List<Object?> get props => [];
}

class LoadFriends extends FriendEvent {
  final bool refresh;

  const LoadFriends({this.refresh = false});

  @override
  List<Object?> get props => [refresh];
}

class SendFriendRequest extends FriendEvent {
  final String receiverId;
  final String? message;

  const SendFriendRequest({
    required this.receiverId,
    this.message,
  });

  @override
  List<Object?> get props => [receiverId, message];
}

class LoadFriendRequests extends FriendEvent {
  final bool refresh;

  const LoadFriendRequests({this.refresh = false});

  @override
  List<Object?> get props => [refresh];
}

class AcceptFriendRequest extends FriendEvent {
  final String requestId;

  const AcceptFriendRequest(this.requestId);

  @override
  List<Object?> get props => [requestId];
}

class RejectFriendRequest extends FriendEvent {
  final String requestId;

  const RejectFriendRequest(this.requestId);

  @override
  List<Object?> get props => [requestId];
}

class RemoveFriend extends FriendEvent {
  final String friendId;

  const RemoveFriend(this.friendId);

  @override
  List<Object?> get props => [friendId];
}
