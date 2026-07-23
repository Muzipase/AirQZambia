'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { fetchApiStatus } from '@/lib/api';

const navLinks = [
  { label: 'Home', href: '/', icon: 'home' },
  { label: 'Air Quality', href: '/dashboard', icon: 'air' },
  { label: 'Pollution Map', href: '/map', icon: 'globe' },
  { label: 'Historical Trends', href: '/historical', icon: 'chart' },
];

const cities = [
  { name: 'Lusaka', desc: 'Capital City' },
  { name: 'Ndola', desc: 'Copperbelt' },
  { name: 'Kitwe', desc: 'Copperbelt' },
];

interface NavigationProps {
  children: React.ReactNode;
  selectedCity: string;
  onCitySelect: (city: string) => void;
}

function SidebarIcon({ icon }: { icon: string }) {
  const p = { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  switch (icon) {
    case 'home':
      return <svg {...p}><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>;
    case 'air':
      return <svg {...p}><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>;
    case 'globe':
      return <svg {...p}><circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" /><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" /></svg>;
    case 'chart':
      return <svg {...p}><path d="M3 3v18h18" /><path d="M7 16l4-5 4 3 5-7" /></svg>;
    default:
      return <svg {...p}><circle cx="12" cy="12" r="10" /></svg>;
  }
}

export default React.memo(function Navigation({ children, selectedCity, onCitySelect }: NavigationProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    let mounted = true;
    const check = () => {
      fetchApiStatus().then((s) => {
        if (mounted) setApiOnline(!!s);
      }).catch(() => {
        if (mounted) setApiOnline(false);
      });
    };
    check();
    const interval = setInterval(check, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  // Close sidebar on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  // Lock body scroll when sidebar is open on mobile
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [sidebarOpen]);

  const handleCitySelect = useCallback((city: string) => {
    onCitySelect(city);
    setSidebarOpen(false);
    if (pathname !== '/dashboard') {
      router.push('/dashboard');
    }
  }, [onCitySelect, pathname, router]);

  return (
    <div className="app-layout">
      {/* Mobile top bar */}
      <div className="mobile-topbar">
        <button className="hamburger-btn" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle navigation">
          {sidebarOpen ? (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
          ) : (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M3 12h18M3 6h18M3 18h18" /></svg>
          )}
        </button>
        <Link href="/" className="mobile-topbar-brand">
          <div className="sidebar-logo-icon" style={{ width: 28, height: 28, borderRadius: 8 }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="mobile-topbar-text">AirQ<span>Zambia</span></span>
        </Link>
        <div className="mobile-topbar-city">{selectedCity}</div>
      </div>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <Link href="/" className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <div className="sidebar-brand-text">AirQ<span>Zambia</span></div>
              <div className="sidebar-brand-sub">Air Quality Monitor</div>
            </div>
          </Link>
          <button className="sidebar-close-btn" onClick={() => setSidebarOpen(false)} aria-label="Close navigation">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
          </button>
        </div>

        {/* Nav links */}
        <div className="sidebar-nav">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || (link.href !== '/' && pathname?.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`sidebar-nav-link ${isActive ? 'active' : ''}`}
              >
                <SidebarIcon icon={link.icon} />
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="sidebar-section-label">Select Your City</div>

        <div className="sidebar-cities">
          {cities.map((city) => (
            <button
              key={city.name}
              className={`sidebar-city-btn ${selectedCity === city.name ? 'active' : ''}`}
              onClick={() => handleCitySelect(city.name)}
            >
              <div className="sidebar-city-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <div className="sidebar-city-info">
                <span className="sidebar-city-name">{city.name}</span>
                <span className="sidebar-city-desc">{city.desc}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <div className={`sidebar-status-dot ${apiOnline === null ? '' : apiOnline ? 'online' : 'offline'}`} />
            <span className="sidebar-status-text">
              {apiOnline === null ? 'Connecting...' : apiOnline ? 'Data Online' : 'Offline'}
            </span>
          </div>
          <div className="sidebar-info">
            <p>Data from Open-Meteo & OpenAQ</p>
            <p>Powered by Bayesian-Optimized SVM</p>
          </div>
        </div>
      </aside>

      {/* Overlay — must come AFTER sidebar for CSS sibling selector */}
      <div className={`sidebar-overlay ${sidebarOpen ? 'overlay-visible' : ''}`} onClick={() => setSidebarOpen(false)} />

      {/* Main content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
})
