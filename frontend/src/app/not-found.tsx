/**
 * 404 Not Found Page
 */

import Link from 'next/link';
import { Button } from '@/components/common';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-600 mb-4">404</h1>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Page Not Found
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Link href="/">
          <Button leftIcon={<Home className="w-4 h-4" />}>
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
