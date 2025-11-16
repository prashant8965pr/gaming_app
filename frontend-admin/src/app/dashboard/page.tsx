/**
 * Admin Dashboard Page
 * Displays key metrics and statistics
 */

'use client';

import { useEffect, useState } from 'react';
import {
  Users,
  UserCheck,
  CreditCard,
  TrendingUp,
  FileCheck,
  DollarSign,
  Activity,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common';
import { formatCurrency } from '@/lib/utils';
import { api } from '@/lib/api';
import type { DashboardStats } from '@/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Failed to load dashboard statistics</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Platform overview and key metrics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Users */}
        <StatsCard
          title="Total Users"
          value={stats.users.total.toLocaleString()}
          icon={<Users className="w-6 h-6" />}
          color="primary"
          subtitle={`${stats.users.new_today} new today`}
        />

        {/* Active Users */}
        <StatsCard
          title="Active Users"
          value={stats.users.active.toLocaleString()}
          icon={<UserCheck className="w-6 h-6" />}
          color="success"
          subtitle="Last 7 days"
        />

        {/* Total Revenue */}
        <StatsCard
          title="Total Revenue"
          value={formatCurrency(stats.transactions.revenue_total)}
          icon={<DollarSign className="w-6 h-6" />}
          color="primary"
          subtitle="All time"
        />

        {/* Active Sessions */}
        <StatsCard
          title="Active Sessions"
          value={stats.sessions.active.toLocaleString()}
          icon={<Activity className="w-6 h-6" />}
          color="warning"
          subtitle="Currently playing"
        />
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* KYC Pending */}
        <StatsCard
          title="Pending KYC"
          value={stats.kyc.pending.toLocaleString()}
          icon={<FileCheck className="w-6 h-6" />}
          color="warning"
          subtitle={`${stats.kyc.approved} approved`}
        />

        {/* Pending Withdrawals */}
        <StatsCard
          title="Pending Withdrawals"
          value={stats.withdrawals.pending_count.toLocaleString()}
          icon={<CreditCard className="w-6 h-6" />}
          color="danger"
          subtitle={formatCurrency(stats.withdrawals.pending_amount)}
        />

        {/* Today's Transactions */}
        <StatsCard
          title="Today's Deposits"
          value={formatCurrency(stats.transactions.deposits_today)}
          icon={<TrendingUp className="w-6 h-6" />}
          color="success"
          subtitle={`Withdrawals: ${formatCurrency(stats.transactions.withdrawals_today)}`}
        />
      </div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ActionCard
          title="Review KYC Documents"
          description="Approve or reject pending KYC documents"
          count={stats.kyc.pending}
          href="/dashboard/kyc"
          color="warning"
        />

        <ActionCard
          title="Process Withdrawals"
          description="Review and approve withdrawal requests"
          count={stats.withdrawals.pending_count}
          href="/dashboard/withdrawals"
          color="danger"
        />

        <ActionCard
          title="Manage Users"
          description="View and manage platform users"
          count={stats.users.total}
          href="/dashboard/users"
          color="primary"
        />
      </div>
    </div>
  );
}

interface StatsCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'danger';
  subtitle?: string;
}

function StatsCard({ title, value, icon, color, subtitle }: StatsCardProps) {
  const colors = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400',
    success: 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400',
    warning: 'bg-warning-100 text-warning-600 dark:bg-warning-900/20 dark:text-warning-400',
    danger: 'bg-danger-100 text-danger-600 dark:bg-danger-900/20 dark:text-danger-400',
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <div className={`p-2 rounded-lg ${colors[color]}`}>{icon}</div>
        </div>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</p>
        {subtitle && <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}

interface ActionCardProps {
  title: string;
  description: string;
  count: number;
  href: string;
  color: 'primary' | 'warning' | 'danger';
}

function ActionCard({ title, description, count, href, color }: ActionCardProps) {
  const colors = {
    primary: 'border-primary-200 dark:border-primary-800',
    warning: 'border-warning-200 dark:border-warning-800',
    danger: 'border-danger-200 dark:border-danger-800',
  };

  return (
    <Card className={`border-2 ${colors[color]} hover:shadow-lg transition-shadow`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
          </div>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{count}</span>
        </div>
        <a
          href={href}
          className="inline-block text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline"
        >
          View all →
        </a>
      </CardContent>
    </Card>
  );
}
