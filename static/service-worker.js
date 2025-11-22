/* BeeSmart Spelling App - Simple Service Worker for PWA baseline */
// Bump this to force clients to refresh cached assets after important fixes
const CACHE_VERSION = 'beesmart-v1.3.0-2025-11-21-quiz-syntax-fix';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

// Minimal core assets to cache; extend as needed
const CORE_ASSETS = [
  '/',
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

  // Skip service worker completely for avatar assets - always fetch fresh
  if (url.pathname.endsWith('.glb') || 
      url.pathname.endsWith('.png') || 
      url.pathname.includes('/avatars/') ||
      url.pathname.includes('/glb_files/') ||
      url.pathname.includes('/AvatarThumbnails/')) {
    return; // Let browser handle avatar requests directly without SW interference
  }

  // Network-first for navigation requests to keep content fresh
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/'))
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
