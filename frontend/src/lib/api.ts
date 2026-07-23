import useSWR from 'swr';
import type { CityAirQuality, EvaluationMetrics, ForecastData, PredictionInput, PredictionResult } from '@/types';

function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:8000';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

const fetcher = (url: string) => fetch(url).then((r) => r.json());

// ==================== Status ====================
export async function fetchApiStatus(retries = 2): Promise<any> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const url = `${getApiBaseUrl()}/status`;
      const response = await fetch(url, { signal: AbortSignal.timeout(5000) });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
        continue;
      }
      console.error('API status check failed after retries:', error);
      return null;
    }
  }
  return null;
}

// ==================== City Air Quality ====================
export async function fetchCityAirQuality(cityName: string): Promise<CityAirQuality | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error fetching air quality for ${cityName}:`, error);
    return null;
  }
}

// ==================== City Forecast ====================
export async function fetchCityForecast(cityName: string, forecastDays: number = 3): Promise<ForecastData | null> {
  try {
    const response = await fetch(`${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}/forecast?forecast_days=${forecastDays}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error fetching forecast for ${cityName}:`, error);
    return null;
  }
}

// ==================== Predictions ====================
export async function makePrediction(
  data: PredictionInput,
  modelType: 'baseline' | 'optimized' = 'optimized'
): Promise<PredictionResult> {
  try {
    const params = modelType === 'baseline' ? '?model_type=baseline' : '';
    return await request<PredictionResult>(`/api/predict${params}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  } catch (error) {
    console.error('Error making prediction:', error);
    throw error;
  }
}

// ==================== Evaluation ====================
export async function fetchEvaluationMetrics(): Promise<EvaluationMetrics> {
  try {
    return await request<EvaluationMetrics>('/api/evaluation/metrics');
  } catch (error) {
    console.error('Error fetching evaluation metrics:', error);
    return {};
  }
}

// ==================== SHAP Explainability ====================
export async function fetchShapSummary() {
  try {
    return await request('/api/explainability/shap-summary');
  } catch (error) {
    console.error('Error fetching SHAP summary:', error);
    return 'SHAP explainability details are currently unavailable.';
  }
}

export async function fetchShapForce(instanceIndex: number) {
  try {
    return await request(`/api/explainability/force/${instanceIndex}`);
  } catch (error) {
    console.error('Error fetching SHAP force plot:', error);
    return null;
  }
}

// ==================== Live Prediction ====================
export async function fetchLivePrediction(
  city: string,
  modelType: 'baseline' | 'optimized' = 'optimized'
): Promise<any> {
  try {
    const modelParam = modelType === 'baseline' ? '&model_type=baseline' : '';
    return await request(`/api/predict/live?city=${encodeURIComponent(city)}${modelParam}`);
  } catch (error) {
    console.error(`Error fetching live prediction for ${city}:`, error);
    throw error;
  }
}

// ==================== Batch Predictions ====================
export async function batchPredict(
  csvData: string,
  modelType: 'baseline' | 'optimized' = 'optimized'
) {
  try {
    const formData = new FormData();
    formData.append('file', new Blob([csvData], { type: 'text/csv' }), 'data.csv');

    const params = modelType === 'baseline' ? '?model_type=baseline' : '';
    const response = await fetch(`${getApiBaseUrl()}/api/predict/batch${params}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error in batch prediction:', error);
    throw error;
  }
}

// ==================== System Info ====================
export async function fetchSystemMetrics() {
  try {
    return await request('/api/system/metrics');
  } catch (error) {
    console.error('Error fetching system metrics:', error);
    return null;
  }
}

// ==================== Historical Air Quality ====================
export interface HistoricalDay {
  date: string;
  pm25?: number | null;
  pm25_max?: number | null;
  pm10?: number | null;
  pm10_max?: number | null;
  no2?: number | null;
  no2_max?: number | null;
  so2?: number | null;
  so2_max?: number | null;
  co?: number | null;
  co_max?: number | null;
  o3?: number | null;
  o3_max?: number | null;
}

export interface HistoricalData {
  status: string;
  city: string;
  message?: string;
  date_range: { start: string; end: string };
  pollutants: string[];
  daily: HistoricalDay[];
  stats: Record<string, { min: number; max: number; mean: number; trend: string; count: number }>;
}

export async function fetchCityHistorical(
  cityName: string,
  startDate: string,
  endDate: string,
  pollutants: string[] = ['pm25', 'pm10', 'no2', 'o3'],
): Promise<HistoricalData | null> {
  try {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      pollutants: pollutants.join(','),
    });
    const response = await fetch(`${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}/historical?${params}`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.error(`Error fetching historical data for ${cityName}:`, error);
    return null;
  }
}

// ==================== SWR Hooks ====================

export function useCityAirQuality(cityName: string) {
  return useSWR<CityAirQuality | null>(
    `${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}`,
    fetcher,
    { refreshInterval: 60000, revalidateOnFocus: true }
  );
}

export function useCityForecast(cityName: string, forecastDays: number = 3) {
  return useSWR<ForecastData | null>(
    `${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}/forecast?forecast_days=${forecastDays}`,
    fetcher,
    { refreshInterval: 120000 }
  );
}

export function useEvaluationMetrics() {
  return useSWR<EvaluationMetrics>(
    `${getApiBaseUrl()}/api/evaluation/metrics`,
    fetcher,
    { revalidateOnFocus: false }
  );
}

export function useShapSummary() {
  return useSWR(
    `${getApiBaseUrl()}/api/explainability/shap-summary`,
    fetcher,
    { revalidateOnFocus: false }
  );
}

export function useSystemMetrics() {
  return useSWR(
    `${getApiBaseUrl()}/api/system/metrics`,
    fetcher,
    { refreshInterval: 10000 }
  );
}

export function useCityHistorical(
  cityName: string,
  startDate: string,
  endDate: string,
  pollutants: string[] = ['pm25', 'pm10', 'no2', 'o3'],
) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    pollutants: pollutants.join(','),
  });
  return useSWR<HistoricalData | null>(
    `${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}/historical?${params}`,
    fetcher,
    { revalidateOnFocus: false }
  );
}

export default request;
