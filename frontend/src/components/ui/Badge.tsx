import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}: BadgeProps) {
  const variantStyles = {
    default: 'bg-gray-100 text-text-secondary',
    primary: 'bg-primary/10 text-primary',
    success: 'bg-success/10 text-success',
    warning: 'bg-warning/10 text-warning',
    error: 'bg-error/10 text-error',
    info: 'bg-info/10 text-info',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  };

  return (
    <span
      className={`
        inline-flex items-center font-medium rounded-full
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}

interface SeverityBadgeProps {
  severity: 'critical' | 'major' | 'moderate' | 'minor';
  className?: string;
}

export function SeverityBadge({ severity, className = '' }: SeverityBadgeProps) {
  const severityConfig = {
    critical: { label: 'Critical', variant: 'error' as const },
    major: { label: 'Major', variant: 'warning' as const },
    moderate: { label: 'Moderate', variant: 'info' as const },
    minor: { label: 'Minor', variant: 'success' as const },
  };

  const config = severityConfig[severity];

  return (
    <Badge variant={config.variant} className={className}>
      {config.label}
    </Badge>
  );
}

interface RiskBadgeProps {
  risk: 'low' | 'moderate' | 'high';
  className?: string;
}

export function RiskBadge({ risk, className = '' }: RiskBadgeProps) {
  const riskConfig = {
    low: { label: 'Low Risk', variant: 'success' as const, icon: '🟢' },
    moderate: { label: 'Moderate', variant: 'warning' as const, icon: '🟡' },
    high: { label: 'High Risk', variant: 'error' as const, icon: '🔴' },
  };

  const config = riskConfig[risk];

  return (
    <Badge variant={config.variant} className={className}>
      <span className="mr-1">{config.icon}</span>
      {config.label}
    </Badge>
  );
}
