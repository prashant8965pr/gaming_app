/**
 * Deposit Modal Component
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { CreditCard, Smartphone, Building } from 'lucide-react';
import { Modal, ModalFooter, Button, Input, Alert } from '@/components/common';
import { api } from '@/lib/api';
import { formatCurrency } from '@/utils/format';
import { isValidAmount } from '@/utils/validation';
import type { DepositRequest } from '@/types';

interface DepositModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const DepositModal: React.FC<DepositModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [selectedMethod, setSelectedMethod] = useState<'upi' | 'card' | 'netbanking'>('upi');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<DepositRequest>();

  const onSubmit = async (data: DepositRequest) => {
    setIsLoading(true);

    try {
      const payload = {
        ...data,
        payment_method: selectedMethod,
      };

      const result = await api.deposit(payload);
      toast.success('Deposit initiated successfully!');
      reset();
      onSuccess();
      onClose();

      // In a real app, redirect to payment gateway
      if (result.payment_url) {
        window.location.href = result.payment_url;
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Deposit failed';
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
    <Modal isOpen={isOpen} onClose={handleClose} title="Add Money" size="md">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Alert variant="info">
          Minimum deposit: {formatCurrency(100)} | Maximum: {formatCurrency(100000)}
        </Alert>

        <Input
          label="Amount"
          type="number"
          placeholder="Enter amount"
          error={errors.amount?.message}
          {...register('amount', {
            required: 'Amount is required',
            validate: (value) => {
              const validation = isValidAmount(Number(value), 100, 100000);
              return validation.isValid || validation.error;
            },
          })}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Payment Method
          </label>
          <div className="space-y-2">
            <PaymentMethod
              id="upi"
              icon={<Smartphone className="w-5 h-5" />}
              label="UPI"
              description="PhonePe, Google Pay, Paytm"
              selected={selectedMethod === 'upi'}
              onSelect={() => setSelectedMethod('upi')}
            />
            <PaymentMethod
              id="card"
              icon={<CreditCard className="w-5 h-5" />}
              label="Debit/Credit Card"
              description="Visa, Mastercard, Rupay"
              selected={selectedMethod === 'card'}
              onSelect={() => setSelectedMethod('card')}
            />
            <PaymentMethod
              id="netbanking"
              icon={<Building className="w-5 h-5" />}
              label="Net Banking"
              description="All major banks"
              selected={selectedMethod === 'netbanking'}
              onSelect={() => setSelectedMethod('netbanking')}
            />
          </div>
        </div>

        <ModalFooter>
          <Button variant="ghost" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            {isLoading ? 'Processing...' : 'Proceed to Payment'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};

interface PaymentMethodProps {
  id: string;
  icon: React.ReactNode;
  label: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}

const PaymentMethod: React.FC<PaymentMethodProps> = ({
  icon,
  label,
  description,
  selected,
  onSelect,
}) => {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
        selected
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
      }`}
    >
      <div className="flex items-center">
        <div className={`mr-3 ${selected ? 'text-primary-600' : 'text-gray-500'}`}>
          {icon}
        </div>
        <div className="flex-1">
          <p className={`font-medium ${selected ? 'text-primary-900 dark:text-primary-100' : 'text-gray-900 dark:text-white'}`}>
            {label}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
        </div>
        <div
          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
            selected
              ? 'border-primary-500 bg-primary-500'
              : 'border-gray-300 dark:border-gray-600'
          }`}
        >
          {selected && <div className="w-2 h-2 bg-white rounded-full" />}
        </div>
      </div>
    </button>
  );
};
