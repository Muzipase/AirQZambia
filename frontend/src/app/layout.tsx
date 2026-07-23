import React from 'react';
import { Inter } from 'next/font/google';
import { CityProvider } from '@/lib/city-context';
import AppShell from '@/components/AppShell';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'AirQ Zambia - Air Quality Monitor',
  description: 'Real-time air quality monitoring for Lusaka, Ndola, and Kitwe',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CityProvider>
          <AppShell>{children}</AppShell>
        </CityProvider>
      </body>
    </html>
  );
}
