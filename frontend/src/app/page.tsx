'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCity } from '@/lib/city-context';
import { fetchCityAirQuality } from '@/lib/api';
import type { CityAirQuality } from '@/types';

const cities = [
  { name: 'Lusaka', desc: 'Capital City', pop: '3.2 million' },
  { name: 'Ndola', desc: 'Copperbelt Province', pop: '455,000' },
  { name: 'Kitwe', desc: 'Copperbelt Province', pop: '517,000' },
];

const steps = [
  {
    num: '1',
    title: 'Select your city',
    desc: 'Choose Lusaka, Ndola, or Kitwe from the sidebar.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
        <circle cx="12" cy="10" r="3" />
      </svg>
    ),
  },
  {
    num: '2',
    title: 'Check the air quality',
    desc: 'See the current air quality level, what it means, and what you should do.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </svg>
    ),
  },
  {
    num: '3',
    title: 'Stay safe',
    desc: 'Follow simple health advice to protect yourself and your family.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
  },
];

const aqiLevels = [
  { range: '0 - 50', label: 'Good', color: 'var(--aqi-good)', desc: 'Safe for everyone' },
  { range: '51 - 100', label: 'Moderate', color: 'var(--aqi-moderate)', desc: 'Sensitive people be careful' },
  { range: '101 - 150', label: 'Unhealthy', color: 'var(--aqi-unhealthy)', desc: 'Limit time outdoors' },
  { range: '151 - 200', label: 'Very Unhealthy', color: 'var(--aqi-very-unhealthy)', desc: 'Stay indoors' },
  { range: '201+', label: 'Hazardous', color: 'var(--aqi-hazardous)', desc: 'Emergency — seek medical help' },
];

