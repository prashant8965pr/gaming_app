/**
 * Badge Component
 */

import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400',
      success: 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400',
      warning: 'bg-warning-100 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400',
      danger: 'bg-danger-100 text-danger-700 dark:bg-danger-900/20 dark:text-danger-400',
    };

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

export default Badge;
