'use client';

import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  status?: 'good' | 'moderate' | 'poor' | 'neutral';
  icon?: React.ReactNode;
  trend?: number[];
}

function ProgressRing({ value, status }: { value: number; status: string }) {
  const radius = 16;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(value, 100) / 100) * circumference;

  return (
    <div className="progress-ring">
      <svg width="44" height="44" viewBox="0 0 44 44">
        <circle className="progress-ring-track" cx="22" cy="22" r={radius} />
        <circle
          className={`progress-ring-fill ${status}`}
          cx="22"
          cy="22"
          r={radius}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-[0.625rem] font-bold" style={{ color: 'inherit' }}>
        {Math.round(value)}
      </span>
    </div>
  );
}

function MiniTrend({ data }: { data: number[] }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = 72;
  const height = 24;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="mt-1.5 opacity-50">
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default React.memo(function MetricCard({ label, value, change, status = 'neutral', icon, trend }: MetricCardProps) {
  return (
    <div className={`metric-card status-${status}`}>
      <div className="flex items-start justify-between">
        <div className={`metric-card-icon ${status}`}>
          {icon || (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          )}
        </div>
        <ProgressRing
          value={typeof value === 'string' ? parseFloat(value) || 0 : value}
          status={status}
        />
      </div>
      <p className="text-[0.6875rem] font-medium text-[var(--text-muted)] mt-1">{label}</p>
      <p className={`metric-card-value ${status}`}>{value}</p>
      <div className="flex items-center justify-between mt-0.5">
        {change && (
          <p className="text-[0.6875rem] text-[var(--text-muted)]">{change}</p>
        )}
        {trend && <MiniTrend data={trend} />}
      </div>
    </div>
  );
})
