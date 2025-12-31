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

  // Capacitor sometimes populates `Capacitor.Plugins` slightly after our script runs
  // (especially with `defer`), so we retry a few times before giving up.
  const MAX_ATTEMPTS = 25; // ~2.5s @ 100ms
  const RETRY_MS = 100;

  function hasBridge() {
    return !!(window.BeeSmartIAP && typeof window.BeeSmartIAP.getOwnedProducts === 'function');
  }

  function getNativePlugin() {
    const cap = window.Capacitor;
    const plugins = cap && cap.Plugins;
    // Capacitor v5 uses `Capacitor.Plugins.<PluginName>`.
    // Our iOS bridge registers as BeeSmartIAPPlugin (class name).
    return plugins && (plugins.BeeSmartIAP || plugins.BeeSmartIAPPlugin);
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

      async restore() {
        // Initiates the platform restore/sync flow (iOS: AppStore.sync()).
        if (typeof nativePlugin.restorePurchases === 'function') {
          return await Promise.resolve(nativePlugin.restorePurchases());
        }
        // Back-compat no-op: older native wrappers only supported getOwnedProducts.
        return { unsupported: true };
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
        return out;
      }
    };

    try {
      console.log('[BeeSmartIAP] bridged from Capacitor plugin (platform=' + platform + ')');
      // Light readiness signal for UI/debugging.
      window.dispatchEvent(new CustomEvent('beesmart:iap-ready', { detail: { platform } }));
    } catch (e) {
      // ignore
    }
    return true;
  }

  try {
    // Fast path
    if (initBridgeOnce()) return;

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
          try { console.warn('[BeeSmartIAP] native bridge init failed:', e); } catch (e2) {}
        }
      }
    }, RETRY_MS);
  } catch (e) {
    try {
      console.warn('[BeeSmartIAP] native bridge init failed:', e);
    } catch (e2) {
      // ignore
    }
  }
})();
