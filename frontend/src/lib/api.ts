import useSWR from 'swr';
import type { CityAirQuality, ConfusionMatrixData, CrossValidationResult, EvaluationMetrics, ForecastData, ModelComparison, PredictionInput, PredictionResult } from '@/types';

/** Returns the FastAPI backend base URL, preferring the env var, then window origin, then localhost. */
function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:8000';
}

/** Generic typed fetch wrapper that prepends the API base URL and sets JSON headers. */
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
/** Checks FastAPI /status endpoint with retries. Returns the status payload or null on failure. */
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

// ==================== Live Weather (direct from Open-Meteo) ====================
const CITY_COORDS: Record<string, { latitude: number; longitude: number }> = {
  Lusaka: { latitude: -15.3875, longitude: 28.3228 },
  Ndola: { latitude: -12.8, longitude: 28.2167 },
  Kitwe: { latitude: -10.8833, longitude: 27.7833 },
};

/** Fetches current weather (temp, humidity, wind) from Open-Meteo for the given Zambian city. */
export async function fetchLiveWeather(cityName: string): Promise<{ temperature: number; humidity: number; wind_speed: number } | null> {
  const coords = CITY_COORDS[cityName];
  if (!coords) return null;
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${coords.latitude}&longitude=${coords.longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Africa%2FLusaka`;
    const response = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!response.ok) return null;
    const data = await response.json();
    const cur = data?.current;
    if (!cur) return null;
    return {
      temperature: cur.temperature_2m ?? 0,
      humidity: cur.relative_humidity_2m ?? 0,
      wind_speed: cur.wind_speed_10m ?? 0,
    };
  } catch {
    return null;
  }
}

/** Fetches hourly weather forecasts from Open-Meteo keyed by ISO timestamp string. */
export async function fetchLiveWeatherHourly(cityName: string, forecastDays: number = 3): Promise<Record<string, { temperature: number; humidity: number; wind_speed: number }> | null> {
  const coords = CITY_COORDS[cityName];
  if (!coords) return null;
  try {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${coords.latitude}&longitude=${coords.longitude}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=Africa%2FLusaka&forecast_days=${forecastDays}`;
    const response = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (!response.ok) return null;
    const data = await response.json();
    const h = data?.hourly;
    if (!h?.time) return null;
    const map: Record<string, { temperature: number; humidity: number; wind_speed: number }> = {};
    for (let i = 0; i < h.time.length; i++) {
      map[h.time[i]] = {
        temperature: h.temperature_2m[i] ?? 0,
        humidity: h.relative_humidity_2m[i] ?? 0,
        wind_speed: h.wind_speed_10m[i] ?? 0,
      };
    }
    return map;
  } catch {
    return null;
  }
}

// ==================== City Air Quality ====================
/** Fetches the current air quality reading (pollutants, health advice, category) for a city. */
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
/** Fetches hourly and daily AQI forecasts for a city. */
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
/** Submits pollutant/weather readings to the SVM model and returns a classification result. */
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
/** Fetches overall model evaluation metrics (accuracy, precision, recall, f1). */
export async function fetchEvaluationMetrics(): Promise<EvaluationMetrics> {
  try {
    return await request<EvaluationMetrics>('/api/evaluation/metrics');
  } catch (error) {
    console.error('Error fetching evaluation metrics:', error);
    return {};
  }
}

/** Fetches a side-by-side comparison of baseline vs. optimized model metrics. */
export async function fetchModelComparison(): Promise<ModelComparison | null> {
  try {
    const data = await request<{ status: string; comparison: ModelComparison }>('/api/evaluation/comparison');
    return data?.comparison ?? null;
  } catch (error) {
    console.error('Error fetching model comparison:', error);
    return null;
  }
}

/** Fetches confusion matrices for both the baseline and optimized models. */
export async function fetchConfusionMatrix(): Promise<ConfusionMatrixData | null> {
  try {
    return await request<ConfusionMatrixData>('/api/evaluation/confusion-matrix');
  } catch (error) {
    console.error('Error fetching confusion matrix:', error);
    return null;
  }
}

