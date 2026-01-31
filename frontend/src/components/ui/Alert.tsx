import React from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';

interface AlertProps {
  type: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  children: React.ReactNode;
  className?: string;
  onDismiss?: () => void;
}

export function Alert({ type, title, children, className = '', onDismiss }: AlertProps) {
  const icons = {
    success: <CheckCircle className="text-success" size={20} />,
    warning: <AlertTriangle className="text-warning" size={20} />,
    error: <AlertCircle className="text-error" size={20} />,
    info: <Info className="text-info" size={20} />,
  };

  const styles = {
    success: 'bg-success/10 border-success/30 text-success',
    warning: 'bg-warning/10 border-warning/30 text-warning',
    error: 'bg-error/10 border-error/30 text-error',
    info: 'bg-info/10 border-info/30 text-info',
  };

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-lg border
        ${styles[type]} ${className}
      `}
      role="alert"
    >
      <div className="flex-shrink-0">{icons[type]}</div>
      <div className="flex-1">
        {title && (
          <p className="font-semibold text-text-primary">{title}</p>
        )}
        <div className="text-text-primary/90">{children}</div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 p-1 hover:bg-white/50 rounded"
        >
          ×
        </button>
      )}
    </div>
  );
}

interface RedFlagAlertProps {
  flags: string[];
  className?: string;
}

export function RedFlagAlert({ flags, className = '' }: RedFlagAlertProps) {
  if (flags.length === 0) return null;

  return (
    <Alert type="error" title="⚠️ Red Flags Detected" className={className}>
      <p className="mb-2 font-medium">
        The following symptoms require immediate medical attention:
      </p>
      <ul className="list-disc list-inside space-y-1">
        {flags.map((flag, index) => (
          <li key={index}>{flag}</li>
        ))}
      </ul>
    </Alert>
  );
}
