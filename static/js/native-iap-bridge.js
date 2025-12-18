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

  try {
    // Do not override an existing native bridge (or a test/mock bridge).
    if (window.BeeSmartIAP && typeof window.BeeSmartIAP.getOwnedProducts === 'function') {
      return;
    }

    const cap = window.Capacitor;
    const plugins = cap && cap.Plugins;

    // Capacitor v5 uses `Capacitor.Plugins.<PluginName>`.
    const nativePlugin = plugins && (plugins.BeeSmartIAP || plugins.BeeSmartIAPPlugin);
    if (!nativePlugin) {
      return;
    }

    const capPlatform = (cap && typeof cap.getPlatform === 'function') ? cap.getPlatform() : null;
    const platform = (capPlatform === 'ios') ? 'apple' : ((capPlatform === 'android') ? 'google' : 'web');

    window.BeeSmartIAP = {
      platform,

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
    } catch (e) {
      // ignore
    }
  } catch (e) {
    try {
      console.warn('[BeeSmartIAP] native bridge init failed:', e);
    } catch (e2) {
      // ignore
    }
  }
})();
