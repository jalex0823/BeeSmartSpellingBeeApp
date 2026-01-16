/* BeeSmart Spelling App - Simple Service Worker for PWA baseline */
// Bump this to force clients to refresh cached assets after important fixes.
// 2026-01-05: iOS Connect fixes (loader/system checks, registered avatar stability, restore hang).
// IMPORTANT: do not precache HTML navigations like '/' — stale cached HTML can break auth-gated flows.
// 2026-01-07: cache bust + ensure Word Lists UI updates immediately (Apple review).
// 2026-01-16: force-refresh SW caches + never intercept /quiz (fix stale quiz HTML / JS syntax errors).
const CACHE_VERSION = 'beesmart-v1.4.6-v40-2026-01-16-no-quiz-cache';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

// Minimal core assets to cache; extend as needed
const CORE_ASSETS = [
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

// Allow clients to force immediate activation (helps iOS Safari/PWA apply updates promptly).
self.addEventListener('message', (event) => {
  try {
    const data = event && event.data;
    if (data && (data.type === 'SKIP_WAITING' || data === 'SKIP_WAITING')) {
      self.skipWaiting();
    }
  } catch (_e) {
    // no-op
  }
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

  // ✅ Word Lists page is being actively iterated and must never be served stale.
  // Let the browser handle it directly (no SW interception/caching).
  if (url.pathname === '/word-lists') {
    return;
  }

  // ✅ Quiz HTML must never be cached/intercepted by the SW.
  // If an older SW ever cached /quiz HTML, clients can end up running stale inline JS
  // even after a deploy (manifesting as SyntaxError and QuizManager not defined).
  if (url.pathname === '/quiz' || url.pathname === '/speed-round/quiz') {
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
    url.pathname.startsWith('/api/wordbank/') ||
    // ✅ Avatar/session-sensitive APIs (auth-dependent): bypass SW to avoid stale/offline fallbacks.
    url.pathname === '/api/users/me/avatar' ||
    url.pathname === '/api/avatars' ||
    // ✅ IAP flows: allow direct network so restore/reconcile isn't affected by SW caching.
    url.pathname.startsWith('/api/iap/')
  ) {
    return;
  }

  // ✅ Word list APIs: always bypass the SW so buttons work immediately after deploy.
  if (url.pathname.startsWith('/api/saved-lists') || url.pathname.startsWith('/api/buzz-dust/')) {
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
        .catch(() => {
          // Offline fallback (do not rely on cached '/'; auth pages can differ per user).
          return new Response(
            '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline</title></head><body style="font-family:system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding:16px;"><h2>BeeSmart is offline</h2><p>Please check your connection and try again.</p></body></html>',
            { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
        })
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
