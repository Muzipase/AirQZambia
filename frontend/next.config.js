const withSerwist = require('@serwist/next').default({
    swSrc: 'src/app/sw.ts',
    swDest: 'public/sw.js',
});

// Proxy API + public data requests to the FastAPI backend so the browser only
// ever talks to the frontend origin. Override for deployments with
// NEXT_PUBLIC_API_BASE_URL (e.g. the Render backend URL).
const BACKEND_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    poweredByHeader: false,
    experimental: {
        optimizePackageImports: ['leaflet'],
    },
    async rewrites() {
        return [
            { source: '/api/:path*', destination: `${BACKEND_BASE}/api/:path*` },
            { source: '/public/:path*', destination: `${BACKEND_BASE}/public/:path*` },
        ];
    },
};

module.exports = withSerwist(nextConfig);