export default function LandingPage() {
  const { selectedCity, setSelectedCity } = useCity();
  const router = useRouter();
  const [liveData, setLiveData] = useState<CityAirQuality | null>(null);

  const getAQIValue = (pm25: number) => {
    if (pm25 <= 12.0) return Math.round((pm25 / 12.0) * 50);
    if (pm25 <= 35.4) return Math.round(50 + ((pm25 - 12.0) / (35.4 - 12.0)) * 50);
    if (pm25 <= 55.4) return Math.round(100 + ((pm25 - 35.4) / (55.4 - 35.4)) * 50);
    if (pm25 <= 150.4) return Math.round(150 + ((pm25 - 55.4) / (150.4 - 35.4)) * 100);
    return Math.round(200 + ((pm25 - 150.4) / (500 - 150.4)) * 300);
  };

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'Good': return 'var(--aqi-good)';
      case 'Moderate': return 'var(--aqi-moderate)';
      case 'Unhealthy': return 'var(--aqi-unhealthy)';
      case 'Very Unhealthy': return 'var(--aqi-very-unhealthy)';
      case 'Hazardous': return 'var(--aqi-hazardous)';
      default: return 'var(--aqi-moderate)';
    }
  };

  const loadLive = useCallback(async () => {
    const data = await fetchCityAirQuality(selectedCity);
    if (data && data.status === 'ok') setLiveData(data);
  }, [selectedCity]);

  useEffect(() => {
    loadLive();
    const interval = setInterval(loadLive, 120000);
    return () => clearInterval(interval);
  }, [loadLive]);

  const aqiValue = liveData ? getAQIValue(liveData.readings.pm25) : null;
  const category = liveData?.category ?? null;
  const healthMsg = liveData?.health?.message ?? null;
  const catColor = category ? getCategoryColor(category) : 'var(--aqi-good)';

  return (
    <div className="landing">
      {/* Hero */}
      <section className="landing-hero">
        <div className="landing-hero-inner">
          <div className="landing-hero-badge">Zambia&apos;s Air Quality Monitor</div>
          <h1 className="landing-hero-title">
            Breathe Easy.<br />
            <span className="landing-hero-highlight">Know Your Air.</span>
          </h1>
          <p className="landing-hero-desc">
            Check the air quality in your city and get simple health advice to keep you and your family safe.
            Free, real-time, and built for every Zambian.
          </p>
          <div className="landing-hero-actions">
            <Link href="/dashboard" className="landing-btn landing-btn-primary">
              Check Air Quality Now
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </Link>
            <button
              className="landing-btn landing-btn-secondary"
              onClick={() => setSelectedCity('Lusaka')}
            >
              I&apos;m in Lusaka
            </button>
          </div>
          <div className="landing-hero-cities">
            {cities.map((c) => (
              <span key={c.name} className="landing-hero-city-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                {c.name}
              </span>
            ))}
          </div>
        </div>
        <div className="landing-hero-visual">
          <div className="landing-aqi-preview">
            <div className="landing-aqi-preview-ring">
              <span className="landing-aqi-preview-value">{aqiValue ?? '—'}</span>
              <span className="landing-aqi-preview-label">AQI</span>
            </div>
            <div className="landing-aqi-preview-info">
              {category && (
                <span className="landing-aqi-preview-badge" style={{ background: catColor }}>{category}</span>
              )}
              <span className="landing-aqi-preview-msg">{healthMsg ?? 'Loading live air quality data...'}</span>
              {liveData && (
                <span className="landing-aqi-preview-source" style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
                  {selectedCity} — PM2.5: {liveData.readings.pm25} µg/m³
                </span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="landing-section">
        <h2 className="landing-section-title">How it works</h2>
        <p className="landing-section-subtitle">Three simple steps to check your air</p>
        <div className="landing-steps">
          {steps.map((step) => (
            <div key={step.num} className="landing-step">
              <div className="landing-step-icon">{step.icon}</div>
              <div className="landing-step-num">{step.num}</div>
              <h3 className="landing-step-title">{step.title}</h3>
              <p className="landing-step-desc">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Cities */}
      <section className="landing-section landing-section-cities">
        <h2 className="landing-section-title">Cities we cover</h2>
        <p className="landing-section-subtitle">Real-time air quality data for Zambia&apos;s urban centres</p>
        <div className="landing-cities-grid">
          {cities.map((city) => (
            <button
              key={city.name}
              className="landing-city-card"
              onClick={() => {
                setSelectedCity(city.name);
                router.push('/dashboard');
              }}
            >
              <div className="landing-city-card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <h3 className="landing-city-card-name">{city.name}</h3>
              <p className="landing-city-card-desc">{city.desc}</p>
              <p className="landing-city-card-pop">Population: {city.pop}</p>
            </button>
          ))}
        </div>
      </section>

      {/* AQI Scale */}
      <section className="landing-section">
        <h2 className="landing-section-title">Understanding Air Quality</h2>
        <p className="landing-section-subtitle">What the numbers mean for your health</p>
        <div className="landing-aqi-scale">
          {aqiLevels.map((level) => (
            <div key={level.label} className="landing-aqi-level">
              <div className="landing-aqi-level-bar" style={{ background: level.color }} />
              <div className="landing-aqi-level-info">
                <div className="landing-aqi-level-header">
                  <span className="landing-aqi-level-range">{level.range}</span>
                  <span className="landing-aqi-level-label" style={{ color: level.color }}>{level.label}</span>
                </div>
                <span className="landing-aqi-level-desc">{level.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Why it matters */}
      <section className="landing-section landing-why">
        <h2 className="landing-section-title">Why air quality matters</h2>
        <div className="landing-why-grid">
          <div className="landing-why-card">
            <div className="landing-why-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <h3>Protect your lungs</h3>
            <p>Poor air quality can cause breathing problems, especially for children and the elderly. Knowing the air quality helps you make safer choices.</p>
          </div>
          <div className="landing-why-card">
            <div className="landing-why-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" />
                <path d="M16 3.13a4 4 0 010 7.75" />
              </svg>
            </div>
            <h3>Keep your family safe</h3>
            <p>Get alerts when air quality is bad so you can keep children indoors, close windows, and take other simple steps to stay healthy.</p>
          </div>
          <div className="landing-why-card">
            <div className="landing-why-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--zambia-green)" strokeWidth="2" strokeLinecap="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
            </div>
            <h3>Plan your day</h3>
            <p>Check the air before you go outside. If it&apos;s bad, plan indoor activities. If it&apos;s good, enjoy the outdoors!</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="landing-cta">
        <h2>Ready to check your air?</h2>
        <p>Select your city and see the current air quality right now.</p>
        <Link href="/dashboard" className="landing-btn landing-btn-primary landing-btn-lg">
          Go to Air Quality Dashboard
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </Link>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="flag-accent" />
        <p>AirQ Zambia &mdash; Keeping communities informed about air quality</p>
        <p className="landing-footer-sub">Data sourced from Open-Meteo & OpenAQ &middot; Powered by Bayesian-Optimized SVM</p>
      </footer>
    </div>
  );
}
