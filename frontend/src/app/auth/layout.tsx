/**
 * Auth Layout
 */

import { Trophy } from 'lucide-react';
import Link from 'next/link';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <Link href="/" className="flex items-center space-x-2 mb-8">
          <Trophy className="w-8 h-8 text-primary-600" />
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            Gaming Platform
          </span>
        </Link>
        {children}
      </div>
    </div>
  );
}
