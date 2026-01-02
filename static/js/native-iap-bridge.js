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
      const data = await res.json().catch(function () { return null; });

      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: !!(data && data.success), reason: reason || 'native_reconcile', data, owned }
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
      const data = await r.json().catch(function () { return null; });
      try {
        window.dispatchEvent(new CustomEvent('beesmart:iap-reconciled', {
          detail: { ok: !!(data && data.success), reason: reason || 'unknown', data }
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
        if (typeof nativePlugin.restorePurchases === 'function') {
          const out = await Promise.resolve(nativePlugin.restorePurchases());
          // After restore, reconcile owned products to server.
          try { await reconcileFromNative('restore'); } catch (e) { /* ignore */ }
          return out;
        }
        // Back-compat no-op: older native wrappers only supported getOwnedProducts.
        return { unsupported: true };
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
