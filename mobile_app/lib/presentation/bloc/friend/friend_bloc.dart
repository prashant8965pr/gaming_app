import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/friend_repository.dart';
import 'friend_event.dart';
import 'friend_state.dart';

class FriendBloc extends Bloc<FriendEvent, FriendState> {
  final FriendRepository repository;

  FriendBloc({required this.repository}) : super(FriendInitial()) {
    on<LoadFriends>(_onLoadFriends);
    on<SendFriendRequest>(_onSendFriendRequest);
    on<LoadFriendRequests>(_onLoadFriendRequests);
    on<AcceptFriendRequest>(_onAcceptFriendRequest);
    on<RejectFriendRequest>(_onRejectFriendRequest);
    on<RemoveFriend>(_onRemoveFriend);
  }

  Future<void> _onLoadFriends(
    LoadFriends event,
    Emitter<FriendState> emit,
  ) async {
    if (event.refresh) {
      emit(FriendLoading());
    }

    final result = await repository.getFriends();

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (friends) => emit(FriendsLoaded(friends)),
    );
  }

  Future<void> _onSendFriendRequest(
    SendFriendRequest event,
    Emitter<FriendState> emit,
  ) async {
    emit(FriendRequestSending());

    final result = await repository.sendFriendRequest(
      event.receiverId,
      event.message,
    );

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (_) => emit(FriendRequestSent()),
    );
  }

  Future<void> _onLoadFriendRequests(
    LoadFriendRequests event,
    Emitter<FriendState> emit,
  ) async {
    emit(FriendRequestsLoading());

    final result = await repository.getFriendRequests();

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (requests) => emit(FriendRequestsLoaded(requests)),
    );
  }

  Future<void> _onAcceptFriendRequest(
    AcceptFriendRequest event,
    Emitter<FriendState> emit,
  ) async {
    emit(FriendRequestAccepting());

    final result = await repository.acceptFriendRequest(event.requestId);

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (_) => emit(FriendRequestAccepted()),
    );
  }

  Future<void> _onRejectFriendRequest(
    RejectFriendRequest event,
    Emitter<FriendState> emit,
  ) async {
    emit(FriendRequestRejecting());

    final result = await repository.rejectFriendRequest(event.requestId);

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (_) => emit(FriendRequestRejected()),
    );
  }

  Future<void> _onRemoveFriend(
    RemoveFriend event,
    Emitter<FriendState> emit,
  ) async {
    emit(FriendRemoving());

    final result = await repository.removeFriend(event.friendId);

    result.fold(
      (failure) => emit(FriendError(failure.message)),
      (_) => emit(FriendRemoved()),
    );
  }
}
