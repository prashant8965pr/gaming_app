/**
 * Referrals Page
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Users, Copy, TrendingUp, Gift } from 'lucide-react';
import { useAuth } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Spinner } from '@/components/common';
import { formatCurrency, formatRelativeDate } from '@/utils/format';
import { api } from '@/lib/api';

export default function ReferralsPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [referrals, setReferrals] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadReferralData();
  }, []);

  const loadReferralData = async () => {
    try {
      const [statsData, referralsData] = await Promise.all([
        api.getReferralStats(),
        api.getReferrals(),
      ]);
      setStats(statsData);
      setReferrals(referralsData.referrals || []);
    } catch (error) {
      console.error('Failed to load referral data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyReferralCode = () => {
    navigator.clipboard.writeText(user?.referral_code || '');
    toast.success('Referral code copied to clipboard!');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Referral Program</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Invite friends and earn rewards
        </p>
      </div>

      {/* Referral Code Card */}
      <Card variant="elevated" className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <CardContent className="p-8">
          <h2 className="text-2xl font-bold mb-4">Your Referral Code</h2>
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 bg-white/20 backdrop-blur-sm rounded-lg p-4">
              <p className="text-3xl font-mono font-bold tracking-wider">
                {user?.referral_code}
              </p>
            </div>
            <Button
              onClick={copyReferralCode}
              variant="secondary"
              leftIcon={<Copy className="w-4 h-4" />}
            >
              Copy
            </Button>
          </div>
          <p className="text-primary-100">
            Share this code with friends. You'll earn Rs.100 when they make their first deposit!
          </p>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard
          icon={<Users className="w-6 h-6" />}
          label="Total Referrals"
          value={stats?.total_referrals || 0}
          color="primary"
        />
        <StatsCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Active Referrals"
          value={stats?.active_referrals || 0}
          color="success"
        />
        <StatsCard
          icon={<Gift className="w-6 h-6" />}
          label="Total Earnings"
          value={formatCurrency(stats?.total_earnings || 0)}
          color="secondary"
        />
      </div>

      {/* Referrals List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Referrals</CardTitle>
        </CardHeader>
        <CardContent>
          {referrals.length > 0 ? (
            <div className="space-y-3">
              {referrals.map((referral: any) => (
                <div
                  key={referral.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      User #{referral.referred_id?.substring(0, 8)}
                    </p>
                    <p className="text-sm text-gray-500">
                      Joined {formatRelativeDate(referral.created_at)}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge variant={referral.status === 'rewarded' ? 'success' : 'warning'}>
                      {referral.status}
                    </Badge>
                    {referral.bonus_amount > 0 && (
                      <p className="text-sm text-success-600 mt-1">
                        +{formatCurrency(referral.bonus_amount)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center py-8 text-gray-500">
              No referrals yet. Start inviting friends!
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatsCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: 'primary' | 'secondary' | 'success';
}) {
  const colors = {
    primary: 'bg-primary-100 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400',
    secondary: 'bg-secondary-100 text-secondary-600 dark:bg-secondary-900/20 dark:text-secondary-400',
    success: 'bg-success-100 text-success-600 dark:bg-success-900/20 dark:text-success-400',
  };

  return (
    <Card>
      <CardContent className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>{icon}</div>
      </CardContent>
    </Card>
  );
}
