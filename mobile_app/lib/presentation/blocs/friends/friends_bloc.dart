import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../data/models/friend_model.dart';
import '../../../data/repositories/friends_repository.dart';
import '../../../core/errors/failures.dart';

// Events
abstract class FriendsEvent extends Equatable {
  const FriendsEvent();
  @override
  List<Object?> get props => [];
}

class LoadFriends extends FriendsEvent {}
class LoadFriendRequests extends FriendsEvent {}
class SendFriendRequest extends FriendsEvent {
  final int userId;
  const SendFriendRequest(this.userId);
  @override
  List<Object?> get props => [userId];
}

class AcceptFriendRequest extends FriendsEvent {
  final int requestId;
  const AcceptFriendRequest(this.requestId);
  @override
  List<Object?> get props => [requestId];
}

class RejectFriendRequest extends FriendsEvent {
  final int requestId;
  const RejectFriendRequest(this.requestId);
  @override
  List<Object?> get props => [requestId];
}

class RemoveFriend extends FriendsEvent {
  final int friendshipId;
  const RemoveFriend(this.friendshipId);
  @override
  List<Object?> get props => [friendshipId];
}

// State
enum FriendsStatus { initial, loading, loaded, error }

class FriendsState extends Equatable {
  final FriendsStatus status;
  final List<FriendModel> friends;
  final List<FriendRequestModel> requests;
  final String? errorMessage;

  const FriendsState({
    this.status = FriendsStatus.initial,
    this.friends = const [],
    this.requests = const [],
    this.errorMessage,
  });

  FriendsState copyWith({
    FriendsStatus? status,
    List<FriendModel>? friends,
    List<FriendRequestModel>? requests,
    String? errorMessage,
  }) {
    return FriendsState(
      status: status ?? this.status,
      friends: friends ?? this.friends,
      requests: requests ?? this.requests,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, friends, requests, errorMessage];
}

// BLoC
class FriendsBloc extends Bloc<FriendsEvent, FriendsState> {
  final FriendsRepository friendsRepository;

  FriendsBloc({required this.friendsRepository}) : super(const FriendsState()) {
    on<LoadFriends>(_onLoadFriends);
    on<LoadFriendRequests>(_onLoadFriendRequests);
    on<SendFriendRequest>(_onSendFriendRequest);
    on<AcceptFriendRequest>(_onAcceptFriendRequest);
    on<RejectFriendRequest>(_onRejectFriendRequest);
    on<RemoveFriend>(_onRemoveFriend);
  }

  Future<void> _onLoadFriends(LoadFriends event, Emitter<FriendsState> emit) async {
    emit(state.copyWith(status: FriendsStatus.loading));
    final result = await friendsRepository.getFriends();
    result.fold(
      (failure) => emit(state.copyWith(
        status: FriendsStatus.error,
        errorMessage: failure.message,
      )),
      (friends) => emit(state.copyWith(
        status: FriendsStatus.loaded,
        friends: friends,
      )),
    );
  }

  Future<void> _onLoadFriendRequests(LoadFriendRequests event, Emitter<FriendsState> emit) async {
    final result = await friendsRepository.getFriendRequests();
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (requests) => emit(state.copyWith(requests: requests)),
    );
  }

  Future<void> _onSendFriendRequest(SendFriendRequest event, Emitter<FriendsState> emit) async {
    final result = await friendsRepository.sendFriendRequest(userId: event.userId);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) => add(LoadFriendRequests()),
    );
  }

  Future<void> _onAcceptFriendRequest(AcceptFriendRequest event, Emitter<FriendsState> emit) async {
    final result = await friendsRepository.acceptFriendRequest(requestId: event.requestId);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) {
        add(LoadFriends());
        add(LoadFriendRequests());
      },
    );
  }

  Future<void> _onRejectFriendRequest(RejectFriendRequest event, Emitter<FriendsState> emit) async {
    final result = await friendsRepository.rejectFriendRequest(requestId: event.requestId);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) => add(LoadFriendRequests()),
    );
  }

  Future<void> _onRemoveFriend(RemoveFriend event, Emitter<FriendsState> emit) async {
    final result = await friendsRepository.removeFriend(friendshipId: event.friendshipId);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) => add(LoadFriends()),
    );
  }
}
