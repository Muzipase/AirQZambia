'use client';

import React from 'react';
import type { AlertItem } from '@/types';

interface AlertPanelProps {
  alerts: AlertItem[];
  filter: 'all' | 'critical' | 'warning' | 'info';
  onFilterChange: (filter: 'all' | 'critical' | 'warning' | 'info') => void;
  onDismiss: (alert: AlertItem) => void;
}

const filterOptions = [
  { label: 'All', value: 'all' as const },
  { label: 'Critical', value: 'critical' as const },
  { label: 'Warning', value: 'warning' as const },
  { label: 'Info', value: 'info' as const },
];

const levelStyles = {
  critical: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', chip: 'bg-red-100 text-red-700' },
  warning: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', chip: 'bg-amber-100 text-amber-700' },
  info: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', chip: 'bg-indigo-100 text-indigo-700' },
};

export default React.memo(function AlertPanel({ alerts, filter, onFilterChange, onDismiss }: AlertPanelProps) {
  return (
    <div className="card card-elevated">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`alert-dot ${alerts.length > 0 ? 'critical' : ''}`} style={alerts.length === 0 ? { background: '#22c55e' } : undefined} />
            <h2 className="text-base font-bold text-[var(--text-primary)]">System Alerts</h2>
          </div>
          {alerts.length > 0 && (
            <span className="chip chip-poor">{alerts.length}</span>
          )}
        </div>

        <div className="flex gap-1 p-1 bg-[var(--bg-primary)] rounded-lg">
          {filterOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onFilterChange(option.value)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                filter === option.value
                  ? 'bg-white text-[var(--zambia-green)] shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 px-5 py-4">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#006a3d" strokeWidth="2" strokeLinecap="round">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
            <path d="M22 4L12 14.01l-3-3" />
          </svg>
          <div>
            <p className="text-sm font-semibold text-[var(--zambia-green)]">All clear</p>
            <p className="text-xs text-[var(--text-muted)]">No active alerts matching the selected filter.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const styles = levelStyles[alert.level];
            return (
              <div
                key={alert.id}
                className={`rounded-xl border ${styles.border} ${styles.bg} p-4 transition-all hover:shadow-sm`}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`alert-dot ${alert.level}`} style={{ marginTop: '0.375rem' }} />
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`chip ${styles.chip}`}>{alert.level}</span>
                      </div>
                      <h3 className="text-sm font-bold text-[var(--text-primary)]">{alert.title}</h3>
                      <p className="text-xs text-[var(--text-secondary)] mt-1 leading-relaxed">{alert.message}</p>
                      {alert.action && (
                        <p className="text-xs font-medium text-[var(--zambia-green)] mt-2">
                          <span className="font-bold">Action:</span> {alert.action}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 sm:flex-shrink-0">
                    <div className="text-right">
                      <p className="text-[0.625rem] uppercase tracking-wider text-[var(--text-muted)]">Value</p>
                      <p className={`text-lg font-bold ${styles.text}`}>{alert.value}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => onDismiss(alert)}
                      className="btn btn-ghost btn-sm"
                      title="Dismiss alert"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                        <path d="M18 6L6 18M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
})
