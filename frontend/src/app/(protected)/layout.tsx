/**
 * Protected Routes Layout
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Header, Sidebar, Footer } from '@/components/layout';
import { useAuth } from '@/hooks';
import { PageLoader } from '@/components/common';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
}
