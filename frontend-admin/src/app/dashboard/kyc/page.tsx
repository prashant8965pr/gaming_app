/**
 * KYC Management Page
 * Review and approve/reject KYC documents
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { FileCheck, Eye, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
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
import { formatDateTime, getStatusColor } from '@/lib/utils';
import { api } from '@/lib/api';
import type { KYCDocument, ReviewKYCRequest } from '@/types';

export default function KYCManagementPage() {
  const [documents, setDocuments] = useState<KYCDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<KYCDocument | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isReviewing, setIsReviewing] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approve' | 'reject' | 'request_resubmit'>('approve');
  const [rejectionReason, setRejectionReason] = useState('');
  const [adminNotes, setAdminNotes] = useState('');

  useEffect(() => {
    loadPendingKYC();
  }, []);

  const loadPendingKYC = async () => {
    try {
      const data = await api.getPendingKYC({ limit: 100 });
      setDocuments(data.documents);
    } catch (error) {
      console.error('Failed to load KYC documents:', error);
      toast.error('Failed to load KYC documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReview = (doc: KYCDocument) => {
    setSelectedDoc(doc);
    setReviewAction('approve');
    setRejectionReason('');
    setAdminNotes('');
  };

  const handleSubmitReview = async () => {
    if (!selectedDoc) return;

    if (reviewAction !== 'approve' && !rejectionReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }

    setIsReviewing(true);
    try {
      const reviewData: ReviewKYCRequest = {
        kyc_id: selectedDoc.id,
        action: reviewAction,
        rejection_reason: rejectionReason.trim() || undefined,
        admin_notes: adminNotes.trim() || undefined,
      };

      await api.reviewKYC(reviewData);
      toast.success(`KYC document ${reviewAction}d successfully!`);
      setSelectedDoc(null);
      loadPendingKYC();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to review KYC document';
      toast.error(message);
    } finally {
      setIsReviewing(false);
    }
  };

  if (isLoading) {
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">KYC Management</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Review and approve KYC documents
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pending Review</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {documents.length}
                </p>
              </div>
              <FileCheck className="w-8 h-8 text-warning-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* KYC List */}
      <Card>
        <CardHeader>
          <CardTitle>Pending KYC Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-12">
              <FileCheck className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">No pending KYC documents</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {doc.full_name}
                      </h4>
                      <Badge className={getStatusColor(doc.status)}>{doc.status}</Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Document:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {doc.document_type}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Number:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {doc.document_number}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">DOB:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {new Date(doc.date_of_birth).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Submitted:</span>
                        <p className="text-gray-900 dark:text-white font-medium">
                          {formatDateTime(doc.submitted_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="primary"
                    leftIcon={<Eye className="w-4 h-4" />}
                    onClick={() => handleReview(doc)}
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
        isOpen={!!selectedDoc}
        onClose={() => setSelectedDoc(null)}
        title="Review KYC Document"
        size="xl"
        footer={
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => setSelectedDoc(null)}>
              Cancel
            </Button>
            <Button
              variant="success"
              isLoading={isReviewing}
              onClick={handleSubmitReview}
            >
              Submit Review
            </Button>
          </div>
        }
      >
        {selectedDoc && (
          <div className="space-y-6">
            {/* User Info */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">Full Name</label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedDoc.full_name}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">Date of Birth</label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {new Date(selectedDoc.date_of_birth).toLocaleDateString()}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">Document Type</label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedDoc.document_type}
                </p>
              </div>
              <div>
                <label className="text-sm text-gray-600 dark:text-gray-400">
                  Document Number
                </label>
                <p className="text-gray-900 dark:text-white font-medium">
                  {selectedDoc.document_number}
                </p>
              </div>
            </div>

            {/* Documents */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                Document Images
              </h4>
              <div className="grid grid-cols-3 gap-4">
                {selectedDoc.document_front_url && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Front</p>
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <img
                        src={selectedDoc.document_front_url}
                        alt="Document Front"
                        className="w-full h-48 object-cover"
                      />
                    </div>
                  </div>
                )}
                {selectedDoc.document_back_url && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Back</p>
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <img
                        src={selectedDoc.document_back_url}
                        alt="Document Back"
                        className="w-full h-48 object-cover"
                      />
                    </div>
                  </div>
                )}
                {selectedDoc.selfie_url && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Selfie</p>
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <img
                        src={selectedDoc.selfie_url}
                        alt="Selfie"
                        className="w-full h-48 object-cover"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Review Action */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Review Action
              </label>
              <div className="flex gap-3">
                <Button
                  variant={reviewAction === 'approve' ? 'success' : 'outline'}
                  leftIcon={<CheckCircle className="w-4 h-4" />}
                  onClick={() => setReviewAction('approve')}
                >
                  Approve
                </Button>
                <Button
                  variant={reviewAction === 'reject' ? 'danger' : 'outline'}
                  leftIcon={<XCircle className="w-4 h-4" />}
                  onClick={() => setReviewAction('reject')}
                >
                  Reject
                </Button>
                <Button
                  variant={reviewAction === 'request_resubmit' ? 'warning' : 'outline'}
                  leftIcon={<AlertCircle className="w-4 h-4" />}
                  onClick={() => setReviewAction('request_resubmit')}
                >
                  Request Resubmit
                </Button>
              </div>
            </div>

            {/* Rejection Reason */}
            {reviewAction !== 'approve' && (
              <Input
                label="Rejection Reason"
                placeholder="Enter reason for rejection or resubmit request"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
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
