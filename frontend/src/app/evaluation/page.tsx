'use client';

import React, { useEffect, useState } from 'react';
import MetricCard from '@/components/MetricCard';
import { fetchEvaluationMetrics } from '@/lib/api';
import { EvaluationMetrics } from '@/types';

function ProgressCircle({ value, label, color }: { value: number; label: string; color: string }) {
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(value * 100, 100) / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg width="96" height="96" viewBox="0 0 96 96">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="var(--border-default)" strokeWidth="5" />
          <circle
            cx="48"
            cy="48"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-base font-extrabold" style={{ color }}>
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <p className="text-xs font-semibold text-[var(--text-secondary)]">{label}</p>
    </div>
  );
}

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await fetchEvaluationMetrics();
        if (data && typeof data === 'object') setMetrics(data as EvaluationMetrics);
      } catch (error) {
        console.error('Error loading evaluation metrics:', error);
      } finally {
        setLoading(false);
      }
    };
    loadMetrics();
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="space-y-4">
          <div className="skeleton h-10 w-48" />
          <div className="skeleton h-6 w-72" />
          <div className="skeleton h-48 w-full" />
          <div className="skeleton h-64 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <p className="page-label">Evaluation</p>
        <h1 className="page-title">Model Performance</h1>
        <p className="page-subtitle">Comprehensive evaluation metrics for the air quality classification model.</p>
      </div>

      <div className="page-body">
        <section className="card card-elevated animate-fade-in-up delay-100">
          <h3 className="text-sm font-bold text-[var(--text-primary)] mb-6">Performance Overview</h3>
          <div className="flex flex-wrap justify-center gap-8 sm:gap-12">
            <ProgressCircle value={metrics?.accuracy ?? 0} label="Accuracy" color="#006a3d" />
            <ProgressCircle value={metrics?.precision ?? 0} label="Precision" color="#ff8c00" />
            <ProgressCircle value={metrics?.recall ?? 0} label="Recall" color="#6366f1" />
            <ProgressCircle value={metrics?.f1_score ?? 0} label="F1 Score" color="#de3831" />
          </div>
        </section>

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="animate-fade-in-up delay-200">
            <MetricCard
              label="Accuracy"
              value={metrics?.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}
              status="good"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14" /><path d="M22 4L12 14.01l-3-3" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-300">
            <MetricCard
              label="Precision"
              value={metrics?.precision ? `${(metrics.precision * 100).toFixed(1)}%` : 'N/A'}
              status="moderate"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-400">
            <MetricCard
              label="Recall"
              value={metrics?.recall ? `${(metrics.recall * 100).toFixed(1)}%` : 'N/A'}
              status="neutral"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-500">
            <MetricCard
              label="F1 Score"
              value={metrics?.f1_score ? `${(metrics.f1_score * 100).toFixed(1)}%` : 'N/A'}
              status="good"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>}
            />
          </div>
        </section>

        {metrics && (
          <section className="card animate-fade-in-up delay-300">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-4">Detailed Metrics</h3>
            <div className="overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
              <table className="data-table">
                <thead>
                  <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
                </thead>
                <tbody>
                  {Object.entries(metrics).map(([key, value]) => (
                    <tr key={key}>
                      <td className="capitalize font-semibold">{key.replace(/_/g, ' ')}</td>
                      <td className="font-bold">{typeof value === 'number' ? value.toFixed(4) : String(value)}</td>
                      <td className="text-[var(--text-muted)]">
                        {key === 'accuracy' && 'Overall prediction correctness'}
                        {key === 'precision' && 'Positive prediction reliability'}
                        {key === 'recall' && 'True positive detection rate'}
                        {key === 'f1_score' && 'Harmonic mean of precision & recall'}
                        {key === 'confusion_matrix' && 'Classification breakdown'}
                        {!['accuracy', 'precision', 'recall', 'f1_score', 'confusion_matrix'].includes(key) && '\u2014'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        <section className="card animate-fade-in-up delay-400">
          <div className="flex items-center gap-2 mb-3">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" />
            </svg>
            <p className="text-xs font-bold text-[var(--text-primary)]">What these metrics mean</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { metric: 'Accuracy', desc: 'Percentage of all predictions that were correct.' },
              { metric: 'Precision', desc: 'Of predicted positives, how many were actually positive.' },
              { metric: 'Recall', desc: 'Of actual positives, how many were correctly identified.' },
              { metric: 'F1 Score', desc: 'Harmonic mean balancing precision and recall.' },
            ].map((item) => (
              <div key={item.metric} className="flex items-start gap-2 text-xs">
                <span className="w-1 h-1 rounded-full bg-[var(--zambia-green)] mt-1.5 flex-shrink-0" />
                <span><span className="font-semibold text-[var(--text-primary)]">{item.metric}:</span> <span className="text-[var(--text-muted)]">{item.desc}</span></span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
