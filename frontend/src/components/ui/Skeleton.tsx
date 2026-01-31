import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
}: SkeletonProps) {
  const variantStyles = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  return (
    <div
      className={`
        bg-gray-200 animate-pulse
        ${variantStyles[variant]}
        ${className}
      `}
      style={{ width, height }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-6 border border-gray-100">
      <Skeleton className="h-4 w-1/3 mb-4" />
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-2/3 mb-4" />
      <div className="flex gap-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-6 border border-gray-100">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <Skeleton className="h-3 w-20 mb-2" />
          <Skeleton className="h-8 w-16" />
        </div>
        <Skeleton variant="circular" className="h-12 w-12" />
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-surface rounded-xl border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="flex gap-4 p-4 border-b border-gray-100">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 p-4 border-b border-gray-50">
          {[1, 2, 3, 4].map((j) => (
            <Skeleton key={j} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

export function ImageAnalysisSkeleton() {
  return (
    <div className="bg-surface rounded-xl p-6 border border-gray-100">
      <div className="flex items-center gap-2 mb-4">
        <Skeleton variant="circular" className="h-8 w-8" />
        <Skeleton className="h-4 w-32" />
      </div>
      <Skeleton className="h-48 w-full mb-4" />
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-3 w-5/6" />
      </div>
    </div>
  );
}
