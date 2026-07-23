// ==================== API Response Types ====================

export interface ApiStatus {
  status: string;
  models?: Record<string, string>;
}

export interface CityAirQuality {
  status: string;
  city: string;
  category: string;
  health: {
    message: string;
    color: string;
    action: string;
  };
  readings: {
    pm25: number;
    pm10: number;
    no2: number;
    so2: number;
    co: number;
    o3: number;
    temperature: number;
    humidity: number;
    wind_speed: number;
  };
  timestamp: string;
}

export interface PredictionInput {
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

export interface PredictionResult {
  prediction: string | number;
  confidence?: number;
  probability?: Record<string, number>;
}

export interface MetricCard {
  label: string;
  value: string | number;
  change?: string;
  status?: 'good' | 'moderate' | 'poor';
}

export interface EvaluationMetrics {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  confusion_matrix?: number[][];
  [key: string]: any;
}

export interface ShapData {
  summary: string;
  force_plot?: string;
  dependence?: Record<string, any>;
}

export interface SystemMetrics {
  cpu_usage?: number;
  memory_usage?: number;
  api_response_time: number;
  uptime: number;
  status?: string;
  timestamp?: string;
}

export interface AlertItem {
  id: string;
  level: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  value: string;
  action?: string;
}

export interface AlertHistoryItem extends AlertItem {
  dismissedAt: string;
}

export interface TrendDataPoint {
  timestamp: string;
  pm25: number;
  pm10: number;
  o3: number;
  [key: string]: any;
}

// ==================== Forecast Types ====================

export interface HourlyForecast {
  timestamp: string;
  aqi: number;
  pm25: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  category: string;
}

export interface DailyForecast {
  date: string;
  aqi_max: number;
  aqi_min: number;
  temp_max: number;
  temp_min: number;
  wind_max: number;
  humidity_avg: number;
  category: string;
}

export interface ForecastData {
  status: string;
  city: string;
  hourly: HourlyForecast[];
  daily: DailyForecast[];
  who_guideline: {
    pm25_annual: number;
    pm25_24h: number;
  };
}
