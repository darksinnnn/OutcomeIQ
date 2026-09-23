import React from 'react';
import { Loader2, AlertCircle, Database } from 'lucide-react';

interface StateWrapperProps {
  isLoading?: boolean;
  isError?: boolean;
  errorText?: string;
  isEmpty?: boolean;
  emptyText?: string;
  onRetry?: () => void;
  children: React.ReactNode;
}

export const StateWrapper: React.FC<StateWrapperProps> = ({
  isLoading,
  isError,
  errorText = 'Failed to fetch telemetry or model prediction data.',
  isEmpty,
  emptyText = 'No active mission records found.',
  onRetry,
  children,
}) => {
  if (isLoading) {
    return (
      <div className="bg-panel border border-hairline rounded-md p-12 flex flex-col items-center justify-center text-center my-6">
        <Loader2 className="w-8 h-8 text-accent animate-spin mb-3" />
        <p className="text-text-primary font-display font-medium text-sm">
          Computing Mission Reasoning...
        </p>
        <p className="text-text-muted font-body text-xs mt-1">
          Evaluating telemetry stream, operator capability, and time quantile bands.
        </p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-panel border border-status-red/30 rounded-md p-8 flex flex-col items-center justify-center text-center my-6">
        <AlertCircle className="w-8 h-8 text-status-red mb-3" />
        <p className="text-text-primary font-display font-medium text-sm">
          Data Integration Warning
        </p>
        <p className="text-text-secondary font-body text-xs mt-1 max-w-md">
          {errorText}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 px-3 py-1.5 bg-elevated hover:bg-hairline text-text-primary text-xs font-display rounded-sm border border-hairline transition-colors"
          >
            Retry Connection
          </button>
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="bg-panel border border-hairline rounded-md p-12 flex flex-col items-center justify-center text-center my-6">
        <Database className="w-8 h-8 text-text-muted mb-3" />
        <p className="text-text-secondary font-display font-medium text-sm">
          {emptyText}
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
