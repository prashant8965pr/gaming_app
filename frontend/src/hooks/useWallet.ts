/**
 * useWallet Hook
 */

'use client';

import { useEffect } from 'react';
import { useWalletStore } from '@/store/walletStore';
import { useAuth } from './useAuth';

export const useWallet = () => {
  const walletStore = useWalletStore();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      walletStore.fetchWallets();
    }
  }, [isAuthenticated]);

  return walletStore;
};
