/**
 * useAuth Hook
 */

'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

export const useAuth = () => {
  const authStore = useAuthStore();

  useEffect(() => {
    // Refresh user on mount if authenticated
    if (authStore.isAuthenticated && authStore.token) {
      authStore.refreshUser();
    }
  }, []);

  return authStore;
};
