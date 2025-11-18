import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/repositories/wallet_repository.dart';
import 'wallet_event.dart';
import 'wallet_state.dart';

class WalletBloc extends Bloc<WalletEvent, WalletState> {
  final WalletRepository walletRepository;

  WalletBloc({required this.walletRepository}) : super(const WalletState()) {
    on<LoadWallets>(_onLoadWallets);
    on<DepositMoney>(_onDepositMoney);
    on<WithdrawMoney>(_onWithdrawMoney);
    on<LoadTransactions>(_onLoadTransactions);
    on<RefreshWallets>(_onRefreshWallets);
  }

  Future<void> _onLoadWallets(
    LoadWallets event,
    Emitter<WalletState> emit,
  ) async {
    emit(state.copyWith(status: WalletStatus.loading));

    try {
      final result = await walletRepository.getWallets();

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: WalletStatus.error,
            errorMessage: failure.message,
          ));
        },
        (wallets) {
          emit(state.copyWith(
            status: WalletStatus.loaded,
            wallets: wallets,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: WalletStatus.error,
        errorMessage: 'Failed to load wallets: $e',
      ));
    }
  }

  Future<void> _onDepositMoney(
    DepositMoney event,
    Emitter<WalletState> emit,
  ) async {
    emit(state.copyWith(status: WalletStatus.depositing));

    try {
      final result = await walletRepository.deposit(
        amount: event.amount,
        paymentMethod: event.paymentMethod,
        promoCode: event.promoCode,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: WalletStatus.error,
            errorMessage: failure.message,
          ));
        },
        (paymentUrl) {
          // Payment URL returned, handle payment gateway
          emit(state.copyWith(status: WalletStatus.loaded));
          // Refresh wallets after successful deposit
          add(const RefreshWallets());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: WalletStatus.error,
        errorMessage: 'Failed to deposit money: $e',
      ));
    }
  }

  Future<void> _onWithdrawMoney(
    WithdrawMoney event,
    Emitter<WalletState> emit,
  ) async {
    emit(state.copyWith(status: WalletStatus.withdrawing));

    try {
      final result = await walletRepository.withdraw(
        walletType: event.walletType,
        amount: event.amount,
        bankAccountId: event.bankAccountId,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: WalletStatus.error,
            errorMessage: failure.message,
          ));
        },
        (withdrawal) {
          emit(state.copyWith(status: WalletStatus.loaded));
          // Refresh wallets after withdrawal request
          add(const RefreshWallets());
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: WalletStatus.error,
        errorMessage: 'Failed to withdraw money: $e',
      ));
    }
  }

  Future<void> _onLoadTransactions(
    LoadTransactions event,
    Emitter<WalletState> emit,
  ) async {
    if (event.page == 1) {
      emit(state.copyWith(status: WalletStatus.loading));
    }

    try {
      final result = await walletRepository.getTransactions(
        walletType: event.walletType,
        transactionType: event.transactionType,
        page: event.page,
        limit: event.limit,
      );

      result.fold(
        (failure) {
          emit(state.copyWith(
            status: WalletStatus.error,
            errorMessage: failure.message,
          ));
        },
        (newTransactions) {
          final updatedTransactions = event.page == 1
              ? newTransactions
              : [...state.transactions, ...newTransactions];

          emit(state.copyWith(
            status: WalletStatus.loaded,
            transactions: updatedTransactions,
            hasMoreTransactions: newTransactions.length >= event.limit,
            currentPage: event.page,
          ));
        },
      );
    } catch (e) {
      emit(state.copyWith(
        status: WalletStatus.error,
        errorMessage: 'Failed to load transactions: $e',
      ));
    }
  }

  Future<void> _onRefreshWallets(
    RefreshWallets event,
    Emitter<WalletState> emit,
  ) async {
    try {
      final result = await walletRepository.getWallets();

      result.fold(
        (failure) {
          // Silent fail on refresh
        },
        (wallets) {
          emit(state.copyWith(wallets: wallets));
        },
      );
    } catch (e) {
      // Silent fail on refresh
    }
  }
}
