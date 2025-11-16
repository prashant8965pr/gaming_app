/**
 * Avatar Component
 */

import React from 'react';
import { User } from 'lucide-react';
import { cn } from '@/utils/cn';
import { getInitials } from '@/utils/format';

export interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  name,
  size = 'md',
  className,
}) => {
  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  const baseStyles = 'rounded-full flex items-center justify-center bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-200 font-semibold';

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name || 'Avatar'}
        className={cn('rounded-full object-cover', sizes[size], className)}
      />
    );
  }

  if (name) {
    return (
      <div className={cn(baseStyles, sizes[size], className)}>
        {getInitials(name)}
      </div>
    );
  }

  return (
    <div className={cn(baseStyles, sizes[size], className)}>
      <User className="w-1/2 h-1/2" />
    </div>
  );
};
