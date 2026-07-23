'use client';

import React from 'react';
import type { AlertHistoryItem } from '@/types';

interface AlertHistoryPanelProps {
  history: AlertHistoryItem[];
  onClearHistory: () => void;
}

export default function AlertHistoryPanel({ history, onClearHistory }: AlertHistoryPanelProps) {
  return (
    <div className="card">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-[var(--text-primary)]">Alert History</h2>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">Previously dismissed alerts</p>
        </div>
        {history.length > 0 && (
          <button type="button" onClick={onClearHistory} className="btn btn-ghost btn-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
            </svg>
            Clear history
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-primary)] px-5 py-4">
          <p className="text-xs text-[var(--text-muted)]">No dismissed alerts yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {history.map((item) => (
            <div
              key={`${item.id}-${item.dismissedAt}`}
              className="flex items-start gap-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-primary)] px-4 py-3"
            >
              <div className="alert-dot info" style={{ marginTop: '0.375rem' }} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="text-xs font-bold text-[var(--text-primary)]">{item.title}</p>
                  <span className="chip" style={{ background: 'rgba(99,102,241,0.08)', color: '#6366f1' }}>{item.level}</span>
                </div>
                <p className="text-[0.6875rem] text-[var(--text-muted)] line-clamp-1">{item.message}</p>
                <p className="text-[0.625rem] text-[var(--text-muted)] mt-1">
                  Dismissed {new Date(item.dismissedAt).toLocaleString()}
                </p>
              </div>
              <span className="text-xs font-semibold text-[var(--text-secondary)] flex-shrink-0">{item.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
