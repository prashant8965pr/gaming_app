/**
 * Alert Component
 */

import React from 'react';
import { AlertCircle, CheckCircle, XCircle, Info, X } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'danger';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  children,
  onClose,
  className,
}) => {
  const variants = {
    info: {
      container: 'bg-primary-50 border-primary-200 dark:bg-primary-900/20 dark:border-primary-800',
      icon: 'text-primary-600 dark:text-primary-400',
      title: 'text-primary-900 dark:text-primary-100',
      text: 'text-primary-700 dark:text-primary-200',
      Icon: Info,
    },
    success: {
      container: 'bg-success-50 border-success-200 dark:bg-success-900/20 dark:border-success-800',
      icon: 'text-success-600 dark:text-success-400',
      title: 'text-success-900 dark:text-success-100',
      text: 'text-success-700 dark:text-success-200',
      Icon: CheckCircle,
    },
    warning: {
      container: 'bg-warning-50 border-warning-200 dark:bg-warning-900/20 dark:border-warning-800',
      icon: 'text-warning-600 dark:text-warning-400',
      title: 'text-warning-900 dark:text-warning-100',
      text: 'text-warning-700 dark:text-warning-200',
      Icon: AlertCircle,
    },
    danger: {
      container: 'bg-danger-50 border-danger-200 dark:bg-danger-900/20 dark:border-danger-800',
      icon: 'text-danger-600 dark:text-danger-400',
      title: 'text-danger-900 dark:text-danger-100',
      text: 'text-danger-700 dark:text-danger-200',
      Icon: XCircle,
    },
  };

  const config = variants[variant];
  const Icon = config.Icon;

  return (
    <div className={cn('p-4 rounded-lg border', config.container, className)}>
      <div className="flex items-start">
        <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', config.icon)} />
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={cn('text-sm font-medium mb-1', config.title)}>
              {title}
            </h3>
          )}
          <div className={cn('text-sm', config.text)}>{children}</div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={cn('ml-3 flex-shrink-0', config.icon, 'hover:opacity-70')}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
