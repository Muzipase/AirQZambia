'use client';

import React, { useEffect, useState, useMemo } from 'react';
import MetricCard from '@/components/MetricCard';
import { fetchEvaluationMetrics, fetchModelComparison, fetchConfusionMatrix } from '@/lib/api';
import { EvaluationMetrics, ModelComparison, ModelMetrics, ConfusionMatrixData } from '@/types';

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

// ==================== SVG Grouped Bar Chart ====================

interface BarDatum {
  name: string;
  value: number;
  color: string;
}

interface BarGroup {
  label: string;
  bars: BarDatum[];
}

function GroupedBarChart({ groups, yMax = 1 }: { groups: BarGroup[]; yMax?: number }) {
  const W = 880;
  const H = 340;
  const pad = { top: 24, right: 20, bottom: 52, left: 52 };
  const cw = W - pad.left - pad.right;
  const ch = H - pad.top - pad.bottom;

  const { maxBarCount, groupSlot } = useMemo(() => {
    const maxBarCount = Math.max(1, ...groups.map((g) => g.bars.length));
    const groupSlot = (cw - (groups.length - 1) * 14) / Math.max(groups.length, 1);
    return { maxBarCount, groupSlot };
  }, [groups]);

  const barWidth = Math.min(48, (groupSlot - (maxBarCount - 1) * 6) / maxBarCount);
  const yScale = (v: number) => ch - (Math.min(Math.max(v, 0), yMax) / yMax) * ch;

  const ticks = Array.from({ length: 5 }, (_, i) => (i / 4) * yMax);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="xMidYMid meet">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pad.left} y1={pad.top + yScale(t)} x2={W - pad.right} y2={pad.top + yScale(t)} stroke="var(--border)" strokeDasharray="4 4" />
          <text x={pad.left - 8} y={pad.top + yScale(t) + 4} textAnchor="end" fontSize={11} fill="var(--text-muted)">
            {(t * 100).toFixed(0)}%
          </text>
        </g>
      ))}

      {groups.map((group, gi) => {
        const gx = pad.left + gi * (groupSlot + 14) + (groupSlot - (group.bars.length * barWidth + (group.bars.length - 1) * 6)) / 2;
        return (
          <g key={group.label}>
            {group.bars.map((bar, bi) => {
              const bx = gx + bi * (barWidth + 6);
              const bh = ch - yScale(bar.value);
              const by = pad.top + yScale(bar.value);
              return (
                <g key={bar.name}>
                  <rect x={bx} y={by} width={barWidth} height={Math.max(bh, 1)} rx={3} fill={bar.color}>
                    <title>{`${group.label} — ${bar.name}: ${(bar.value * 100).toFixed(1)}%`}</title>
                  </rect>
                  <text x={bx + barWidth / 2} y={by - 4} textAnchor="middle" fontSize={10} fill="var(--text-muted)">
                    {(bar.value * 100).toFixed(1)}%
                  </text>
                </g>
              );
            })}
            <text x={gx + (group.bars.length * barWidth + (group.bars.length - 1) * 6) / 2} y={H - 10} textAnchor="middle" fontSize={11} fill="var(--text-muted)">
              {group.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function ChartLegend({ items }: { items: { name: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap gap-4 justify-center">
      {items.map((item) => (
        <span key={item.name} className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
          <span className="w-3 h-3 rounded-sm" style={{ background: item.color }} />
          {item.name}
        </span>
      ))}
    </div>
  );
}

// ==================== Confusion Matrix Heatmap ====================

function ConfusionMatrixHeatmap({ labels, matrix, title, subtitle }: { labels: string[]; matrix: number[][]; title: string; subtitle?: string }) {
  const cell = 46;
  const W = labels.length * cell + 190;
  const H = labels.length * cell + 90;
  const max = Math.max(1, ...matrix.flat().map(Number));
  const fmt = (v: number) => (v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(v));

  const cellColor = (v: number) => {
    const ratio = v / max;
    if (ratio === 0) return 'var(--border-subtle)';
    const r = Math.round(20 + (6 - 20) * ratio);
    const g = Math.round(106 + (177 - 106) * ratio);
    const b = Math.round(61 + (61 - 61) * ratio);
    return `rgba(${r}, ${g}, ${b}, ${0.12 + 0.88 * ratio})`;
  };

  return (
    <div>
      <p className="text-sm font-bold text-[var(--text-primary)] mb-0.5">{title}</p>
      {subtitle && <p className="text-xs text-[var(--text-muted)] mb-3">{subtitle}</p>}
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} className="min-w-[480px]">
          {labels.map((l, i) => (
            <g key={`row-${i}`}>
              <text x={150} y={52 + i * cell + cell / 2} textAnchor="end" fontSize={11} fill="var(--text-muted)">
                {l}
              </text>
              <text x={186 + labels.length * cell + 6} y={52 + i * cell + cell / 2} textAnchor="start" fontSize={11} fill="var(--text-muted)">
                {l}
              </text>
            </g>
          ))}
          {labels.map((l, i) => (
            <text key={`col-${i}`} x={190 + i * cell + cell / 2} y={30} textAnchor="middle" fontSize={11} fill="var(--text-muted)">
              {l}
            </text>
          ))}
          {matrix.map((row, r) =>
            row.map((v, c) => (
              <rect
                key={`${r}-${c}`}
                x={190 + c * cell}
                y={38 + r * cell}
                width={cell - 2}
                height={cell - 2}
                rx={3}
                fill={cellColor(Number(v))}
                stroke="var(--border-subtle)"
                strokeWidth="0.5"
              >
                <title>{`True ${labels[r]}, Predicted ${labels[c]}: ${v}`}</title>
              </rect>
            ))
          )}
          {matrix.map((row, r) =>
            row.map((v, c) => (
              <text
                key={`val-${r}-${c}`}
                x={190 + c * cell + (cell - 2) / 2}
                y={38 + r * cell + (cell - 2) / 2 + 4}
                textAnchor="middle"
                fontSize={11}
                fontWeight={Number(v) > 0 ? 700 : 400}
                fill={Number(v) > 0 && Number(v) / max > 0.45 ? '#ffffff' : 'var(--text-muted)'}
              >
                {fmt(Number(v))}
              </text>
            ))
          )}
          <text x={190 + (labels.length * cell) / 2} y={H - 16} textAnchor="middle" fontSize={11} fill="var(--text-muted)">
            Predicted category
          </text>
          <text x={16} y={38 + (labels.length * cell) / 2} fontSize={11} fill="var(--text-muted)" transform={`rotate(-90 16 ${38 + (labels.length * cell) / 2})`} textAnchor="middle">
            True category
          </text>
        </svg>
      </div>
    </div>
  );
}

// ==================== Page ====================

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [comparison, setComparison] = useState<ModelComparison | null>(null);
  const [confusion, setConfusion] = useState<ConfusionMatrixData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const [data, comp, cm] = await Promise.all([
          fetchEvaluationMetrics(),
          fetchModelComparison(),
          fetchConfusionMatrix(),
        ]);
        if (!mounted) return;
        if (data && typeof data === 'object') setMetrics(data as EvaluationMetrics);
        setComparison(comp);
        setConfusion(cm);
      } catch (error) {
        console.error('Error loading evaluation data:', error);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, []);

  // The metrics endpoint wraps the model metrics under `metrics`; support both shapes.
  const m: ModelMetrics = useMemo(() => {
    const raw = (metrics?.metrics as ModelMetrics | undefined) ?? (metrics as unknown as ModelMetrics) ?? ({} as ModelMetrics);
    return raw;
  }, [metrics]);

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

  const baseline = comparison?.baseline_metrics;
  const optimized = comparison?.optimized_metrics ?? m;
  const perClass = (optimized?.per_class_metrics ?? m.per_class_metrics) || {};
  const compareGroups: BarGroup[] = baseline
    ? [
        { label: 'Accuracy', bars: [
          { name: 'Baseline', value: baseline.accuracy ?? 0, color: '#94a3b8' },
          { name: 'Optimized', value: optimized.accuracy ?? 0, color: '#10b981' },
        ]},
        { label: 'Precision', bars: [
          { name: 'Baseline', value: baseline.precision ?? 0, color: '#94a3b8' },
          { name: 'Optimized', value: optimized.precision ?? 0, color: '#10b981' },
        ]},
        { label: 'Recall', bars: [
          { name: 'Baseline', value: baseline.recall ?? 0, color: '#94a3b8' },
          { name: 'Optimized', value: optimized.recall ?? 0, color: '#10b981' },
        ]},
        { label: 'F1 Score', bars: [
          { name: 'Baseline', value: baseline.f1_score ?? 0, color: '#94a3b8' },
          { name: 'Optimized', value: optimized.f1_score ?? 0, color: '#10b981' },
        ]},
      ]
    : [];

  const classGroups: BarGroup[] = Object.entries(perClass).map(([label, values]) => ({
    label,
    bars: [
      { name: 'Precision', value: values?.precision ?? 0, color: '#6366f1' },
      { name: 'Recall', value: values?.recall ?? 0, color: '#ff8c00' },
      { name: 'F1', value: values?.f1_score ?? 0, color: '#006a3d' },
    ],
  }));

  // Per-class recall: Baseline vs Optimized
  const recallClasses = (() => {
    const baselinePer = baseline?.per_class_metrics ?? {};
    const optimizedPer = optimized?.per_class_metrics ?? {};
    const labels = Array.from(new Set([...Object.keys(baselinePer), ...Object.keys(optimizedPer)]));
    return labels
      .map((label) => ({
        label,
        baselineRecall: baselinePer[label]?.recall ?? 0,
        optimizedRecall: optimizedPer[label]?.recall ?? 0,
      }))
      .sort((a, b) => b.optimizedRecall - a.optimizedRecall);
  })();

  const recallCompareGroups: BarGroup[] = recallClasses.map((c) => ({
    label: c.label,
    bars: [
      { name: 'Baseline', value: c.baselineRecall, color: '#94a3b8' },
      { name: 'Optimized', value: c.optimizedRecall, color: '#10b981' },
    ],
  }));

  const recallDeltaRows = recallClasses.map((c) => ({
    label: c.label,
    baseline: c.baselineRecall,
    optimized: c.optimizedRecall,
    delta: c.optimizedRecall - c.baselineRecall,
  }));

  const compareRows = baseline
    ? [
        { metric: 'Accuracy', baseline: baseline.accuracy ?? 0, optimized: optimized.accuracy ?? 0 },
        { metric: 'Precision', baseline: baseline.precision ?? 0, optimized: optimized.precision ?? 0 },
        { metric: 'Recall', baseline: baseline.recall ?? 0, optimized: optimized.recall ?? 0 },
        { metric: 'F1 Score', baseline: baseline.f1_score ?? 0, optimized: optimized.f1_score ?? 0 },
      ]
    : [];

  const detailRows = Object.entries(m).filter(([key]) => key !== 'per_class_metrics');

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
            <ProgressCircle value={m.accuracy ?? 0} label="Accuracy" color="#006a3d" />
            <ProgressCircle value={m.precision ?? 0} label="Precision" color="#ff8c00" />
            <ProgressCircle value={m.recall ?? 0} label="Recall" color="#6366f1" />
            <ProgressCircle value={m.f1_score ?? 0} label="F1 Score" color="#de3831" />
          </div>
        </section>

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="animate-fade-in-up delay-200">
            <MetricCard
              label="Accuracy"
              value={m.accuracy ? `${(m.accuracy * 100).toFixed(1)}%` : 'N/A'}
              status="good"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14" /><path d="M22 4L12 14.01l-3-3" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-300">
            <MetricCard
              label="Precision"
              value={m.precision ? `${(m.precision * 100).toFixed(1)}%` : 'N/A'}
              status="moderate"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-400">
            <MetricCard
              label="Recall"
              value={m.recall ? `${(m.recall * 100).toFixed(1)}%` : 'N/A'}
              status="neutral"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>}
            />
          </div>
          <div className="animate-fade-in-up delay-500">
            <MetricCard
              label="F1 Score"
              value={m.f1_score ? `${(m.f1_score * 100).toFixed(1)}%` : 'N/A'}
              status="good"
              icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>}
            />
          </div>
        </section>

        {compareGroups.length > 0 && (
          <section className="card animate-fade-in-up delay-300">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">Baseline vs Optimized SVM</h3>
            <p className="text-xs text-[var(--text-muted)] mb-4">
              Standard RBF SVM compared against the Bayesian-optimized hybrid SMOTE-Tomek framework.
            </p>
            <GroupedBarChart groups={compareGroups} />
            <div className="mt-3">
              <ChartLegend
                items={[
                  { name: 'Baseline SVM', color: '#94a3b8' },
                  { name: 'Optimized SVM', color: '#10b981' },
                ]}
              />
            </div>

            <div className="mt-5 overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
              <table className="data-table">
                <thead>
                  <tr><th>Metric</th><th>Baseline</th><th>Optimized</th><th>Delta</th></tr>
                </thead>
                <tbody>
                  {compareRows.map((row) => {
                    const delta = row.optimized - row.baseline;
                    return (
                      <tr key={row.metric}>
                        <td className="capitalize font-semibold">{row.metric}</td>
                        <td className="font-bold">{(row.baseline * 100).toFixed(1)}%</td>
                        <td className="font-bold">{(row.optimized * 100).toFixed(1)}%</td>
                        <td className={`font-bold ${delta >= 0 ? 'text-[#006a3d]' : 'text-[#de3831]'}`}>
                          {delta >= 0 ? '+' : ''}{(delta * 100).toFixed(2)}pp
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {recallCompareGroups.length > 0 && (
          <section className="card animate-fade-in-up delay-350">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">Minority-Class Recall: Baseline vs Optimized</h3>
            <p className="text-xs text-[var(--text-muted)] mb-4">
              Recall per air quality category. Higher recall on minority classes (Unhealthy, Very Unhealthy)
              shows the hybrid SMOTE-Tomek framework&apos;s main contribution.
            </p>
            <GroupedBarChart groups={recallCompareGroups} />
            <div className="mt-3">
              <ChartLegend
                items={[
                  { name: 'Baseline SVM (imbalanced)', color: '#94a3b8' },
                  { name: 'Optimized SVM (SMOTE-Tomek)', color: '#10b981' },
                ]}
              />
            </div>

            <div className="mt-5 overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
              <table className="data-table">
                <thead>
                  <tr><th>Category</th><th>Baseline Recall</th><th>Optimized Recall</th><th>Delta</th></tr>
                </thead>
                <tbody>
                  {recallDeltaRows.map((row) => (
                    <tr key={row.label}>
                      <td className="capitalize font-semibold">{row.label}</td>
                      <td className="font-bold">{(row.baseline * 100).toFixed(1)}%</td>
                      <td className="font-bold">{(row.optimized * 100).toFixed(1)}%</td>
                      <td className={`font-bold ${row.delta >= 0 ? 'text-[#006a3d]' : 'text-[#de3831]'}`}>
                        {row.delta >= 0 ? '+' : ''}{(row.delta * 100).toFixed(1)}pp
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {classGroups.length > 0 && (
          <section className="card animate-fade-in-up delay-400">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">Per-Class Performance</h3>
            <p className="text-xs text-[var(--text-muted)] mb-4">
              Precision, recall, and F1 for each air quality category, highlighting minority-class behavior.
            </p>
            <GroupedBarChart groups={classGroups} />
            <div className="mt-3">
              <ChartLegend
                items={[
                  { name: 'Precision', color: '#6366f1' },
                  { name: 'Recall', color: '#ff8c00' },
                  { name: 'F1 Score', color: '#006a3d' },
                ]}
              />
            </div>
          </section>
        )}

        {confusion && confusion.labels && confusion.labels.length > 0 && (
          <section className="card animate-fade-in-up delay-450">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">Confusion Matrices</h3>
            <p className="text-xs text-[var(--text-muted)] mb-6">
              Classification breakdown per category. Rows are true categories, columns are predicted categories;
              the diagonal shows correct classifications.
            </p>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <ConfusionMatrixHeatmap
                labels={confusion.labels}
                matrix={confusion.baseline?.matrix ?? []}
                title="Baseline SVM"
                subtitle="Trained on imbalanced data without SMOTE-Tomek"
              />
              <ConfusionMatrixHeatmap
                labels={confusion.labels}
                matrix={confusion.optimized?.matrix ?? []}
                title="Optimized SVM"
                subtitle="Hybrid framework with SMOTE-Tomek balancing"
              />
            </div>
          </section>
        )}

        {detailRows.length > 0 && (
          <section className="card animate-fade-in-up delay-500">
            <h3 className="text-sm font-bold text-[var(--text-primary)] mb-4">Detailed Metrics</h3>
            <div className="overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
              <table className="data-table">
                <thead>
                  <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
                </thead>
                <tbody>
                  {detailRows.map(([key, value]) => (
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
