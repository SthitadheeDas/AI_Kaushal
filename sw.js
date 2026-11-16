/* ============================================================
   SamaadSetu - Service Worker (sw.js)
   Offline-First PWA Cache & Background Sync Worker for 2G/3G Rural Connectivity
   ============================================================ */

const CACHE_NAME = 'samaadsetu-v1.3';
const STATIC_ASSETS = [
  './',
  './index.html',
  './officer.html',
  './manifest.json',
  'https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js'
];

// Install: Cache offline essentials
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching offline assets for 2G/3G resilience');
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Pre-cache partial warning:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate: Purge stale caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Stale-While-Revalidate with offline fallback
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        // Network failed (offline in rural area)
        return cachedResponse;
      });

      return cachedResponse || fetchPromise;
    })
  );
});

// Background Sync API: Re-transmit queued grievances when network returns
self.addEventListener('sync', (event) => {
  if (event.tag === 'samaadsetu-sync-outbox' || event.tag === 'jan-shakti-sync-outbox') {
    console.log('[SW] Background Sync triggered: Flushing offline grievance queue');
    event.waitUntil(
      self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          client.postMessage({ type: 'TRIGGER_OUTBOX_FLUSH' });
        });
      })
    );
  }
});
