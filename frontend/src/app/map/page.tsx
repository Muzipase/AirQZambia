'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { fetchCityAirQuality, fetchLiveWeather } from '@/lib/api';

const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

const CITIES = [
  { name: 'Lusaka', lat: -15.3875, lon: 28.3228, desc: 'Capital' },
  { name: 'Ndola', lat: -12.9689, lon: 28.6392, desc: 'Copperbelt' },
  { name: 'Kitwe', lat: -12.8024, lon: 28.2132, desc: 'Copperbelt' },
];

function aqiColor(aqi: number): string {
  if (aqi <= 50) return '#22c55e';
  if (aqi <= 100) return '#eab308';
  if (aqi <= 150) return '#f97316';
  if (aqi <= 200) return '#ef4444';
  return '#7f1d1d';
}

function aqiCategory(aqi: number): string {
  if (aqi <= 50) return 'Good';
  if (aqi <= 100) return 'Moderate';
  if (aqi <= 150) return 'Unhealthy for Sensitive';
  if (aqi <= 200) return 'Unhealthy';
  return 'Hazardous';
}

function pm25ToAqi(pm25: number): number {
  if (pm25 <= 12) return Math.round((pm25 / 12) * 50);
  if (pm25 <= 35.4) return Math.round(50 + ((pm25 - 12) / 23.4) * 50);
  if (pm25 <= 55.4) return Math.round(100 + ((pm25 - 35.4) / 20) * 50);
  return Math.round(150 + ((pm25 - 55.4) / 95) * 100);
}

export default function PollutionMapPage() {
  const [cityData, setCityData] = useState<Record<string, { aqi: number; category: string; pm25: number; temperature: number; humidity: number; wind_speed: number }>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAllCities() {
      const results: Record<string, { aqi: number; category: string; pm25: number; temperature: number; humidity: number; wind_speed: number }> = {};
      await Promise.all(
        CITIES.map(async (city) => {
          const data = await fetchCityAirQuality(city.name);
          if (data && data.status === 'ok') {
            const pm25 = data.readings?.pm25 ?? 0;
            results[city.name] = {
              aqi: pm25ToAqi(pm25),
              category: data.category || 'Moderate',
              pm25,
              temperature: data.readings?.temperature ?? 0,
              humidity: data.readings?.humidity ?? 0,
              wind_speed: data.readings?.wind_speed ?? 0,
            };
            if (results[city.name].temperature === 0) {
              const wx = await fetchLiveWeather(city.name);
              if (wx) {
                results[city.name].temperature = wx.temperature;
                results[city.name].humidity = wx.humidity;
                results[city.name].wind_speed = wx.wind_speed;
              }
            }
          }
        })
      );
      setCityData(results);
      setLoading(false);
    }
    loadAllCities();
    const interval = setInterval(loadAllCities, 60000);
    return () => clearInterval(interval);
  }, []);

  const citiesWithCoords = useMemo(() =>
    CITIES.map((c) => ({ ...c, data: cityData[c.name] })),
    [cityData]
  );

  const mapCenter: [number, number] = useMemo(() => {
    const lats = CITIES.map((c) => c.lat);
    const lons = CITIES.map((c) => c.lon);
    return [(Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lons) + Math.max(...lons)) / 2];
  }, []);

  return (
    <div className="map-page">
      <div className="map-breadcrumb">
        <Link href="/" className="map-breadcrumb-link">World</Link>
        <span className="map-breadcrumb-sep">/</span>
        <span className="map-breadcrumb-current">Zambia Pollution Map</span>
      </div>

      <div className="map-header">
        <h1 className="map-title">Pollution Map</h1>
        <p className="map-subtitle">Real-time air quality visualization across Zambia</p>
      </div>

      <div className="map-container">
        <MapView center={mapCenter} cities={citiesWithCoords} loading={loading} />
      </div>

      <div className="map-legend">
        <div className="map-legend-title">Air Quality Index (AQI)</div>
        <div className="map-legend-items">
          <div className="map-legend-item"><span className="map-legend-dot" style={{ background: '#22c55e' }} /><span>Good (0-50)</span></div>
          <div className="map-legend-item"><span className="map-legend-dot" style={{ background: '#eab308' }} /><span>Moderate (51-100)</span></div>
          <div className="map-legend-item"><span className="map-legend-dot" style={{ background: '#f97316' }} /><span>Unhealthy for Sensitive (101-150)</span></div>
          <div className="map-legend-item"><span className="map-legend-dot" style={{ background: '#ef4444' }} /><span>Unhealthy (151-200)</span></div>
          <div className="map-legend-item"><span className="map-legend-dot" style={{ background: '#7f1d1d' }} /><span>Hazardous (201+)</span></div>
        </div>
      </div>

      <div className="map-cards">
        {citiesWithCoords.map((city) => {
          const aqi = city.data?.aqi ?? 0;
          return (
            <Link href="/dashboard" key={city.name} className="map-city-card">
              <div className="map-city-card-dot" style={{ background: aqiColor(aqi) }} />
              <div className="map-city-card-info">
                <span className="map-city-card-name">{city.name}</span>
                <span className="map-city-card-desc">{city.desc}</span>
              </div>
              <div className="map-city-card-aqi" style={{ color: aqiColor(aqi) }}>
                {aqi || '...'}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
