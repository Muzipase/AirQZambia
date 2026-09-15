/**
 * US-EPA 2016 multi-pollutant Air Quality Index conversion.
 *
 * Computes a per-pollutant sub-index for each of the six criteria pollutants
 * (PM2.5, PM10, NO2, SO2, CO, O3) and returns the maximum — the US-EPA
 * multi-pollutant AQI. This mirrors the Streamlit command center
 * (`app/state.py` `compute_aqi`) and the FastAPI backend so every surface
 * reports the same index for the same concentrations.
 */

export type PollutantKey = 'pm25' | 'pm10' | 'no2' | 'so2' | 'co' | 'o3';

/** A single (c_low, c_high, i_low, i_high) US-EPA breakpoint band. */
type Breakpoint = [number, number, number, number];

/**
 * Piecewise-linear US-EPA AQI sub-index for a concentration.
 *
 * Returns null when the value is missing / non-finite, 500 when it exceeds
 * all defined bands.
 */
function aqiFromBreakpoints(value: number | null | undefined, breakpoints: Breakpoint[]): number | null {
  if (value == null || !Number.isFinite(value)) return null;
  for (const [cLow, cHigh, iLow, iHigh] of breakpoints) {
    if (value <= cHigh) {
      return Math.round(iLow + ((value - cLow) / (cHigh - cLow)) * (iHigh - iLow));
    }
  }
  return 500;
}

// PM2.5 / PM10 / NO2 / SO2 / O3 are graded directly in µg/m³ (Open-Meteo's
// unit). CO is graded in mg/m³ so µg/m³ values are divided by 1000 first.

const PM25_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 12.0, 0, 50],
  [12.0, 35.4, 50, 100],
  [35.4, 55.4, 100, 150],
  [55.4, 150.4, 150, 200],
  [150.4, 250.4, 200, 300],
  [250.4, 500.4, 300, 500],
];

const PM10_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 54.0, 0, 50],
  [54.0, 154.0, 50, 100],
  [154.0, 254.0, 100, 150],
  [254.0, 354.0, 150, 200],
  [354.0, 424.0, 200, 300],
  [424.0, 504.0, 300, 400],
  [504.0, 604.0, 400, 500],
];

const NO2_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 53.0, 0, 50],
  [53.0, 100.0, 50, 100],
  [100.0, 360.0, 100, 150],
  [360.0, 649.0, 150, 200],
  [649.0, 1249.0, 200, 300],
  [1249.0, 1649.0, 300, 400],
  [1649.0, 2049.0, 400, 500],
];

const SO2_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 35.0, 0, 50],
  [35.0, 75.0, 50, 100],
  [75.0, 185.0, 100, 150],
  [185.0, 304.0, 150, 200],
  [304.0, 604.0, 200, 300],
  [604.0, 804.0, 300, 400],
  [804.0, 1004.0, 400, 500],
];

const CO_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 4.4, 0, 50],
  [4.4, 9.4, 50, 100],
  [9.4, 12.4, 100, 150],
  [12.4, 15.4, 150, 200],
  [15.4, 30.4, 200, 300],
  [30.4, 40.4, 300, 400],
  [40.4, 50.4, 400, 500],
];

const O3_AQI_BREAKPOINTS: Breakpoint[] = [
  [0.0, 108.0, 0, 50],
  [108.0, 140.0, 50, 100],
  [140.0, 170.0, 100, 150],
  [170.0, 210.0, 150, 200],
  [210.0, 400.0, 200, 300],
  [400.0, 600.0, 300, 400],
  [600.0, 800.0, 400, 500],
];

/** US-EPA AQI index from a PM2.5 concentration (µg/m³). */
export function pm25ToAqi(pm25: number | null | undefined): number | null {
  return aqiFromBreakpoints(pm25, PM25_AQI_BREAKPOINTS);
}

