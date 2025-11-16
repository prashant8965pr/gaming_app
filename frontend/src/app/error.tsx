/**
 * Global Error Page
 */

'use client';

import { useEffect } from 'react';
import { Button } from '@/components/common';
import { AlertCircle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <AlertCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Something went wrong!
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          {error.message || 'An unexpected error occurred'}
        </p>
        <Button onClick={reset}>
          Try again
        </Button>
      </div>
    </div>
  );
}
