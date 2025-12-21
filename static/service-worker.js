/* BeeSmart Spelling App - Simple Service Worker for PWA baseline */
// Bump this to force clients to refresh cached assets after important fixes
const CACHE_VERSION = 'beesmart-v1.4.2-2025-12-18-auth-logout-sw-bypass';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

// Minimal core assets to cache; extend as needed
const CORE_ASSETS = [
  '/',
  '/static/BeeSmartCrestLogo1.png',
  '/static/css/BeeSmart.css',
  '/static/css/ui-fixes.css',
  '/static/css/mobile-fonts.css',
  '/static/js/mascot-3d.js',
  '/static/js/user-avatar-loader.js',
  '/static/android-chrome-192x192.png',
  '/static/android-chrome-512x512.png',
  '/static/apple-touch-icon.png',
  '/static/favicon-32x32.png',
  '/static/favicon-16x16.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(CORE_ASSETS)).catch(() => Promise.resolve())
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== STATIC_CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // ✅ Auth endpoints often use redirects (e.g., /auth/logout -> /auth/login or /).
  // Some requests may have redirect mode != 'follow', which can produce:
  // "a redirected response was used for a request whose redirect mode is not 'follow'".
  // Let the browser handle these directly (no caching, no SW interception).
  if (url.pathname.startsWith('/auth/')) {
    return;
  }

  // Cache GLB files with network-first strategy (they're large but static)
  if (url.pathname.endsWith('.glb')) {
    event.respondWith(
      fetch(request).then((response) => {
        const copy = response.clone();
        caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy)).catch(() => {});
        return response;
      }).catch(() => caches.match(request))
    );
    return;
  }

  // Skip service worker ONLY for avatar-related assets (let the browser fetch directly).
  // NOTE: Do NOT exclude all PNGs; we want the SW to be able to cache app icons + brand logos.
  if (
    url.pathname.includes('/static/assets/avatars/') ||
    url.pathname.includes('/AvatarThumbnails/')
  ) {
    return;
  }

  // Network-first for navigation requests to keep content fresh
  if (request.mode === 'navigate') {
    event.respondWith(
      // Force a network refresh for HTML navigations; fall back to cached home when offline.
      fetch(new Request(request.url, { credentials: 'same-origin', cache: 'reload' }))
        .catch(() => caches.match('/'))
    );
    return;
  }

  // Cache-first for static assets under /static/ (excluding avatars)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const fetchAndCache = fetch(request).then((response) => {
          const copy = response.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy)).catch(() => {});
          return response;
        }).catch(() => cached);
        return cached || fetchAndCache;
      })
    );
    return;
  }

  // Default: network-first for all other requests (API calls, etc.)
  event.respondWith(
    fetch(request).catch((err) => {
      // Suppress warnings for expected API failures (battles, stats when offline)
      const isExpectedFailure = url.pathname.includes('/api/battles/') || 
                                url.pathname.includes('/api/users/stats');
      if (!isExpectedFailure) {
        console.warn('[SW] Network fetch failed for:', url.pathname, err);
      }
      return caches.match(request).then(cached => cached || new Response('Offline', { status: 503 }));
    })
  );
});
