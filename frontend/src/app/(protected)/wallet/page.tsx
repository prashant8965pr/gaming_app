/**
 * Wallet Page
 */

'use client';

import { useState, useEffect } from 'react';
import { Plus, ArrowDownLeft, ArrowUpRight, History } from 'lucide-react';
import { useWallet } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Spinner } from '@/components/common';
import { DepositModal } from '@/components/wallet/DepositModal';
import { WithdrawalModal } from '@/components/wallet/WithdrawalModal';
import { formatCurrency, formatRelativeDate } from '@/utils/format';
import { api } from '@/lib/api';
import type { Transaction } from '@/types';

export default function WalletPage() {
  const { wallets, fetchWallets, getTotalBalance } = useWallet();
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoadingTransactions, setIsLoadingTransactions] = useState(true);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      const data = await api.getTransactions(1, 10);
      setTransactions(data);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setIsLoadingTransactions(false);
    }
  };

  const handleTransactionSuccess = () => {
    fetchWallets();
    loadTransactions();
  };

  const cashWallet = wallets.find((w) => w.wallet_type === 'cash');
  const bonusWallet = wallets.find((w) => w.wallet_type === 'bonus');
  const winningsWallet = wallets.find((w) => w.wallet_type === 'winnings');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Wallet</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your account balance and transactions
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={() => setShowWithdrawModal(true)}
            variant="outline"
            leftIcon={<ArrowUpRight className="w-4 h-4" />}
          >
            Withdraw
          </Button>
          <Button
            onClick={() => setShowDepositModal(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Money
          </Button>
        </div>
      </div>

      {/* Total Balance */}
      <Card variant="elevated" className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <CardContent className="p-8">
          <p className="text-primary-100 text-sm mb-2">Total Balance</p>
          <p className="text-5xl font-bold mb-4">{formatCurrency(getTotalBalance())}</p>
          <p className="text-primary-100 text-sm">
            Available across all wallets
          </p>
        </CardContent>
      </Card>

      {/* Wallets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <WalletCard
          title="Cash Wallet"
          balance={cashWallet?.balance || 0}
          description="Use for entry fees"
          color="primary"
          icon={<ArrowDownLeft className="w-6 h-6" />}
        />
        <WalletCard
          title="Bonus Wallet"
          balance={bonusWallet?.balance || 0}
          description="From promotions & referrals"
          color="secondary"
          icon={<Plus className="w-6 h-6" />}
        />
        <WalletCard
          title="Winnings Wallet"
          balance={winningsWallet?.balance || 0}
          description="Your game winnings"
          color="success"
          icon={<ArrowUpRight className="w-6 h-6" />}
        />
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Transactions</CardTitle>
          <Button variant="ghost" size="sm" leftIcon={<History className="w-4 h-4" />}>
            View All
          </Button>
        </CardHeader>
        <CardContent>
          {isLoadingTransactions ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : transactions.length > 0 ? (
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <TransactionItem key={transaction.id} transaction={transaction} />
              ))}
            </div>
          ) : (
            <p className="text-center py-8 text-gray-500">No transactions yet</p>
          )}
        </CardContent>
      </Card>

      {/* Modals */}
      <DepositModal
        isOpen={showDepositModal}
        onClose={() => setShowDepositModal(false)}
        onSuccess={handleTransactionSuccess}
      />
      <WithdrawalModal
        isOpen={showWithdrawModal}
        onClose={() => setShowWithdrawModal(false)}
        onSuccess={handleTransactionSuccess}
        cashBalance={cashWallet?.balance || 0}
        winningsBalance={winningsWallet?.balance || 0}
      />
    </div>
  );
}

interface WalletCardProps {
  title: string;
  balance: number;
  description: string;
  color: 'primary' | 'secondary' | 'success';
  icon: React.ReactNode;
}

function WalletCard({ title, balance, description, color, icon }: WalletCardProps) {
  const colors = {
    primary: 'border-primary-200 dark:border-primary-800 bg-primary-50 dark:bg-primary-900/10',
    secondary: 'border-secondary-200 dark:border-secondary-800 bg-secondary-50 dark:bg-secondary-900/10',
    success: 'border-success-200 dark:border-success-800 bg-success-50 dark:bg-success-900/10',
  };

  const iconColors = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400',
    secondary: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/20 dark:text-secondary-400',
    success: 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400',
  };

  return (
    <Card className={`border-2 ${colors[color]}`}>
      <CardContent className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {formatCurrency(balance)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>
        </div>
        <div className={`p-3 rounded-lg ${iconColors[color]}`}>{icon}</div>
      </CardContent>
    </Card>
  );
}

function TransactionItem({ transaction }: { transaction: Transaction }) {
  const getIcon = () => {
    if (transaction.transaction_type === 'deposit') return <ArrowDownLeft className="w-5 h-5 text-success-600" />;
    if (transaction.transaction_type === 'withdrawal') return <ArrowUpRight className="w-5 h-5 text-danger-600" />;
    return <History className="w-5 h-5 text-gray-600" />;
  };

  const getStatusBadge = () => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      completed: 'success',
      pending: 'warning',
      failed: 'danger',
      cancelled: 'default',
    };
    return <Badge variant={variants[transaction.status] || 'default'}>{transaction.status}</Badge>;
  };

  const isCredit = ['deposit', 'game_win', 'bonus', 'refund', 'referral'].includes(transaction.transaction_type);

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
      <div className="flex items-center gap-3">
        {getIcon()}
        <div>
          <p className="font-medium text-gray-900 dark:text-white capitalize">
            {transaction.transaction_type.replace('_', ' ')}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {formatRelativeDate(transaction.created_at)}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className={`font-bold ${isCredit ? 'text-success-600' : 'text-danger-600'}`}>
          {isCredit ? '+' : '-'}{formatCurrency(transaction.amount)}
        </p>
        {getStatusBadge()}
      </div>
    </div>
  );
}