/** US-EPA AQI index from a PM10 concentration (µg/m³). */
export function pm10ToAqi(pm10: number | null | undefined): number | null {
  return aqiFromBreakpoints(pm10, PM10_AQI_BREAKPOINTS);
}

/** US-EPA AQI index from an NO2 concentration (µg/m³). */
export function no2ToAqi(no2: number | null | undefined): number | null {
  return aqiFromBreakpoints(no2, NO2_AQI_BREAKPOINTS);
}

/** US-EPA AQI index from an SO2 concentration (µg/m³). */
export function so2ToAqi(so2: number | null | undefined): number | null {
  return aqiFromBreakpoints(so2, SO2_AQI_BREAKPOINTS);
}

/** US-EPA AQI index from a CO concentration (µg/m³, converted to mg/m³). */
export function coToAqi(co: number | null | undefined): number | null {
  if (co == null || !Number.isFinite(co)) return null;
  return aqiFromBreakpoints(co / 1000.0, CO_AQI_BREAKPOINTS);
}

/** US-EPA AQI index from an O3 concentration (µg/m³). */
export function o3ToAqi(o3: number | null | undefined): number | null {
  return aqiFromBreakpoints(o3, O3_AQI_BREAKPOINTS);
}

/** Per-pollutant sub-index functions, in display order. */
const AQI_FUNCTIONS: Record<PollutantKey, (value: number | null | undefined) => number | null> = {
  pm25: pm25ToAqi,
  pm10: pm10ToAqi,
  no2: no2ToAqi,
  so2: so2ToAqi,
  co: coToAqi,
  o3: o3ToAqi,
};

export interface AqiResult {
  /** Overall multi-pollutant AQI (max sub-index), or null when no readings. */
  aqi: number | null;
  /** Pollutant that drove the overall AQI, or null when no readings. */
  dominant: PollutantKey | null;
  /** Per-pollutant sub-indices for the readings that were present. */
  subIndices: Partial<Record<PollutantKey, number>>;
}

/**
 * US-EPA multi-pollutant AQI from per-pollutant concentrations.
 *
 * Missing / non-finite values are skipped; ties favour the earlier pollutant
 * in display order (e.g. PM2.5). Mirrors `app/state.py` `compute_aqi`.
 */
export function computeAqi(readings: Partial<Record<string, number>>): AqiResult {
  const subIndices: Partial<Record<PollutantKey, number>> = {};
  const order: PollutantKey[] = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'];
  for (const pollutant of order) {
    const value = readings[pollutant];
    if (value == null) continue;
    const sub = AQI_FUNCTIONS[pollutant](value);
    if (sub != null) subIndices[pollutant] = sub;
  }
  const present = order.filter((p) => subIndices[p] != null);
  if (present.length === 0) return { aqi: null, dominant: null, subIndices };
  const aqi = Math.max(...present.map((p) => subIndices[p] as number));
  const dominant = present.find((p) => subIndices[p] === aqi) ?? null;
  return { aqi, dominant, subIndices };
}

/** Category string for an AQI index value using the shared US-EPA bands. */
export function aqiCategory(aqi: number): string {
  if (aqi <= 50) return 'Good';
  if (aqi <= 100) return 'Moderate';
  if (aqi <= 150) return 'Unhealthy';
  if (aqi <= 200) return 'Very Unhealthy';
  return 'Hazardous';
}

/** Health message for an AQI index value, mirroring `app/state.py` classify_aqi. */
export function aqiHealthMessage(aqi: number): string {
  if (aqi <= 50) return 'Air quality is satisfactory and poses little or no risk.';
  if (aqi <= 100) return 'Acceptable air quality; sensitive groups should limit prolonged exposure.';
  if (aqi <= 150) return 'Unhealthy for sensitive groups — reduce prolonged outdoor exposure.';
  if (aqi <= 200) return 'Health alert — serious effects possible; limit outdoor activity.';
  return 'Health alert — serious effects likely; stay indoors where possible.';
}