/** Triggers server-side k-fold cross-validation and polls until completion (up to 10 min). */
export async function runCrossValidation(
  folds: number = 5,
  modelType: string = 'optimized',
): Promise<CrossValidationResult> {
  const url = `/api/evaluation/cross-validate?folds=${folds}&model_type=${modelType}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(30_000),
  });

  if (!response.ok) {
    let detail = '';
    try { detail = (await response.json())?.detail ?? ''; } catch { /* ignore */ }
    throw new Error(detail || `Server responded with status ${response.status}`);
  }

  const started = (await response.json()) as { status: string; job_id?: string };
  if (started.status === 'completed' && started.job_id) {
    return started as unknown as CrossValidationResult;
  }
  if (!started.job_id) {
    throw new Error('Cross-validation could not be started on the backend.');
  }

  const jobId = started.job_id;
  const statusUrl = `/api/evaluation/cross-validate/status/${jobId}`;
  const deadline = Date.now() + 10 * 60 * 1000;

  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, 3000));
    const pollRes = await fetch(statusUrl, { signal: AbortSignal.timeout(30_000) });
    if (!pollRes.ok) {
      let detail = '';
      try { detail = (await pollRes.json())?.detail ?? ''; } catch { /* ignore */ }
      throw new Error(detail || `Server responded with status ${pollRes.status}`);
    }
    const status = (await pollRes.json()) as Record<string, unknown>;
    if (status.status === 'completed') {
      return status as unknown as CrossValidationResult;
    }
    if (status.status === 'error') {
      throw new Error(String(status.error || 'Cross-validation failed on the backend.'));
    }
  }

  throw new Error('Cross-validation timed out after 10 minutes.');
}

/** SWR hook that keeps the model comparison data fresh without revalidating on focus. */
export function useModelComparison() {
  return useSWR<ModelComparison | null>(
    `${getApiBaseUrl()}/api/evaluation/comparison`,
    (url: string) =>
      fetch(url)
        .then((r) => r.json())
        .then((d) => d?.comparison ?? null),
    { revalidateOnFocus: false }
  );
}

// ==================== SHAP Explainability ====================
/** Fetches global SHAP feature importance summary (falls back to a friendly message). */
export async function fetchShapSummary() {
  try {
    return await request('/api/explainability/shap-summary');
  } catch (error) {
    console.error('Error fetching SHAP summary:', error);
    return 'SHAP explainability details are currently unavailable.';
  }
}

/** Fetches per-class SHAP feature importances. */
export async function fetchShapPerClass() {
  try {
    return await request('/api/explainability/shap-per-class');
  } catch (error) {
    console.error('Error fetching per-class SHAP importance:', error);
    return null;
  }
}

/** Fetches a SHAP force plot for a single prediction instance by index. */
export async function fetchShapForce(instanceIndex: number) {
  try {
    return await request(`/api/explainability/force/${instanceIndex}`);
  } catch (error) {
    console.error('Error fetching SHAP force plot:', error);
    return null;
  }
}

// ==================== Live Prediction ====================
/** Gets the model's live prediction for a city using its current Open-Meteo readings. */
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
/** Submits a CSV string for batch prediction and returns the model's results. */
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
/** Fetches backend system metrics (CPU, memory, uptime). */
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

/** Fetches per-day historical pollutant measurements for a city over a date range. */
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

/** SWR hook polling current air quality for a city every 60s. */
export function useCityAirQuality(cityName: string) {
  return useSWR<CityAirQuality | null>(
    `${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}`,
    fetcher,
    { refreshInterval: 60000, revalidateOnFocus: true }
  );
}

/** SWR hook polling the AQI forecast for a city every 2 minutes. */
export function useCityForecast(cityName: string, forecastDays: number = 3) {
  return useSWR<ForecastData | null>(
    `${getApiBaseUrl()}/public/city/${encodeURIComponent(cityName)}/forecast?forecast_days=${forecastDays}`,
    fetcher,
    { refreshInterval: 120000 }
  );
}

/** SWR hook for model evaluation metrics. */
export function useEvaluationMetrics() {
  return useSWR<EvaluationMetrics>(
    `${getApiBaseUrl()}/api/evaluation/metrics`,
    fetcher,
    { revalidateOnFocus: false }
  );
}

/** SWR hook for the SHAP explainability summary. */
export function useShapSummary() {
  return useSWR(
    `${getApiBaseUrl()}/api/explainability/shap-summary`,
    fetcher,
    { revalidateOnFocus: false }
  );
}

/** SWR hook polling backend system metrics every 10s. */
export function useSystemMetrics() {
  return useSWR(
    `${getApiBaseUrl()}/api/system/metrics`,
    fetcher,
    { refreshInterval: 10000 }
  );
}

/** SWR hook for historical pollutant data over a date range. */
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
