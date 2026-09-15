/**
 * US-EPA Air Quality Index conversion from PM2.5 concentration.
 *
 * Keeps every page (landing, dashboard, map) on the same formula, which
 * mirrors the Python backend (api.py `_pm25_to_aqi`) and the Streamlit
 * command center so all surfaces report the same index.
 */

/** Converts a PM2.5 concentration (µg/m³) into the US-EPA AQI scale (0–500). */
export function pm25ToAqi(pm25: number): number {
  if (pm25 <= 12.0) return Math.round((pm25 / 12.0) * 50);
  if (pm25 <= 35.4) return Math.round(50 + ((pm25 - 12.0) / (35.4 - 12.0)) * 50);
  if (pm25 <= 55.4) return Math.round(100 + ((pm25 - 35.4) / (55.4 - 35.4)) * 50);
  if (pm25 <= 150.4) return Math.round(150 + ((pm25 - 55.4) / (150.4 - 55.4)) * 50);
  if (pm25 <= 250.4) return Math.round(200 + ((pm25 - 150.4) / (250.4 - 150.4)) * 100);
  return Math.round(300 + ((pm25 - 250.4) / (500.4 - 250.4)) * 200);
}