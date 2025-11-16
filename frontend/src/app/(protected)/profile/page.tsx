/**
 * Profile Settings Page
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { User, Mail, Phone, Shield, CreditCard } from 'lucide-react';
import { useAuth } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Badge } from '@/components/common';
import { api } from '@/lib/api';

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      display_name: user?.display_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
    },
  });

  const onSubmit = async (data: any) => {
    setIsLoading(true);
    try {
      await api.updateProfile(data);
      await refreshUser();
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Account Status */}
      <Card>
        <CardHeader>
          <CardTitle>Account Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">Email Verification</span>
            </div>
            <Badge variant={user?.is_verified ? 'success' : 'warning'}>
              {user?.is_verified ? 'Verified' : 'Not Verified'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CreditCard className="w-5 h-5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">KYC Status</span>
            </div>
            <Badge variant={user?.kyc_status === 'approved' ? 'success' : 'warning'}>
              {user?.kyc_status || 'Not Submitted'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Username"
              value={user?.username}
              disabled
              helperText="Username cannot be changed"
            />

            <Input
              label="Display Name"
              placeholder="Your display name"
              error={errors.display_name?.message}
              {...register('display_name')}
            />

            <Input
              label="Email"
              type="email"
              leftIcon={<Mail className="w-5 h-5" />}
              error={errors.email?.message}
              {...register('email', { required: 'Email is required' })}
            />

            <Input
              label="Phone"
              type="tel"
              leftIcon={<Phone className="w-5 h-5" />}
              error={errors.phone?.message}
              {...register('phone', { required: 'Phone is required' })}
            />

            <div className="pt-4">
              <Button type="submit" isLoading={isLoading}>
                Save Changes
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Referral Info */}
      <Card>
        <CardHeader>
          <CardTitle>Referral Code</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Input
              value={user?.referral_code || ''}
              disabled
              className="flex-1"
            />
            <Button
              onClick={() => {
                navigator.clipboard.writeText(user?.referral_code || '');
                toast.success('Referral code copied!');
              }}
            >
              Copy Code
            </Button>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Share this code with friends to earn bonus rewards
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
