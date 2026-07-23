'use client';

import React, { createContext, useContext, useState, useMemo } from 'react';

interface CityContextType {
  selectedCity: string;
  setSelectedCity: (city: string) => void;
}

const CityContext = createContext<CityContextType>({
  selectedCity: 'Lusaka',
  setSelectedCity: () => {},
});

export function useCity() {
  return useContext(CityContext);
}

export function CityProvider({ children }: { children: React.ReactNode }) {
  const [selectedCity, setSelectedCity] = useState('Lusaka');
  const value = useMemo(() => ({ selectedCity, setSelectedCity }), [selectedCity]);

  return (
    <CityContext.Provider value={value}>
      {children}
    </CityContext.Provider>
  );
}
