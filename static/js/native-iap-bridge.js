 /**
 * Native IAP Bridge (Capacitor)
 *
 * Purpose:
 * - Provide a stable, cross-platform `window.BeeSmartIAP` API for the web UI.
 * - Backed by the Capacitor native plugin `BeeSmartIAP` when running inside
 *   the iOS/Android wrappers.
 *
 * Contract used by the Flask templates:
 *   - window.BeeSmartIAP.platform: 'apple' | 'google' | 'web'
 *   - window.BeeSmartIAP.getOwnedProducts(): Promise<Array<string|object>>
 *   - window.BeeSmartIAP.purchase(productId): Promise<object>
 */

(function () {
  'use strict';

  // Login handoff:
  // When the user signs in, /auth/login now returns a fresh entitlements summary.
  // The login page stores it in localStorage so the *next* page load can trigger
  // the same refresh pathway used by native restores (beesmart:iap-reconciled).
  // This avoids requiring a manual refresh after login.
  function consumeLoginEntitlementsHandoff() {
    try {
      if (!window.localStorage) return null;
      const key = 'beesmart_login_entitlements_v1';
      const raw = window.localStorage.getItem(key);
      if (!raw || typeof raw !== 'string') return null;

      let parsed = null;
      try { parsed = JSON.parse(raw); } catch (e) { parsed = null; }
      window.localStorage.removeItem(key);

      if (!parsed || typeof parsed !== 'object') return null;
      const ts = parsed.ts;
      const entitlements = parsed.entitlements;
      if (!entitlements || typeof entitlements !== 'object') return null;

      // Expire old handoffs (e.g., stale localStorage) to avoid surprising refreshes.
      if (typeof ts === 'number' && (Date.now() - ts) > 2 * 60 * 1000) return null;

      return entitlements;
    } catch (e) {
      return null;
    }
  }

  function schedulePostLoginRefresh(entitlements) {
    try {
      const fire = function () {
        // Allow other DOMContentLoaded handlers (that install listeners) to run first.
        setTimeout(function () {
          try {
            window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
              detail: {
                ok: true,
                status: 200,
                reason: 'login_handoff',
                data: { success: true, entitlements: entitlements },
                owned: (entitlements && (entitlements.anon_owned_products || entitlements.owned_products)) || []
              }
            }));
          } catch (e) { /* ignore */ }
        }, 0);
      };

      if (document && document.readyState === 'loading') {
        window.addEventListener('DOMContentLoaded', fire, { once: true });
      } else {
        fire();
      }
    } catch (e) { /* ignore */ }
  }

  // Subscription enforcement refresh:
  // Ensure entitlement state is refreshed on app launch and when the app resumes
  // (iOS/Android WebView + Safari). This supports UI prompts and content gating.
  let _lastAutoReconcileAt = 0;
  function autoReconcile(reason) {
    try {
      const now = Date.now();
      // Throttle to avoid repeated calls during rapid visibility changes.
      if (_lastAutoReconcileAt && (now - _lastAutoReconcileAt) < 5000) return;
      _lastAutoReconcileAt = now;

      // Defer slightly to let page listeners install first.
      setTimeout(function () {
        try {
          if (hasBridge()) {
            reconcileFromNative(reason || 'auto');
          } else {
            serverReconcile(reason || 'auto_no_bridge');
          }
        } catch (e) { /* ignore */ }
      }, 0);
    } catch (e) { /* ignore */ }
  }

  function installAutoReconcileListeners() {
    try {
      if (window.__beesmartAutoReconcileInstalled) return;
      window.__beesmartAutoReconcileInstalled = true;

      // App launch / initial paint.
      autoReconcile('app_launch');

      // App resume.
      document.addEventListener('visibilitychange', function () {
        try {
          if (document.visibilityState === 'visible') {
            autoReconcile('app_resume_visibility');
          }
        } catch (e) { /* ignore */ }
      });

      // BFCache restores (Safari) can skip full reloads.
      window.addEventListener('pageshow', function (ev) {
        try {
          if (ev && ev.persisted) {
            autoReconcile('app_resume_pageshow');
          }
        } catch (e) { /* ignore */ }
      });
    } catch (e) { /* ignore */ }
  }

  // Optional continuity helper:
  // - In production native wrappers, prefer providing a stable keychain identifier
  //   via the Capacitor plugin (e.g., getInstallId()) so guest restores can be
  //   re-associated after reinstall.
  // - In pure web contexts, we fall back to localStorage (best-effort only).
  function _getOrCreateWebInstallId() {
    try {
      if (!window.localStorage) return null;
      const key = 'beesmart_install_id_v1';
      let v = window.localStorage.getItem(key);
      if (v && typeof v === 'string' && v.length >= 12) return v;
      // Prefer crypto.randomUUID where available
      if (window.crypto && typeof window.crypto.randomUUID === 'function') {
        v = window.crypto.randomUUID();
      } else {
        // Non-crypto fallback: still fine for *best-effort* browser continuity.
        v = 'web_' + Math.random().toString(16).slice(2) + Date.now().toString(16);
      }
      window.localStorage.setItem(key, v);
      return v;
    } catch (e) {
      return null;
    }
  }

  async function _getInstallIdForServer() {
    // Try native first. This is the key part for "survive reinstall".
    try {
      const p = getNativePlugin();
      if (p && typeof p.getInstallId === 'function') {
        const r = await Promise.resolve(p.getInstallId());
        if (r && typeof r.installId === 'string' && r.installId.trim()) return r.installId.trim();
        if (typeof r === 'string' && r.trim()) return r.trim();
      }
    } catch (e) { /* ignore */ }

    return _getOrCreateWebInstallId();
  }

  // IMPORTANT: No customer-facing diagnostics.
  // We avoid monkey-patching console.* in production because some native shells
  // surface console output on-screen.

  // Capacitor sometimes populates `Capacitor.Plugins` slightly after our script runs
  // (especially with `defer`), so we retry a few times before giving up.
  const MAX_ATTEMPTS = 25; // ~2.5s @ 100ms
  const RETRY_MS = 100;

  function hasBridge() {
    return !!(window.BeeSmartIAP && typeof window.BeeSmartIAP.getOwnedProducts === 'function');
  }

  async function reconcileFromNative(reason) {
    // Pull owned products from the native layer (if available) and apply them
    // server-side so premium flags / avatar unlocks update immediately.
    // Always emits beesmart:iap-reconciled for the UI to refresh.
    try {
      if (!hasBridge()) {
        return await serverReconcile(reason || 'reconcile_no_bridge');
      }

      const install_id = await _getInstallIdForServer();
      let owned = [];
      try {
        const r = await window.BeeSmartIAP.getOwnedProducts();
        if (Array.isArray(r)) owned = r;
      } catch (e) {
        owned = [];
      }

      const platform = (window.BeeSmartIAP && window.BeeSmartIAP.platform) ? window.BeeSmartIAP.platform : 'apple';
      const res = await fetch('/api/iap/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ platform: platform || 'apple', product_ids: owned || [], install_id })
      });
      let data = await res.json().catch(function () { return null; });
      if ((res.status === 401 || res.status === 403) && (!data || typeof data !== 'object')) {
        data = {
          success: false,
          error: 'login_required',
          message: 'Please sign in to restore purchases.',
          login_url: '/auth/login'
        };
      }

      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: !!(data && data.success), status: res.status, reason: reason || 'native_reconcile', data, owned }
        }));
      } catch (e) { /* ignore */ }

      return data;
    } catch (e) {
      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: false, reason: reason || 'native_reconcile_error', error: String(e) }
        }));
      } catch (e2) { /* ignore */ }
      return null;
    }
  }

  async function serverReconcile(reason) {
    // Server-first reconcile: when the JS/native bridge is missing or late,
    // ask the backend to return current entitlements (cookie + DB-backed anon_restore_id).
    // This keeps TestFlight from getting stuck in a "web-only" branch.
    try {
      const install_id = await _getInstallIdForServer();
      const r = await fetch('/api/iap/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ platform: 'apple', product_ids: [], install_id })
      });
      let data = await r.json().catch(function () { return null; });
      if ((r.status === 401 || r.status === 403) && (!data || typeof data !== 'object')) {
        data = {
          success: false,
          error: 'login_required',
          message: 'Please sign in to restore purchases.',
          login_url: '/auth/login'
        };
      }
      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: !!(data && data.success), status: r.status, reason: reason || 'unknown', data }
        }));
      } catch (e) { /* ignore */ }
      return data;
    } catch (e) {
      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: false, reason: reason || 'unknown', error: String(e) }
        }));
      } catch (e2) { /* ignore */ }
      return null;
    }
  }

  function getNativePlugin() {
    const cap = window.Capacitor;
    const plugins = cap && cap.Plugins;
    // Capacitor v5 uses `Capacitor.Plugins.<PluginName>`.
    // Our iOS bridge registers as BeeSmartIAPPlugin (class name).
    if (!plugins) return null;

    // Be tolerant: depending on how the plugin is registered, the key can vary.
    const candidates = [
      'BeeSmartIAP',
      'BeeSmartIAPPlugin',
      'BeeSmartIap',
      'BeeSmartIapPlugin',
      'IAP',
      'IAPPlugin'
    ];

    for (const k of candidates) {
      if (plugins[k]) return plugins[k];
    }
    return null;
  }

  function initBridgeOnce() {
    // Do not override an existing native bridge (or a test/mock bridge).
    if (hasBridge()) return true;

    const cap = window.Capacitor;
    const nativePlugin = getNativePlugin();
    if (!nativePlugin) return false;

    const capPlatform = (cap && typeof cap.getPlatform === 'function') ? cap.getPlatform() : null;
    const platform = (capPlatform === 'ios') ? 'apple' : ((capPlatform === 'android') ? 'google' : 'web');

    window.BeeSmartIAP = {
      platform,

      // Expose a reconciliation helper so templates can force-refresh entitlement
      // state after purchase/restore without duplicating fetch logic.
      async reconcile(reason) {
        return await reconcileFromNative(reason || 'manual');
      },

      async restore() {
        // Initiates the platform restore/sync flow (iOS: AppStore.sync()).
        let restoreOut = null;
        let reconcileOut = null;

        if (typeof nativePlugin.restorePurchases === 'function') {
          restoreOut = await Promise.resolve(nativePlugin.restorePurchases());
          // After restore, reconcile owned products to server.
          try { reconcileOut = await reconcileFromNative('restore'); } catch (e) { /* ignore */ }
          return { restore: restoreOut, reconcile: reconcileOut, unsupported: false };
        }

        // Back-compat: older native wrappers only supported getOwnedProducts.
        // We can still reconcile to the server (best-effort), but we cannot
        // trigger an OS-level restore/sync.
        try { reconcileOut = await reconcileFromNative('restore_no_native_sync'); } catch (e) { /* ignore */ }
        return { restore: restoreOut, reconcile: reconcileOut, unsupported: true };
      },

      async restorePurchases() {
        // Alias for callers that expect the native method name.
        return await this.restore();
      },

      async getOwnedProducts() {
        const r = await Promise.resolve(nativePlugin.getOwnedProducts());
        if (!r) return [];

        // Prefer normalized list of product IDs if provided.
        if (Array.isArray(r.productIds)) return r.productIds;

        // Allow a few other shapes for flexibility.
        if (Array.isArray(r.products)) return r.products;
        if (Array.isArray(r.owned)) return r.owned;

        return [];
      },

      async purchase(productId) {
        const r = await Promise.resolve(nativePlugin.purchase({ productId }));
        const out = r && typeof r === 'object' ? r : {};

        // Normalize token/id casing for existing server endpoints.
        if (out.purchaseToken && !out.purchase_token) out.purchase_token = out.purchaseToken;
        if (out.transactionId && !out.transaction_id) out.transaction_id = out.transactionId;

        if (!out.payload) out.payload = out;

        // After purchase, reconcile owned products to server.
        try { await reconcileFromNative('purchase'); } catch (e) { /* ignore */ }
        return out;
      }
    };

    try {
      window.dispatchEvent(new CustomEvent('beesmart:iap-ready', { detail: { platform } }));
    } catch (e) { /* ignore */ }
    return true;
  }

  function isDiagEnabled() {
    // Diagnostics UI is disabled.
    return false;
  }

  function isIapDebugEnabled() {
    // Debug UI is disabled.
    return false;
  }

  function ensureDiagButton() {
    // Diagnostic UI disabled.
    return;
  }

  function toggleDiagFlag() {
    return false;
  }

  function installDiagGesture() {
    // Diagnostics disabled.
    return;
  }

  try {
    // Per request: no diagnostic UI.

    // If login handed off entitlements for this navigation, emit an event so
    // pages with listeners (subscription, avatar picker) refresh immediately.
    const loginEntitlements = consumeLoginEntitlementsHandoff();
    if (loginEntitlements) {
      schedulePostLoginRefresh(loginEntitlements);
    }

    // Keep subscription state fresh across launch/resume.
    installAutoReconcileListeners();

    // Fast path
    if (initBridgeOnce()) return;

  // Bridge isn't ready yet. Kick off a server reconcile so the UI can reflect
  // DB-backed guest entitlements immediately (and not show web-only warnings).
  // A later beesmart:iap-ready event can still flip to native flows.
  try { serverReconcile('bridge_missing_initial'); } catch (e) { /* ignore */ }

    // Retry while the app is settling.
    let attempts = 0;
    const timer = setInterval(function () {
      attempts++;
      try {
        if (initBridgeOnce() || attempts >= MAX_ATTEMPTS) {
          clearInterval(timer);
        }
      } catch (e) {
        // Keep retrying unless we hit max attempts.
        if (attempts >= MAX_ATTEMPTS) {
          clearInterval(timer);
        }
      }
    }, RETRY_MS);
  } catch (e) {
    // Ignore bridge init errors; the UI will continue with server reconcile.
  }
})();
