'use client';

import React, { useState, useCallback } from 'react';
import FormBuilder from '@/components/FormBuilder';
import { makePrediction, fetchLivePrediction, fetchCityAirQuality } from '@/lib/api';
import { PredictionInput, PredictionResult } from '@/types';

const CITIES = ['Lusaka', 'Ndola', 'Kitwe'];

interface LiveReadings {
  pm25: number;
  pm10: number;
  no2: number;
  so2: number;
  co: number;
  o3: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
}

export default function PredictionsPage() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [liveReadings, setLiveReadings] = useState<LiveReadings | null>(null);
  const [liveSource, setLiveSource] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [liveLoading, setLiveLoading] = useState(false);
  const [formValues, setFormValues] = useState<Record<string, number>>({});

  const handleCitySelect = useCallback(async (city: string) => {
    setLiveLoading(true);
    setError(null);
    setResult(null);
    setLiveReadings(null);
    try {
      const liveData = await fetchLivePrediction(city);
      if (liveData && liveData.live_readings) {
        setLiveReadings(liveData.live_readings);
        setLiveSource(`Live from Open-Meteo at ${new Date(liveData.timestamp).toLocaleTimeString()}`);
        setFormValues({
          pm25: liveData.live_readings.pm25,
          pm10: liveData.live_readings.pm10,
          no2: liveData.live_readings.no2,
          so2: liveData.live_readings.so2,
          co: liveData.live_readings.co,
          o3: liveData.live_readings.o3,
          temperature: liveData.live_readings.temperature,
          humidity: liveData.live_readings.humidity,
          wind_speed: liveData.live_readings.wind_speed,
        });
        setResult({
          prediction: liveData.prediction,
          confidence: liveData.confidence,
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch live data. The model may not be trained yet.');
    } finally {
      setLiveLoading(false);
    }
  }, []);

  const formFields = [
    { name: 'pm25', label: 'PM2.5 (µg/m³)', type: 'number' as const, min: 0, defaultValue: formValues.pm25 ?? 25, group: 'Pollutants', hint: 'Fine particulate matter' },
    { name: 'pm10', label: 'PM10 (µg/m³)', type: 'number' as const, min: 0, defaultValue: formValues.pm10 ?? 50, group: 'Pollutants', hint: 'Coarse particulate matter' },
    { name: 'no2', label: 'NO₂ (ppb)', type: 'number' as const, min: 0, defaultValue: formValues.no2 ?? 20, group: 'Pollutants', hint: 'Nitrogen dioxide' },
    { name: 'so2', label: 'SO₂ (ppb)', type: 'number' as const, min: 0, defaultValue: formValues.so2 ?? 5, group: 'Pollutants', hint: 'Sulfur dioxide' },
    { name: 'co', label: 'CO (ppm)', type: 'number' as const, min: 0, step: 0.1, defaultValue: formValues.co ?? 0.5, group: 'Pollutants', hint: 'Carbon monoxide' },
    { name: 'o3', label: 'O₃ (ppb)', type: 'number' as const, min: 0, defaultValue: formValues.o3 ?? 30, group: 'Pollutants', hint: 'Ground-level ozone' },
    { name: 'temperature', label: 'Temperature (°C)', type: 'number' as const, defaultValue: formValues.temperature ?? 25, group: 'Weather', hint: 'Ambient temperature' },
    { name: 'humidity', label: 'Humidity (%)', type: 'number' as const, min: 0, max: 100, defaultValue: formValues.humidity ?? 60, group: 'Weather', hint: 'Relative humidity' },
    { name: 'wind_speed', label: 'Wind Speed (m/s)', type: 'number' as const, min: 0, step: 0.1, defaultValue: formValues.wind_speed ?? 5, group: 'Weather', hint: 'Surface wind speed' },
  ];

  const handleSubmit = async (data: Record<string, any>) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload: PredictionInput = {
        pm25: Number(data.pm25 ?? 0),
        pm10: Number(data.pm10 ?? 0),
        no2: Number(data.no2 ?? 0),
        so2: Number(data.so2 ?? 0),
        co: Number(data.co ?? 0),
        o3: Number(data.o3 ?? 0),
        temperature: Number(data.temperature ?? 0),
        humidity: Number(data.humidity ?? 0),
        wind_speed: Number(data.wind_speed ?? 0),
      };
      const prediction = await makePrediction(payload);
      setResult(prediction);
    } catch (err: any) {
      setError(err.message || 'Failed to get prediction.');
    } finally {
      setLoading(false);
    }
  };

  const getPredictionStyle = (pred: string) => {
    const p = String(pred).toLowerCase();
    if (p.includes('good')) return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', accent: '#006a3d' };
    if (p.includes('moderate')) return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', accent: '#ff8c00' };
    return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', accent: '#de3831' };
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <p className="page-label">Predictions</p>
        <h1 className="page-title">Live Air Quality Prediction</h1>
        <p className="page-subtitle">Select a city for live Open-Meteo readings, or enter values manually for what-if analysis.</p>
      </div>

      <div className="page-body">
        {/* City Selector for Live Data */}
        <div className="card card-elevated animate-fade-in-up">
          <div className="flex items-center gap-2 mb-4">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" /><path d="M2 12h20" />
            </svg>
            <p className="text-sm font-bold text-[var(--text-primary)]">Quick: Fetch Live Data</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {CITIES.map((city) => (
              <button
                key={city}
                onClick={() => handleCitySelect(city)}
                disabled={liveLoading}
                className="px-4 py-2 rounded-lg text-sm font-semibold border border-[var(--border)] hover:border-[var(--zambia-green)] hover:bg-green-50 transition-all disabled:opacity-50"
              >
                {liveLoading ? 'Loading...' : `Use ${city} Live Data`}
              </button>
            ))}
          </div>
          {liveSource && (
            <p className="text-xs text-green-600 mt-2 font-medium">✓ {liveSource}</p>
          )}
        </div>

        {/* Manual Prediction Form */}
        <div className="card card-elevated animate-fade-in-up delay-100">
          <div className="flex items-center gap-2 mb-3">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
              <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
            <p className="text-xs font-bold text-[var(--text-primary)]">Or enter values manually</p>
          </div>
          <FormBuilder key={JSON.stringify(formValues)} fields={formFields} onSubmit={handleSubmit} buttonLabel="Run Prediction" loading={loading} />
        </div>

        {/* Prediction Result */}
        {result && (
          <div className="space-y-4 animate-scale-in">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className={`card card-elevated border ${getPredictionStyle(String(result.prediction)).border} ${getPredictionStyle(String(result.prediction)).bg}`}>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${getPredictionStyle(String(result.prediction)).accent}12`, color: getPredictionStyle(String(result.prediction)).accent }}>
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-[0.625rem] font-bold uppercase tracking-wider text-[var(--text-muted)]">SVM Classification</p>
                    <p className={`text-2xl font-extrabold ${getPredictionStyle(String(result.prediction)).text}`}>{result.prediction}</p>
                  </div>
                </div>
                {liveReadings && (
                  <p className="text-[0.625rem] text-[var(--text-muted)] mt-1">Classified by Bayesian-optimized SVM from live sensor data</p>
                )}
              </div>

              {result.confidence !== undefined && (
                <div className="card card-elevated">
                  <p className="text-[0.625rem] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2">Confidence</p>
                  <span className="text-3xl font-extrabold text-[var(--text-primary)]">{(result.confidence * 100).toFixed(1)}%</span>
                  <div className="prob-bar mt-3">
                    <div className="prob-bar-fill" style={{ width: `${result.confidence * 100}%`, background: 'linear-gradient(90deg, #006a3d, #10b981)' }} />
                  </div>
                </div>
              )}
            </div>

            {liveReadings && (
              <div className="card card-elevated">
                <p className="text-sm font-bold text-[var(--text-primary)] mb-3">Live Readings Used</p>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(liveReadings).map(([key, val]) => (
                    <div key={key} className="text-center p-2 rounded-lg bg-gray-50">
                      <p className="text-[0.625rem] uppercase tracking-wider text-[var(--text-muted)]">{key.replace('_', ' ')}</p>
                      <p className="text-sm font-bold text-[var(--text-primary)]">{typeof val === 'number' ? val.toFixed(1) : val}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.probability && (
              <div className="card card-elevated">
                <p className="text-sm font-bold text-[var(--text-primary)] mb-4">Probability Distribution</p>
                <div className="space-y-3">
                  {Object.entries(result.probability).map(([label, prob]) => (
                    <div key={label} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-medium text-[var(--text-secondary)]">{label}</span>
                        <span className="font-bold text-[var(--text-primary)]">{(prob * 100).toFixed(1)}%</span>
                      </div>
                      <div className="prob-bar">
                        <div
                          className="prob-bar-fill"
                          style={{
                            width: `${prob * 100}%`,
                            background: `linear-gradient(90deg, ${prob > 0.5 ? '#006a3d' : prob > 0.2 ? '#ff8c00' : '#de3831'}, ${prob > 0.5 ? '#10b981' : prob > 0.2 ? '#fbbf24' : '#ef4444'})`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="card border border-red-200 bg-red-50 animate-fade-in">
            <div className="flex items-start gap-3">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#de3831" strokeWidth="2" strokeLinecap="round" className="mt-0.5">
                <circle cx="12" cy="12" r="10" /><path d="M15 9l-6 6M9 9l6 6" />
              </svg>
              <div>
                <p className="text-sm font-bold text-red-700">Prediction Error</p>
                <p className="text-xs text-red-600 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="card animate-fade-in-up delay-300">
          <div className="flex items-center gap-2 mb-3">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" />
            </svg>
            <p className="text-xs font-bold text-[var(--text-primary)]">How it works</p>
          </div>
          <ul className="space-y-1.5 text-xs text-[var(--text-secondary)]">
            <li className="flex items-start gap-2">
              <span className="w-1 h-1 rounded-full bg-[var(--zambia-green)] mt-1.5 flex-shrink-0" />
              <strong>Live mode:</strong> Select a city to fetch real-time PM2.5, PM10, NO₂, and weather from Open-Meteo, then classify with the SVM.
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1 h-1 rounded-full bg-[var(--zambia-green)] mt-1.5 flex-shrink-0" />
              <strong>Manual mode:</strong> Enter any pollutant and weather values to run what-if analysis through the same SVM model.
            </li>
            <li className="flex items-start gap-2">
              <span className="w-1 h-1 rounded-full bg-[var(--zambia-green)] mt-1.5 flex-shrink-0" />
              The Bayesian-optimized SVM classifies air quality into Good, Moderate, Unhealthy, Very Unhealthy, or Hazardous.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
