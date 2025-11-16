/**
 * User Details Page
 * View detailed information about a specific user
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Shield,
  Ban,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  Modal,
} from '@/components/common';
import { formatCurrency, formatDateTime, getStatusColor } from '@/lib/utils';
import { api } from '@/lib/api';
import type { UserDetails } from '@/types';

export default function UserDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const userId = params.userId as string;

  const [user, setUser] = useState<UserDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    loadUserDetails();
  }, [userId]);

  const loadUserDetails = async () => {
    try {
      const data = await api.getUserDetails(userId);
      setUser(data);
    } catch (error) {
      console.error('Failed to load user details:', error);
      toast.error('Failed to load user details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!newStatus) return;

    setIsUpdating(true);
    try {
      await api.updateUserStatus(userId, newStatus);
      toast.success('User status updated successfully!');
      setShowStatusModal(false);
      loadUserDetails();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update status';
      toast.error(message);
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">User not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => router.back()}
        >
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {user.user.username}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">User Details</p>
        </div>
        <Button
          variant="outline"
          leftIcon={<Shield className="w-4 h-4" />}
          onClick={() => {
            setNewStatus('');
            setShowStatusModal(true);
          }}
        >
          Change Status
        </Button>
      </div>

      {/* User Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <User className="w-4 h-4" />
                  Username
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {user.user.username}
                </p>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <User className="w-4 h-4" />
                  Display Name
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {user.user.display_name || 'N/A'}
                </p>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <Mail className="w-4 h-4" />
                  Email
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {user.user.email || 'N/A'}
                </p>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <Phone className="w-4 h-4" />
                  Phone
                </label>
                <p className="text-gray-900 dark:text-white font-medium">{user.user.phone}</p>
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-1">
                  <Calendar className="w-4 h-4" />
                  Date of Birth
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {user.user.date_of_birth
                    ? new Date(user.user.date_of_birth).toLocaleDateString()
                    : 'N/A'}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Referral Code
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {user.user.referral_code}
                </p>
              </div>
            </div>

            {user.profile && (
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  Additional Info
                </h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      City
                    </label>
                    <p className="text-gray-900 dark:text-white font-medium">
                      {user.profile.city || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      State
                    </label>
                    <p className="text-gray-900 dark:text-white font-medium">
                      {user.profile.state || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Pincode
                    </label>
                    <p className="text-gray-900 dark:text-white font-medium">
                      {user.profile.pincode || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Status Card */}
        <Card>
          <CardHeader>
            <CardTitle>Account Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mb-2 block">
                Status
              </label>
              <Badge className={getStatusColor(user.user.status)} size="lg">
                {user.user.status}
              </Badge>
            </div>
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mb-2 block">
                KYC Status
              </label>
              <Badge className={getStatusColor(user.user.kyc_status)} size="lg">
                {user.user.kyc_status}
              </Badge>
            </div>
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mb-2 block">
                Email Verified
              </label>
              <Badge
                variant={user.user.is_email_verified ? 'success' : 'warning'}
                size="lg"
              >
                {user.user.is_email_verified ? 'Verified' : 'Not Verified'}
              </Badge>
            </div>
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mb-2 block">
                Phone Verified
              </label>
              <Badge
                variant={user.user.is_phone_verified ? 'success' : 'warning'}
                size="lg"
              >
                {user.user.is_phone_verified ? 'Verified' : 'Not Verified'}
              </Badge>
            </div>
            <div>
              <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                Member Since
              </label>
              <p className="text-gray-900 dark:text-white font-medium">
                {formatDateTime(user.user.created_at)}
              </p>
            </div>
            {user.user.last_login_at && (
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Last Login
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {formatDateTime(user.user.last_login_at)}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Statistics & Wallets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Statistics */}
        {user.statistics && (
          <Card>
            <CardHeader>
              <CardTitle>Gaming Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Games Played
                  </label>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user.statistics.total_games_played}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Games Won
                  </label>
                  <p className="text-2xl font-bold text-success-600">
                    {user.statistics.total_games_won}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Total Winnings
                  </label>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(user.statistics.total_winnings)}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Total Spent
                  </label>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(user.statistics.total_spent)}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">Level</label>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user.statistics.current_level}
                  </p>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Experience
                  </label>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user.statistics.experience_points} XP
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Wallets */}
        <Card>
          <CardHeader>
            <CardTitle>Wallet Balances</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {user.wallets.map((wallet) => (
                <div
                  key={wallet.wallet_type}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                >
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                      {wallet.wallet_type} Wallet
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                      {formatCurrency(wallet.balance)}
                    </p>
                  </div>
                </div>
              ))}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Balance
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatCurrency(
                      user.wallets.reduce((sum, w) => sum + w.balance, 0)
                    )}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          {user.recent_transactions.length === 0 ? (
            <p className="text-center py-8 text-gray-500">No recent transactions</p>
          ) : (
            <div className="space-y-3">
              {user.recent_transactions.map((txn) => (
                <div
                  key={txn.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white capitalize">
                      {txn.type.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-500">{txn.description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDateTime(txn.created_at)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-lg font-bold ${
                        txn.amount >= 0 ? 'text-success-600' : 'text-danger-600'
                      }`}
                    >
                      {txn.amount >= 0 ? '+' : ''}
                      {formatCurrency(Math.abs(txn.amount))}
                    </p>
                    <Badge className={getStatusColor(txn.status)}>{txn.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Status Change Modal */}
      <Modal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        title="Change User Status"
        footer={
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setShowStatusModal(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              isLoading={isUpdating}
              onClick={handleUpdateStatus}
              disabled={!newStatus}
            >
              Update Status
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Current status: <Badge className={getStatusColor(user.user.status)}>{user.user.status}</Badge>
          </p>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Select new status:
            </label>
            <div className="flex flex-col gap-2">
              <Button
                variant={newStatus === 'active' ? 'success' : 'outline'}
                leftIcon={<CheckCircle className="w-4 h-4" />}
                onClick={() => setNewStatus('active')}
                className="justify-start"
              >
                Active - User can access all features
              </Button>
              <Button
                variant={newStatus === 'suspended' ? 'warning' : 'outline'}
                leftIcon={<AlertTriangle className="w-4 h-4" />}
                onClick={() => setNewStatus('suspended')}
                className="justify-start"
              >
                Suspended - Temporary restriction
              </Button>
              <Button
                variant={newStatus === 'banned' ? 'danger' : 'outline'}
                leftIcon={<Ban className="w-4 h-4" />}
                onClick={() => setNewStatus('banned')}
                className="justify-start"
              >
                Banned - Permanent restriction
              </Button>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
