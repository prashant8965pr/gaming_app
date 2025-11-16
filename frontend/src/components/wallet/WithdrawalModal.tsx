/**
 * Withdrawal Modal Component
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Modal, ModalFooter, Button, Input, Alert } from '@/components/common';
import { api } from '@/lib/api';
import { formatCurrency } from '@/utils/format';
import { isValidAmount } from '@/utils/validation';
import type { WithdrawalRequest } from '@/types';

interface WithdrawalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  cashBalance: number;
  winningsBalance: number;
}

export const WithdrawalModal: React.FC<WithdrawalModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  cashBalance,
  winningsBalance,
}) => {
  const [walletType, setWalletType] = useState<'cash' | 'winnings'>('winnings');
  const [isLoading, setIsLoading] = useState(false);

  const availableBalance = walletType === 'cash' ? cashBalance : winningsBalance;

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<WithdrawalRequest>();

  const onSubmit = async (data: WithdrawalRequest) => {
    setIsLoading(true);

    try {
      const payload = {
        ...data,
        wallet_type: walletType,
      };

      await api.withdraw(payload);
      toast.success('Withdrawal request submitted successfully!');
      reset();
      onSuccess();
      onClose();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Withdrawal failed';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Withdraw Money" size="md">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Alert variant="warning">
          Withdrawal fee: 2% | Processing time: 1-3 business days
        </Alert>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Withdraw From
          </label>
          <div className="grid grid-cols-2 gap-3">
            <WalletOption
              label="Winnings Wallet"
              balance={winningsBalance}
              selected={walletType === 'winnings'}
              onSelect={() => setWalletType('winnings')}
            />
            <WalletOption
              label="Cash Wallet"
              balance={cashBalance}
              selected={walletType === 'cash'}
              onSelect={() => setWalletType('cash')}
            />
          </div>
        </div>

        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Available Balance: <span className="font-semibold text-gray-900 dark:text-white">
              {formatCurrency(availableBalance)}
            </span>
          </p>
        </div>

        <Input
          label="Amount"
          type="number"
          placeholder="Enter amount"
          error={errors.amount?.message}
          helperText={`Minimum: ${formatCurrency(200)} | Maximum: ${formatCurrency(50000)}`}
          {...register('amount', {
            required: 'Amount is required',
            validate: (value) => {
              const numValue = Number(value);
              if (numValue > availableBalance) {
                return 'Insufficient balance';
              }
              const validation = isValidAmount(numValue, 200, 50000);
              return validation.isValid || validation.error;
            },
          })}
        />

        <Alert variant="info">
          <p className="text-sm">
            Funds will be transferred to your linked bank account. If you haven't added
            a bank account, please add one in your profile settings first.
          </p>
        </Alert>

        <ModalFooter>
          <Button variant="ghost" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {isLoading ? 'Processing...' : 'Request Withdrawal'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};

interface WalletOptionProps {
  label: string;
  balance: number;
  selected: boolean;
  onSelect: () => void;
}

const WalletOption: React.FC<WalletOptionProps> = ({
  label,
  balance,
  selected,
  onSelect,
}) => {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`p-4 rounded-lg border-2 transition-all text-left ${
        selected
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
      }`}
    >
      <p className={`text-sm font-medium mb-1 ${selected ? 'text-primary-900 dark:text-primary-100' : 'text-gray-900 dark:text-white'}`}>
        {label}
      </p>
      <p className={`text-lg font-bold ${selected ? 'text-primary-600' : 'text-gray-700 dark:text-gray-300'}`}>
        {formatCurrency(balance)}
      </p>
    </button>
  );
};
