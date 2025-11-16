/**
 * Formatting Utilities
 */

import { format, formatDistance, formatRelative } from 'date-fns';

/**
 * Format currency (Indian Rupees)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format number with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Format date
 */
export function formatDate(date: string | Date, formatStr = 'PPP'): string {
  return format(new Date(date), formatStr);
}

/**
 * Format date relative to now (e.g., "2 hours ago")
 */
export function formatRelativeDate(date: string | Date): string {
  return formatDistance(new Date(date), new Date(), { addSuffix: true });
}

/**
 * Format date relative (e.g., "today at 5:00 PM")
 */
export function formatRelativeTime(date: string | Date): string {
  return formatRelative(new Date(date), new Date());
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Truncate text
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return `${text.substring(0, length)}...`;
}

/**
 * Format phone number
 */
export function formatPhone(phone: string): string {
  // Format: +91 98765 43210
  if (phone.startsWith('+91')) {
    const digits = phone.substring(3);
    return `+91 ${digits.substring(0, 5)} ${digits.substring(5)}`;
  }
  return phone;
}

/**
 * Get initials from name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

/**
 * Format game session code (e.g., ABC123 -> ABC-123)
 */
export function formatSessionCode(code: string): string {
  if (code.length === 6) {
    return `${code.substring(0, 3)}-${code.substring(3)}`;
  }
  return code;
}
