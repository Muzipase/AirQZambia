'use client';

import React, { useEffect, useState } from 'react';
import MetricCard from '@/components/MetricCard';
import AlertPanel from '@/components/AlertPanel';
import AlertHistoryPanel from '@/components/AlertHistoryPanel';
import { fetchSystemMetrics } from '@/lib/api';
import { AlertHistoryItem, AlertItem, SystemMetrics } from '@/types';

const ALERT_HISTORY_STORAGE_KEY = 'system-alert-history';

const getSystemAlerts = (metrics: SystemMetrics | null): AlertItem[] => {
  if (!metrics) return [];
  const alerts: AlertItem[] = [];

  if (metrics.cpu_usage != null) {
    if (metrics.cpu_usage >= 90) {
      alerts.push({ id: 'cpu-critical', level: 'critical', title: 'CPU utilization critical', message: 'CPU usage is above 90%, which may cause degraded API performance.', value: `${metrics.cpu_usage.toFixed(1)}%`, action: 'Review running processes and consider scaling.' });
    } else if (metrics.cpu_usage >= 70) {
      alerts.push({ id: 'cpu-warning', level: 'warning', title: 'High CPU usage', message: 'CPU usage is elevated and may impact response times.', value: `${metrics.cpu_usage.toFixed(1)}%`, action: 'Monitor the system and investigate heavy tasks.' });
    }
  }

  if (metrics.memory_usage != null) {
    if (metrics.memory_usage >= 90) {
      alerts.push({ id: 'memory-critical', level: 'critical', title: 'Memory usage critical', message: 'Memory consumption is above 90%, risking out-of-memory failures.', value: `${metrics.memory_usage.toFixed(1)}%`, action: 'Free memory or restart services.' });
    } else if (metrics.memory_usage >= 75) {
      alerts.push({ id: 'memory-warning', level: 'warning', title: 'High memory usage', message: 'Memory usage is elevated and may need attention soon.', value: `${metrics.memory_usage.toFixed(1)}%`, action: 'Check for memory-intensive jobs.' });
    }
  }

  if (metrics.api_response_time != null) {
    if (metrics.api_response_time >= 500) {
      alerts.push({ id: 'response-critical', level: 'critical', title: 'API response time critical', message: 'Average response time is above 500ms, degrading user experience.', value: `${metrics.api_response_time.toFixed(0)}ms`, action: 'Investigate backend latency.' });
    } else if (metrics.api_response_time >= 300) {
      alerts.push({ id: 'response-warning', level: 'warning', title: 'Slow API responses', message: 'Response time is elevated and could impact UI interactions.', value: `${metrics.api_response_time.toFixed(0)}ms`, action: 'Review recent API activity.' });
    }
  }

  if (metrics.status && metrics.status !== 'ok') {
    alerts.push({ id: 'system-status', level: 'warning', title: 'System status issue', message: `Backend reported status: ${metrics.status}.`, value: metrics.status, action: 'Check backend logs.' });
  }

  if (metrics.uptime != null && metrics.uptime < 300) {
    alerts.push({ id: 'recent-restart', level: 'info', title: 'Recent service restart', message: 'Backend has been running for less than 5 minutes.', value: `${(metrics.uptime / 60).toFixed(1)} min`, action: 'Confirm the restart is expected.' });
  }

  return alerts;
};

