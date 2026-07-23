'use client';

import React, { useEffect, useState } from 'react';
import { fetchShapSummary } from '@/lib/api';

export default function ShapAnalysisPage() {
  const [shapData, setShapData] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadShapData = async () => {
      try {
        const data = await fetchShapSummary();
        if (typeof data === 'string') setShapData(data);
      } catch (error) {
        console.error('Error loading SHAP data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadShapData();
  }, []);

  if (loading) {
    return (
      <div className="page-container">
        <div className="space-y-4">
          <div className="skeleton h-10 w-48" />
          <div className="skeleton h-6 w-72" />
          <div className="skeleton h-64 w-full" />
        </div>
      </div>
    );
  }

  const parseShapLines = (data: string) => {
    return data.split('\n').filter(Boolean).map((line) => {
      const match = line.match(/^(.+?):\s*([-\d.]+)/);
      if (match) {
        const value = parseFloat(match[2]);
        return { feature: match[1].trim(), value, isPositive: value > 0 };
      }
      return null;
    }).filter(Boolean) as { feature: string; value: number; isPositive: boolean }[];
  };

  const shapFeatures = shapData ? parseShapLines(shapData) : [];
  const maxAbsValue = shapFeatures.length > 0 ? Math.max(...shapFeatures.map((f) => Math.abs(f.value))) : 1;

  return (
    <div className="page-container">
      <div className="page-header">
        <p className="page-label">SHAP Analysis</p>
        <h1 className="page-title">Model Explainability</h1>
        <p className="page-subtitle">Understand which features drive air quality predictions.</p>
      </div>

      <div className="page-body">
        {shapFeatures.length > 0 && (
          <section className="card card-elevated animate-fade-in-up delay-100">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">Feature Impact</h3>
            <p className="text-xs text-[var(--text-muted)] mb-5">How each feature influences the prediction direction</p>
            <div className="space-y-3">
              {shapFeatures.map((item) => (
                <div key={item.feature} className="flex items-center gap-2 sm:gap-3">
                  <span className="text-xs font-semibold text-[var(--text-secondary)] w-20 sm:w-28 flex-shrink-0 truncate" title={item.feature}>
                    {item.feature}
                  </span>
                  <div className="flex-1 relative h-5 flex items-center">
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[var(--border-default)]" />
                    {item.isPositive ? (
                      <div
                        className="absolute left-1/2 top-0.5 bottom-0.5 rounded-r-sm transition-all duration-700"
                        style={{
                          width: `${(Math.abs(item.value) / maxAbsValue) * 50}%`,
                          background: 'linear-gradient(90deg, rgba(0,106,61,0.12), rgba(0,106,61,0.45))',
                        }}
                      />
                    ) : (
                      <div
                        className="absolute right-1/2 top-0.5 bottom-0.5 rounded-l-sm transition-all duration-700"
                        style={{
                          width: `${(Math.abs(item.value) / maxAbsValue) * 50}%`,
                          background: 'linear-gradient(270deg, rgba(222,56,49,0.12), rgba(222,56,49,0.45))',
                        }}
                      />
                    )}
                  </div>
                  <span className={`text-xs font-bold w-14 sm:w-16 text-right ${item.isPositive ? 'text-[var(--zambia-green)]' : 'text-[var(--zambia-red)]'}`}>
                    {item.value > 0 ? '+' : ''}{item.value.toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-4 text-[0.625rem] text-[var(--text-muted)]">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-sm" style={{ background: 'rgba(222,56,49,0.5)' }} />
                Reduces risk
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-sm" style={{ background: 'rgba(0,106,61,0.5)' }} />
                Increases risk
              </span>
            </div>
          </section>
        )}

        <section className="card animate-fade-in-up delay-200">
          <h3 className="text-sm font-bold text-[var(--text-primary)] mb-3">Raw SHAP Summary</h3>
          <div className="code-block">
            {shapData || 'SHAP analysis data is currently unavailable.'}
          </div>
        </section>

        <section className="card animate-fade-in-up delay-300">
          <div className="flex items-center gap-2 mb-3">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" />
            </svg>
            <p className="text-xs font-bold text-[var(--text-primary)]">Interpreting SHAP Values</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { icon: '\u2191', color: '#006a3d', label: 'Positive SHAP', desc: 'Increases predicted air quality risk' },
              { icon: '\u2193', color: '#de3831', label: 'Negative SHAP', desc: 'Reduces predicted air quality risk' },
              { icon: '\u25c6', color: '#6366f1', label: 'Magnitude', desc: 'Larger values = stronger feature impact' },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-primary)] p-4 text-center">
                <span className="text-2xl" style={{ color: item.color }}>{item.icon}</span>
                <p className="text-xs font-bold text-[var(--text-primary)] mt-2">{item.label}</p>
                <p className="text-[0.6875rem] text-[var(--text-muted)] mt-1">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
