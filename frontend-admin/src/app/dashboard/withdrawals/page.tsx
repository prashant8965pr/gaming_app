/**
 * Withdrawal Management Page
 * Process and approve withdrawal requests
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { CreditCard, Eye, CheckCircle, XCircle, Send } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  Modal,
  Input,
} from '@/components/common';
import { formatCurrency, formatDateTime, getStatusColor, maskAccountNumber } from '@/lib/utils';
import { api } from '@/lib/api';
import type { WithdrawalRequest, ReviewWithdrawalRequest } from '@/types';

export default function WithdrawalManagementPage() {
  const [withdrawals, setWithdrawals] = useState<WithdrawalRequest[]>([]);
  const [selectedWithdrawal, setSelectedWithdrawal] = useState<WithdrawalRequest | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | 'complete'>('approve');
  const [rejectionReason, setRejectionReason] = useState('');
  const [utrNumber, setUtrNumber] = useState('');
  const [adminNotes, setAdminNotes] = useState('');

  useEffect(() => {
    loadPendingWithdrawals();
  }, []);

  const loadPendingWithdrawals = async () => {
    try {
      const data = await api.getPendingWithdrawals({ limit: 100 });
      setWithdrawals(data.withdrawals);
    } catch (error) {
      console.error('Failed to load withdrawals:', error);
      toast.error('Failed to load withdrawals');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReview = (withdrawal: WithdrawalRequest) => {
    setSelectedWithdrawal(withdrawal);
    setReviewAction(withdrawal.status === 'processing' ? 'complete' : 'approve');
    setRejectionReason('');
    setUtrNumber('');
    setAdminNotes('');
  };

  const handleSubmitReview = async () => {
    if (!selectedWithdrawal) return;

    if (reviewAction === 'reject' && !rejectionReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }

    if (reviewAction === 'complete' && !utrNumber.trim()) {
      toast.error('Please provide UTR number');
      return;
    }

    setIsProcessing(true);
    try {
      const reviewData: ReviewWithdrawalRequest = {
        withdrawal_id: selectedWithdrawal.id,
        action: reviewAction,
        rejection_reason: rejectionReason.trim() || undefined,
        utr_number: utrNumber.trim() || undefined,
        admin_notes: adminNotes.trim() || undefined,
      };

      await api.reviewWithdrawal(reviewData);
      toast.success(`Withdrawal ${reviewAction}d successfully!`);
      setSelectedWithdrawal(null);
      loadPendingWithdrawals();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to process withdrawal';
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const totalPendingAmount = withdrawals.reduce((sum, w) => sum + w.final_amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Withdrawal Management
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Review and process withdrawal requests
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pending Requests</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {withdrawals.length}
                </p>
              </div>
              <CreditCard className="w-8 h-8 text-danger-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Pending Amount</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {formatCurrency(totalPendingAmount)}
                </p>
              </div>
              <CreditCard className="w-8 h-8 text-warning-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Withdrawal List */}
      <Card>
        <CardHeader>
          <CardTitle>Pending Withdrawals</CardTitle>
        </CardHeader>
        <CardContent>
          {withdrawals.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No pending withdrawals</p>
            </div>
          ) : (
            <div className="space-y-3">
              {withdrawals.map((withdrawal) => (
                <div
                  key={withdrawal.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {withdrawal.account_holder_name}
                      </h4>
                      <Badge className={getStatusColor(withdrawal.status)}>
                        {withdrawal.status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Amount:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {formatCurrency(withdrawal.final_amount)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Account:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {maskAccountNumber(withdrawal.account_number)}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Bank:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {withdrawal.bank_name}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Requested:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {formatDateTime(withdrawal.requested_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="primary"
                    leftIcon={<Eye className="w-4 h-4" />}
                    onClick={() => handleReview(withdrawal)}
                  >
                    Review
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Review Modal */}
      <Modal
        isOpen={!!selectedWithdrawal}
        onClose={() => setSelectedWithdrawal(null)}
        title="Review Withdrawal Request"
        size="lg"
        footer={
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setSelectedWithdrawal(null)}>
              Cancel
            </Button>
            <Button
              variant="success"
              isLoading={isProcessing}
              onClick={handleSubmitReview}
            >
              Submit Review
            </Button>
          </div>
        }
      >
        {selectedWithdrawal && (
          <div className="space-y-6">
            {/* Amount Breakdown */}
            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                Amount Breakdown
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Requested Amount:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {formatCurrency(selectedWithdrawal.requested_amount)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">TDS (if applicable):</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    - {formatCurrency(selectedWithdrawal.tds_amount)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Processing Fee:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    - {formatCurrency(selectedWithdrawal.processing_fee)}
                  </span>
                </div>
                <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-600">
                  <span className="text-gray-900 dark:text-white font-semibold">
                    Final Amount:
                  </span>
                  <span className="text-gray-900 dark:text-white font-bold text-lg">
                    {formatCurrency(selectedWithdrawal.final_amount)}
                  </span>
                </div>
              </div>
            </div>

            {/* Bank Details */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Account Holder
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedWithdrawal.account_holder_name}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Account Number
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedWithdrawal.account_number}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">IFSC Code</label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedWithdrawal.ifsc_code}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">Bank Name</label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedWithdrawal.bank_name}
                </p>
              </div>
            </div>

            {/* Review Action */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Review Action
              </label>
              <div className="flex gap-3">
                {selectedWithdrawal.status === 'pending' && (
                  <Button
                    variant={reviewAction === 'approve' ? 'success' : 'outline'}
                    leftIcon={<CheckCircle className="w-4 h-4" />}
                    onClick={() => setReviewAction('approve')}
                  >
                    Approve
                  </Button>
                )}
                <Button
                  variant={reviewAction === 'reject' ? 'danger' : 'outline'}
                  leftIcon={<XCircle className="w-4 h-4" />}
                  onClick={() => setReviewAction('reject')}
                >
                  Reject
                </Button>
                {selectedWithdrawal.status === 'processing' && (
                  <Button
                    variant={reviewAction === 'complete' ? 'primary' : 'outline'}
                    leftIcon={<Send className="w-4 h-4" />}
                    onClick={() => setReviewAction('complete')}
                  >
                    Mark as Completed
                  </Button>
                )}
              </div>
            </div>

            {/* Rejection Reason */}
            {reviewAction === 'reject' && (
              <Input
                label="Rejection Reason"
                placeholder="Enter reason for rejection"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            )}

            {/* UTR Number */}
            {reviewAction === 'complete' && (
              <Input
                label="UTR Number"
                placeholder="Enter UTR/transaction reference number"
                value={utrNumber}
                onChange={(e) => setUtrNumber(e.target.value)}
              />
            )}

            {/* Admin Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Admin Notes (Optional)
              </label>
              <textarea
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                rows={3}
                placeholder="Add any internal notes..."
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
