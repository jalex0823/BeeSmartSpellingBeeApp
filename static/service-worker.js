/* BeeSmart Spelling App - Simple Service Worker for PWA baseline */
// Bump this to force clients to refresh cached assets after important fixes
const CACHE_VERSION = 'beesmart-v1.4.3-v38-2026-01-02-disable-menu-sweep-overlay';
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

  // ✅ Admin pages can redirect to login when a session expires.
  // To avoid "redirected response" fetch errors and accidental caching of login HTML,
  // let the browser handle all /admin/* traffic directly.
  if (url.pathname.startsWith('/admin/')) {
    return;
  }

  // ✅ Auth endpoints often use redirects (e.g., /auth/logout -> /auth/login or /).
  // Some requests may have redirect mode != 'follow', which can produce:
  // "a redirected response was used for a request whose redirect mode is not 'follow'".
  // Let the browser handle these directly (no caching, no SW interception).
  if (url.pathname.startsWith('/auth/')) {
    return;
  }

  // ✅ Avatar picker HTML routes can redirect to /auth/login when a session expires.
  // If the SW intercepts one of these navigations and the response is a redirect,
  // some browsers will surface a FetchEvent network error and render a blank page.
  // Let the browser handle these routes directly.
  if (
    url.pathname === '/honeycomb-picker' ||
    url.pathname === '/honeycomb-picker-old' ||
    url.pathname === '/avatar-picker'
  ) {
    return;
  }

  // ✅ Quiz/session-critical endpoints: always bypass the SW.
  // These must reflect the *current* server-side session state, especially after app resume.
  // Letting the SW return cached/offline responses here can cause the resume modal / quiz load to stall.
  if (
    url.pathname.startsWith('/api/quiz/') ||
    url.pathname === '/api/next' ||
    url.pathname === '/api/answer' ||
    url.pathname === '/api/pronounce' ||
    url.pathname === '/api/wordbank' ||
    url.pathname.startsWith('/api/wordbank/')
  ) {
    return;
  }

  // Cache GLB files with network-first strategy (they're large but static)
  if (url.pathname.endsWith('.glb')) {
    event.respondWith(
      fetch(request).then((response) => {
        // Never cache redirects (e.g., auth/login redirects) or opaque-redirect responses.
        // Caching those can trigger: "a redirected response was used for a request whose redirect mode is not 'follow'".
        if (response && response.ok && !response.redirected && response.type !== 'opaqueredirect') {
          const copy = response.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy)).catch(() => {});
        }
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
          if (response && response.ok && !response.redirected && response.type !== 'opaqueredirect') {
            const copy = response.clone();
            caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy)).catch(() => {});
          }
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
