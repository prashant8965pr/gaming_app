/**
 * Dashboard Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Wallet, Gamepad2, Trophy, TrendingUp, Plus } from 'lucide-react';
import { useAuth, useWallet } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Spinner } from '@/components/common';
import { formatCurrency, formatRelativeDate } from '@/utils/format';
import { api } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { wallets, getTotalBalance } = useWallet();
  const [dashboard, setDashboard] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await api.getGameDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  const totalBalance = getTotalBalance();
  const cashWallet = wallets.find((w) => w.wallet_type === 'cash');
  const bonusWallet = wallets.find((w) => w.wallet_type === 'bonus');
  const winningsWallet = wallets.find((w) => w.wallet_type === 'winnings');

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome back, {user?.display_name || user?.username}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Here's what's happening with your account today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Balance"
          value={formatCurrency(totalBalance)}
          icon={<Wallet className="w-6 h-6" />}
          color="primary"
          action={() => router.push('/wallet')}
        />
        <StatCard
          title="Games Played"
          value={user?.total_games_played || 0}
          icon={<Gamepad2 className="w-6 h-6" />}
          color="secondary"
        />
        <StatCard
          title="Total Winnings"
          value={formatCurrency(user?.total_winnings || 0)}
          icon={<Trophy className="w-6 h-6" />}
          color="success"
        />
        <StatCard
          title="Level"
          value={`Level ${user?.level || 1}`}
          subtitle={`${user?.xp || 0} XP`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="warning"
        />
      </div>

      {/* Wallets */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>My Wallets</CardTitle>
          <Button
            size="sm"
            onClick={() => router.push('/wallet/deposit')}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Money
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <WalletCard
              title="Cash Wallet"
              balance={cashWallet?.balance || 0}
              type="cash"
            />
            <WalletCard
              title="Bonus Wallet"
              balance={bonusWallet?.balance || 0}
              type="bonus"
            />
            <WalletCard
              title="Winnings Wallet"
              balance={winningsWallet?.balance || 0}
              type="winnings"
            />
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push('/games')}
              >
                <Gamepad2 className="w-5 h-5 mr-2" />
                Browse Games
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push('/wallet/deposit')}
              >
                <Wallet className="w-5 h-5 mr-2" />
                Deposit Money
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push('/achievements')}
              >
                <Trophy className="w-5 h-5 mr-2" />
                View Achievements
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard?.active_sessions?.length > 0 ? (
              <div className="space-y-3">
                {dashboard.active_sessions.map((session: any) => (
                  <div
                    key={session.id}
                    className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                    onClick={() => router.push(`/games/session/${session.id}`)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {session.game_name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {session.current_players}/{session.max_players} players
                        </p>
                      </div>
                      <Badge variant={session.status === 'in_progress' ? 'warning' : 'info'}>
                        {session.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No active game sessions
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  icon,
  color,
  action,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'success' | 'warning';
  action?: () => void;
}) {
  const colors = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400',
    secondary: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/20 dark:text-secondary-400',
    success: 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400',
    warning: 'bg-warning-100 text-warning-600 dark:bg-warning-900/20 dark:text-warning-400',
  };

  return (
    <Card hover={!!action} onClick={action}>
      <CardContent className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          {icon}
        </div>
      </CardContent>
    </Card>
  );
}

function WalletCard({
  title,
  balance,
  type,
}: {
  title: string;
  balance: number;
  type: string;
}) {
  const colors: Record<string, string> = {
    cash: 'border-primary-200 dark:border-primary-800',
    bonus: 'border-secondary-200 dark:border-secondary-800',
    winnings: 'border-success-200 dark:border-success-800',
  };

  return (
    <div className={`p-4 border-2 ${colors[type]} rounded-lg`}>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{title}</p>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">
        {formatCurrency(balance)}
      </p>
    </div>
  );
}
