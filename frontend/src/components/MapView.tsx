'use client';

import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface CityPoint {
  name: string;
  lat: number;
  lon: number;
  desc: string;
  data?: {
    aqi: number;
    category: string;
    pm25: number;
    temperature: number;
    humidity: number;
    wind_speed: number;
  };
}

interface MapViewProps {
  center: [number, number];
  cities: CityPoint[];
  loading: boolean;
}

function aqiColor(aqi: number): string {
  if (aqi <= 50) return '#22c55e';
  if (aqi <= 100) return '#eab308';
  if (aqi <= 150) return '#f97316';
  if (aqi <= 200) return '#ef4444';
  return '#7f1d1d';
}

function createPulsingIcon(color: string, size: number = 40) {
  return L.divIcon({
    className: 'map-pulse-marker',
    html: `
      <div class="pulse-ring" style="border-color: ${color}"></div>
      <div class="pulse-dot" style="background: ${color}"></div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2 + 4],
  });
}

function createCityIcon(aqi: number) {
  const color = aqiColor(aqi);
  return L.divIcon({
    className: 'map-city-marker',
    html: `
      <div class="city-marker-wrapper">
        <div class="city-marker-pulse" style="box-shadow: 0 0 12px ${color}40"></div>
        <div class="city-marker-dot" style="background: ${color}"></div>
        <div class="city-marker-label">${aqi}</div>
      </div>
    `,
    iconSize: [52, 52],
    iconAnchor: [26, 26],
    popupAnchor: [0, -30],
  });
}

export default function MapView({ center, cities, loading }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const heatLayerRef = useRef<L.Circle[]>([]);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    const map = L.map(mapRef.current, {
      center,
      zoom: 7,
      zoomControl: false,
      attributionControl: true,
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18,
    }).addTo(map);

    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapInstance.current;
    if (!map) return;

    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];
    heatLayerRef.current.forEach((c) => map.removeLayer(c));
    heatLayerRef.current = [];

    cities.forEach((city) => {
      if (!city.data) return;
      const { aqi, category, pm25, temperature, humidity, wind_speed } = city.data;
      const color = aqiColor(aqi);

      // AQI heatmap circle
      const radius = Math.max(aqi * 300, 8000);
      const heatCircle = L.circle([city.lat, city.lon], {
        radius,
        color: 'transparent',
        fillColor: color,
        fillOpacity: 0.12,
        interactive: false,
      }).addTo(map);
      heatLayerRef.current.push(heatCircle);

      // Pulsing outer ring
      const pulseMarker = L.marker([city.lat, city.lon], {
        icon: createPulsingIcon(color),
        interactive: false,
      }).addTo(map);
      markersRef.current.push(pulseMarker);

      // City marker with AQI badge
      const marker = L.marker([city.lat, city.lon], {
        icon: createCityIcon(aqi),
      }).addTo(map);

      marker.bindPopup(`
        <div class="map-popup">
          <div class="map-popup-header">
            <span class="map-popup-dot" style="background: ${color}"></span>
            <span class="map-popup-city">${city.name}</span>
            <span class="map-popup-desc">${city.desc}</span>
          </div>
          <div class="map-popup-aqi-row">
            <div class="map-popup-aqi" style="color: ${color}">${aqi}</div>
            <div class="map-popup-category">${category}</div>
          </div>
          <div class="map-popup-grid">
            <div class="map-popup-stat">
              <span class="map-popup-stat-label">PM2.5</span>
              <span class="map-popup-stat-value">${pm25} µg/m³</span>
            </div>
            <div class="map-popup-stat">
              <span class="map-popup-stat-label">Temp</span>
              <span class="map-popup-stat-value">${temperature}°C</span>
            </div>
            <div class="map-popup-stat">
              <span class="map-popup-stat-label">Humidity</span>
              <span class="map-popup-stat-value">${humidity}%</span>
            </div>
            <div class="map-popup-stat">
              <span class="map-popup-stat-label">Wind</span>
              <span class="map-popup-stat-value">${wind_speed} km/h</span>
            </div>
          </div>
        </div>
      `, {
        className: 'map-popup-wrapper',
        maxWidth: 260,
        closeButton: true,
      });

      markersRef.current.push(marker);
    });
  }, [cities]);

  return (
    <>
      {loading && (
        <div className="map-loading">
          <div className="map-loading-spinner" />
          <span>Loading pollution data...</span>
        </div>
      )}
      <div ref={mapRef} className="map-leaflet-container" />
    </>
  );
}
