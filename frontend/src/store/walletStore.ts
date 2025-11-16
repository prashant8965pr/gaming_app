/**
 * Wallet State Management
 */

import { create } from 'zustand';
import { api } from '@/lib/api';
import type { WalletState, Wallet } from '@/types';

export const useWalletStore = create<WalletState>((set, get) => ({
  wallets: [],
  isLoading: false,

  fetchWallets: async () => {
    set({ isLoading: true });
    try {
      const wallets = await api.getWallets();
      set({ wallets, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  getTotalBalance: () => {
    const { wallets } = get();
    return wallets.reduce((total, wallet) => total + wallet.balance, 0);
  },

  getWalletByType: (type: string) => {
    const { wallets } = get();
    return wallets.find((wallet) => wallet.wallet_type === type);
  },
}));
