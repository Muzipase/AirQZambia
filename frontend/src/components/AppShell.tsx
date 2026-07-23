'use client';

import React from 'react';
import Navigation from '@/components/Navigation';
import { useCity } from '@/lib/city-context';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { selectedCity, setSelectedCity } = useCity();

  return (
    <Navigation selectedCity={selectedCity} onCitySelect={setSelectedCity}>
      {children}
    </Navigation>
  );
}
