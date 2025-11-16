/**
 * Utility Functions
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Tailwind class merger
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(amount);
}

// Format date
export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date));
}

// Format date and time
export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

// Format relative time
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
  return formatDate(date);
}

// Get status badge color
export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    active: 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400',
    pending: 'bg-warning-100 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400',
    processing: 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400',
    completed: 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400',
    approved: 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400',
    verified: 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400',
    suspended: 'bg-warning-100 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400',
    banned: 'bg-danger-100 text-danger-700 dark:bg-danger-900/20 dark:text-danger-400',
    rejected: 'bg-danger-100 text-danger-700 dark:bg-danger-900/20 dark:text-danger-400',
    under_review: 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400',
  };

  return statusColors[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400';
}

// Truncate text
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

// Mask sensitive data
export function maskEmail(email: string): string {
  const [name, domain] = email.split('@');
  if (name.length <= 2) return email;
  return `${name.substring(0, 2)}****@${domain}`;
}

export function maskPhone(phone: string): string {
  if (phone.length <= 6) return phone;
  return `${phone.substring(0, 3)}****${phone.substring(phone.length - 3)}`;
}

export function maskAccountNumber(accountNumber: string): string {
  if (accountNumber.length <= 4) return accountNumber;
  return `****${accountNumber.substring(accountNumber.length - 4)}`;
}
