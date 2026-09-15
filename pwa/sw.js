/* AirQ Zambia — Streamlit-aware service worker (v2).
 *
 * Streamlit apps are WebSocket-driven, so the HTML shell is never cached:
 *  - Document navigations -> network-first, branded /offline.html when offline.
 *  - Versioned /static/* bundles, icons and the manifest -> cache-first with a
 *    background refresh (stale-while-revalidate) for instant repeat launches.
 *  - API, /_stcore/* and WebSocket traffic -> left to the network untouched.
 */

const VERSION = "airq-zambia-v2";
const ASSET_CACHE = VERSION + "-assets";
const OFFLINE_PAGE = "/offline.html";

const STATIC_PRECACHE = [
  "/manifest.json",
  "/offline.html",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/maskable-512.png",
  "/icons/apple-touch-icon-180.png",
];

const STATIC_ASSET = /^\/static\/.+$/;

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches
      .open(ASSET_CACHE)
      .then(function (cache) {
        return cache.addAll(STATIC_PRECACHE);
      })
      .then(function () {
        return self.skipWaiting();
      })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    (async function () {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(function (key) {
            return !key.startsWith(VERSION);
          })
          .map(function (key) {
            return caches.delete(key);
          })
      );
      await self.clients.claim();
    })()
  );
});

async function staleWhileRevalidate(request) {
  const cache = await caches.open(ASSET_CACHE);
  const cached = await cache.match(request);
  const fromNetwork = fetch(request)
    .then(function (response) {
      if (response && response.ok) {
        const copy = response.clone();
        cache.put(request, copy).catch(function () {});
      }
      return response;
    })
    .catch(function () {
      return cached;
    });
  return cached || fromNetwork;
}

self.addEventListener("fetch", function (event) {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== location.origin) return;
  if (request.mode === "websocket") return;

  // Streamlit realtime + health traffic must never be cached or intercepted.
  if (url.pathname.indexOf("/_stcore/") === 0) return;

  // Document navigations: never serve a stale shell; degrade to /offline.html.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(function () {
        return caches.match(OFFLINE_PAGE);
      })
    );
    return;
  }

  // Versioned static bundles, icons and the manifest: stale-while-revalidate.
  if (
    STATIC_ASSET.test(url.pathname) ||
    url.pathname === "/manifest.json" ||
    url.pathname.indexOf("/icons/") === 0
  ) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Everything else (API, misc) -> network only.
});

self.addEventListener("message", function (event) {
  if (event.data === "SKIP_WAITING") {
    self.skipWaiting();
  }
});