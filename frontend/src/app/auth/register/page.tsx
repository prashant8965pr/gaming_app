/**
 * Register Page
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { UserPlus } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { Button, Input, Card, CardContent, Alert } from '@/components/common';
import { isValidEmail, isValidPhone, isValidUsername, isValidPassword } from '@/utils/validation';
import type { RegisterData } from '@/types';

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterData) => {
    setIsLoading(true);
    setError('');

    try {
      await registerUser(data);
      toast.success('Account created successfully!');
      router.push('/dashboard');
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <Card className="shadow-xl">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Create Account
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Join thousands of players already winning
            </p>
          </div>

          {error && (
            <Alert variant="danger" className="mb-6">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Username"
              type="text"
              placeholder="Choose a username"
              error={errors.username?.message}
              {...register('username', {
                required: 'Username is required',
                validate: (value) =>
                  isValidUsername(value) || '3-20 characters, alphanumeric and underscores only',
              })}
            />

            <Input
              label="Email"
              type="email"
              placeholder="your.email@example.com"
              error={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                validate: (value) =>
                  isValidEmail(value) || 'Please enter a valid email',
              })}
            />

            <Input
              label="Phone Number"
              type="tel"
              placeholder="+91 98765 43210"
              error={errors.phone?.message}
              helperText="Indian phone number with country code"
              {...register('phone', {
                required: 'Phone number is required',
                validate: (value) =>
                  isValidPhone(value) || 'Please enter a valid Indian phone number',
              })}
            />

            <Input
              label="Display Name (Optional)"
              type="text"
              placeholder="How should we call you?"
              {...register('display_name')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="Create a strong password"
              error={errors.password?.message}
              helperText="At least 8 characters with uppercase, lowercase, number, and special character"
              {...register('password', {
                required: 'Password is required',
                validate: (value) => {
                  const validation = isValidPassword(value);
                  return validation.isValid || validation.errors[0];
                },
              })}
            />

            <Input
              label="Confirm Password"
              type="password"
              placeholder="Re-enter your password"
              error={errors.confirm_password?.message}
              {...register('confirm_password' as any, {
                required: 'Please confirm your password',
                validate: (value) =>
                  value === password || 'Passwords do not match',
              })}
            />

            <Input
              label="Referral Code (Optional)"
              type="text"
              placeholder="Enter referral code if you have one"
              {...register('referral_code')}
            />

            <div className="flex items-start">
              <input
                type="checkbox"
                className="mt-1 mr-2 rounded border-gray-300"
                required
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                I agree to the{' '}
                <Link href="/terms" className="text-primary-600 hover:text-primary-700">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-primary-600 hover:text-primary-700">
                  Privacy Policy
                </Link>
              </span>
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isLoading}
              leftIcon={<UserPlus className="w-5 h-5" />}
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link
                href="/auth/login"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Login
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
