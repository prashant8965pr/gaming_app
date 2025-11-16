import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/wallet_repository.dart';
import 'wallet_event.dart';
import 'wallet_state.dart';

class WalletBloc extends Bloc<WalletEvent, WalletState> {
  final WalletRepository _walletRepository;

  WalletBloc({required WalletRepository walletRepository})
      : _walletRepository = walletRepository,
        super(const WalletInitial()) {
    on<LoadWalletBalanceEvent>(_onLoadWalletBalance);
    on<AddMoneyEvent>(_onAddMoney);
    on<WithdrawMoneyEvent>(_onWithdrawMoney);
    on<LoadTransactionsEvent>(_onLoadTransactions);
    on<LoadTransactionDetailsEvent>(_onLoadTransactionDetails);
    on<AddBankAccountEvent>(_onAddBankAccount);
    on<LoadBankAccountsEvent>(_onLoadBankAccounts);
    on<DeleteBankAccountEvent>(_onDeleteBankAccount);
    on<SetPrimaryBankAccountEvent>(_onSetPrimaryBankAccount);
    on<ValidatePromoCodeEvent>(_onValidatePromoCode);
    on<ApplyPromoCodeEvent>(_onApplyPromoCode);
  }

  Future<void> _onLoadWalletBalance(
    LoadWalletBalanceEvent event,
    Emitter<WalletState> emit,
  ) async {
    if (event.forceRefresh) {
      emit(const WalletLoading());
    }

    final result = await _walletRepository.getBalance();

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (balance) => emit(WalletBalanceLoaded(balance: balance)),
    );
  }

  Future<void> _onAddMoney(
    AddMoneyEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.addMoney(
      amount: event.amount,
      paymentMethod: event.paymentMethod,
      promoCode: event.promoCode,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (transaction) => emit(MoneyAdded(transaction: transaction)),
    );
  }

  Future<void> _onWithdrawMoney(
    WithdrawMoneyEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.withdrawMoney(
      amount: event.amount,
      bankAccountId: event.bankAccountId,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (transaction) => emit(MoneyWithdrawn(transaction: transaction)),
    );
  }

  Future<void> _onLoadTransactions(
    LoadTransactionsEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.getTransactions(
      limit: event.limit,
      offset: event.offset,
      type: event.type,
      status: event.status,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (transactions) => emit(TransactionsLoaded(transactions: transactions)),
    );
  }

  Future<void> _onLoadTransactionDetails(
    LoadTransactionDetailsEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.getTransactionDetails(
      transactionId: event.transactionId,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (transaction) => emit(TransactionDetailsLoaded(transaction: transaction)),
    );
  }

  Future<void> _onAddBankAccount(
    AddBankAccountEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.addBankAccount(
      accountHolderName: event.accountHolderName,
      accountNumber: event.accountNumber,
      ifscCode: event.ifscCode,
      bankName: event.bankName,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (account) => emit(BankAccountAdded(account: account)),
    );
  }

  Future<void> _onLoadBankAccounts(
    LoadBankAccountsEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.getBankAccounts();

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (accounts) => emit(BankAccountsLoaded(accounts: accounts)),
    );
  }

  Future<void> _onDeleteBankAccount(
    DeleteBankAccountEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.deleteBankAccount(
      accountId: event.accountId,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (_) => emit(const BankAccountDeleted()),
    );
  }

  Future<void> _onSetPrimaryBankAccount(
    SetPrimaryBankAccountEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.setPrimaryBankAccount(
      accountId: event.accountId,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (_) => emit(const PrimaryBankAccountSet()),
    );
  }

  Future<void> _onValidatePromoCode(
    ValidatePromoCodeEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.validatePromoCode(
      code: event.code,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (promoCode) => emit(PromoCodeValidated(promoCode: promoCode)),
    );
  }

  Future<void> _onApplyPromoCode(
    ApplyPromoCodeEvent event,
    Emitter<WalletState> emit,
  ) async {
    emit(const WalletLoading());

    final result = await _walletRepository.applyPromoCode(
      code: event.code,
    );

    result.fold(
      (failure) => emit(WalletError(message: failure.message)),
      (_) => emit(const PromoCodeApplied()),
    );
  }
}
