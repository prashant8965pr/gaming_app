/**
 * User Management Page
 * View, search, and manage platform users
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users as UsersIcon, Search, Filter, Eye } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  Input,
} from '@/components/common';
import { formatCurrency, formatDateTime, getStatusColor } from '@/lib/utils';
import { api } from '@/lib/api';
import type { PlatformUser } from '@/types';

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<PlatformUser[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [kycStatusFilter, setKycStatusFilter] = useState('');
  const [offset, setOffset] = useState(0);
  const limit = 50;

  useEffect(() => {
    loadUsers();
  }, [search, statusFilter, kycStatusFilter, offset]);

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      const data = await api.getUsers({
        limit,
        offset,
        search: search || undefined,
        status_filter: statusFilter || undefined,
        kyc_status_filter: kycStatusFilter || undefined,
      });
      setUsers(data.users);
      setTotalCount(data.total_count);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    setOffset(0);
  };

  const handleViewUser = (userId: string) => {
    router.push(`/dashboard/users/${userId}`);
  };

  if (isLoading && users.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">User Management</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          View and manage platform users
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {totalCount.toLocaleString()}
                </p>
              </div>
              <UsersIcon className="w-8 h-8 text-primary-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-1">
              <Input
                placeholder="Search by username, email, phone..."
                leftIcon={<Search className="w-5 h-5" />}
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>

            {/* Status Filter */}
            <div>
              <select
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
                <option value="banned">Banned</option>
              </select>
            </div>

            {/* KYC Status Filter */}
            <div>
              <select
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                value={kycStatusFilter}
                onChange={(e) => {
                  setKycStatusFilter(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">All KYC Status</option>
                <option value="pending">Pending</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User List */}
      <Card>
        <CardHeader>
          <CardTitle>Users ({totalCount.toLocaleString()})</CardTitle>
        </CardHeader>
        <CardContent>
          {users.length === 0 ? (
            <div className="text-center py-12">
              <UsersIcon className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No users found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {users.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {user.username}
                      </h4>
                      <Badge className={getStatusColor(user.status)}>{user.status}</Badge>
                      <Badge className={getStatusColor(user.kyc_status)}>
                        KYC: {user.kyc_status}
                      </Badge>
                      {user.role !== 'user' && (
                        <Badge variant="primary">{user.role}</Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Email:</span>
                        <p className="text-gray-900 dark:text-white font-medium truncate">
                          {user.email || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Phone:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {user.phone}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Balance:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {formatCurrency(user.total_balance)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Games:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {user.games_played}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Joined:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {new Date(user.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="primary"
                    leftIcon={<Eye className="w-4 h-4" />}
                    onClick={() => handleViewUser(user.id)}
                  >
                    View
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalCount > limit && (
            <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {offset + 1} to {Math.min(offset + limit, totalCount)} of{' '}
                {totalCount} users
              </p>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={offset === 0}
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                >
                  Previous
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={offset + limit >= totalCount}
                  onClick={() => setOffset(offset + limit)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
