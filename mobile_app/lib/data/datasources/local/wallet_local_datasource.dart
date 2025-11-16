import 'package:hive/hive.dart';
import '../../models/wallet_model.dart';
import '../../../core/storage/hive_config.dart';

/// Local data source for wallet data
abstract class WalletLocalDataSource {
  Future<void> cacheBalance(WalletBalanceModel balance);
  Future<WalletBalanceModel?> getCachedBalance();
  Future<void> clearBalance();

  Future<void> cacheTransactions(List<TransactionModel> transactions);
  Future<List<TransactionModel>> getCachedTransactions();
  Future<void> addTransaction(TransactionModel transaction);

  Future<void> cacheBankAccounts(List<BankAccountModel> accounts);
  Future<List<BankAccountModel>> getCachedBankAccounts();
}

class WalletLocalDataSourceImpl implements WalletLocalDataSource {
  final Box _walletBox;
  final Box _transactionsBox;
  final CacheHelper _cacheHelper;

  WalletLocalDataSourceImpl(
    this._walletBox,
    this._transactionsBox,
    this._cacheHelper,
  );

  static const String _balanceKey = 'wallet_balance';
  static const String _bankAccountsKey = 'bank_accounts';

  @override
  Future<void> cacheBalance(WalletBalanceModel balance) async {
    await _walletBox.put(_balanceKey, balance.toJson());
    await _cacheHelper.save(
      key: CacheKeys.walletBalance,
      data: balance.toJson(),
      expiresIn: const Duration(minutes: 5),
    );
  }

  @override
  Future<WalletBalanceModel?> getCachedBalance() async {
    final balanceData = _walletBox.get(_balanceKey);
    if (balanceData == null) return null;

    try {
      return WalletBalanceModel.fromJson(
        Map<String, dynamic>.from(balanceData),
      );
    } catch (e) {
      return null;
    }
  }

  @override
  Future<void> clearBalance() async {
    await _walletBox.delete(_balanceKey);
    await _cacheHelper.delete(CacheKeys.walletBalance);
  }

  @override
  Future<void> cacheTransactions(List<TransactionModel> transactions) async {
    await _transactionsBox.clear();
    for (var i = 0; i < transactions.length; i++) {
      await _transactionsBox.put(i, transactions[i].toJson());
    }
  }

  @override
  Future<List<TransactionModel>> getCachedTransactions() async {
    final transactions = <TransactionModel>[];
    for (var i = 0; i < _transactionsBox.length; i++) {
      final data = _transactionsBox.getAt(i);
      if (data != null) {
        try {
          transactions.add(
            TransactionModel.fromJson(Map<String, dynamic>.from(data)),
          );
        } catch (e) {
          // Skip invalid transaction
        }
      }
    }
    return transactions;
  }

  @override
  Future<void> addTransaction(TransactionModel transaction) async {
    await _transactionsBox.add(transaction.toJson());
  }

  @override
  Future<void> cacheBankAccounts(List<BankAccountModel> accounts) async {
    await _walletBox.put(
      _bankAccountsKey,
      accounts.map((e) => e.toJson()).toList(),
    );
  }

  @override
  Future<List<BankAccountModel>> getCachedBankAccounts() async {
    final accountsData = _walletBox.get(_bankAccountsKey);
    if (accountsData == null) return [];

    try {
      final List<dynamic> dataList = accountsData;
      return dataList
          .map((e) => BankAccountModel.fromJson(Map<String, dynamic>.from(e)))
          .toList();
    } catch (e) {
      return [];
    }
  }
}