export default function SystemPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');
  const [alertHistory, setAlertHistory] = useState<AlertHistoryItem[]>([]);

  const loadMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSystemMetrics();
      if (data && typeof data === 'object') setMetrics(data as SystemMetrics);
      else { setMetrics(null); setError('Unable to load system metrics.'); }
    } catch (fetchError) {
      setMetrics(null);
      setError('Failed to load system metrics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = () => {
    if (typeof window === 'undefined') return;
    const raw = window.localStorage.getItem(ALERT_HISTORY_STORAGE_KEY);
    if (!raw) return;
    try { setAlertHistory(JSON.parse(raw) as AlertHistoryItem[]); } catch { setAlertHistory([]); }
  };

  const saveHistory = (history: AlertHistoryItem[]) => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(ALERT_HISTORY_STORAGE_KEY, JSON.stringify(history));
  };

  const clearHistory = () => { setAlertHistory([]); saveHistory([]); };

  const handleDismiss = (alert: AlertItem) => {
    const dismissedAt = new Date().toISOString();
    const nextHistory = [{ ...alert, dismissedAt }, ...alertHistory.filter((item) => item.id !== alert.id)];
    setAlertHistory(nextHistory);
    saveHistory(nextHistory);
  };

  useEffect(() => { loadMetrics(); loadHistory(); }, []);

  const alerts = getSystemAlerts(metrics);
  const activeAlerts = alerts.filter((alert) => !alertHistory.some((history) => history.id === alert.id));
  const visibleAlerts = filter === 'all' ? activeAlerts : activeAlerts.filter((alert) => alert.level === filter);

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <p className="page-label">System</p>
          <h1 className="page-title">Backend Health</h1>
          <p className="page-subtitle">Monitor API availability, response time, and system performance.</p>
        </div>
        <button className="btn btn-primary" onClick={loadMetrics} disabled={loading}>
          {loading ? <><span className="spinner" /> Refreshing...</> : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M23 4v6h-6M1 20v-6h6" />
                <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
              </svg>
              Refresh
            </>
          )}
        </button>
      </div>

      <div className="page-body">
        {loading && !metrics ? (
          <div className="space-y-4">
            <div className="skeleton h-32 w-full" />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton h-32" />)}
            </div>
          </div>
        ) : error ? (
          <div className="card border border-red-200 bg-red-50 animate-fade-in">
            <div className="flex items-start gap-3">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#de3831" strokeWidth="2" strokeLinecap="round" className="mt-0.5">
                <circle cx="12" cy="12" r="10" /><path d="M15 9l-6 6M9 9l6 6" />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-bold text-red-700">Connection Error</p>
                <p className="text-xs text-red-600 mt-1">{error}</p>
                <button className="btn btn-primary btn-sm mt-3" onClick={loadMetrics}>Retry</button>
              </div>
            </div>
          </div>
        ) : (
          <>
            <AlertPanel alerts={visibleAlerts} filter={filter} onFilterChange={setFilter} onDismiss={handleDismiss} />

            <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="animate-fade-in-up delay-100">
                <MetricCard
                  label="CPU Usage"
                  value={metrics?.cpu_usage != null ? `${metrics.cpu_usage.toFixed(1)}%` : 'N/A'}
                  status={metrics?.cpu_usage != null ? metrics.cpu_usage < 50 ? 'good' : metrics.cpu_usage < 80 ? 'moderate' : 'poor' : 'neutral'}
                  icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="4" width="16" height="16" rx="2" /><rect x="9" y="9" width="6" height="6" /><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" /></svg>}
                />
              </div>
              <div className="animate-fade-in-up delay-200">
                <MetricCard
                  label="Memory Usage"
                  value={metrics?.memory_usage != null ? `${metrics.memory_usage.toFixed(1)}%` : 'N/A'}
                  status={metrics?.memory_usage != null ? metrics.memory_usage < 60 ? 'good' : metrics.memory_usage < 85 ? 'moderate' : 'poor' : 'neutral'}
                  icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="6" width="20" height="12" rx="2" /><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M8 14h8" /></svg>}
                />
              </div>
              <div className="animate-fade-in-up delay-300">
                <MetricCard
                  label="API Response"
                  value={metrics?.api_response_time != null ? `${metrics.api_response_time.toFixed(0)}ms` : 'N/A'}
                  status={metrics?.api_response_time != null ? metrics.api_response_time < 200 ? 'good' : metrics.api_response_time < 500 ? 'moderate' : 'poor' : 'neutral'}
                  icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>}
                />
              </div>
              <div className="animate-fade-in-up delay-400">
                <MetricCard
                  label="Uptime"
                  value={metrics?.uptime != null ? `${(metrics.uptime / 3600).toFixed(1)}h` : 'N/A'}
                  status="good"
                  icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>}
                />
              </div>
            </section>

            <section className="card animate-fade-in-up delay-300">
              <h3 className="text-sm font-bold text-[var(--text-primary)] mb-3">System Status</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { label: 'Backend API', value: metrics ? 'Operational' : 'Unknown', good: !!metrics },
                  { label: 'Last Updated', value: metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'Never', good: !!metrics?.timestamp },
                  { label: 'Model Service', value: 'Loaded if metrics present', good: !!metrics },
                  { label: 'Status', value: metrics?.status || 'N/A', good: metrics?.status === 'ok' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-primary)] px-4 py-3">
                    <span className="text-xs text-[var(--text-muted)]">{item.label}</span>
                    <span className={`text-xs font-semibold ${item.good ? 'text-[var(--zambia-green)]' : 'text-[var(--text-secondary)]'}`}>
                      {item.value}
                    </span>
                  </div>
                ))}
              </div>
            </section>

            <AlertHistoryPanel history={alertHistory} onClearHistory={clearHistory} />
          </>
        )}
      </div>
    </div>
  );
}
