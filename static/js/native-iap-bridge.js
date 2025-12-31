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

  function isDiagEnabled() {
    // Diagnostics can be enabled via URL param OR a persistent local flag.
    // This is important for TestFlight where you often can't type a URL.
    try {
      const qs = new URLSearchParams(window.location && window.location.search ? window.location.search : '');
      if (qs.get('iap_diag') === '1') return true;
    } catch (e) { /* ignore */ }

    try {
      if (window.localStorage && window.localStorage.getItem('beesmart_iap_diag') === '1') return true;
    } catch (e) { /* ignore */ }

    return false;
  }

  function ensureDiagButton() {
    // Visible debug control for TestFlight: a small button to toggle diagnostics.
    // We keep it behind a safe opt-in so it won't show for regular production users.
    // Enable by adding either:
    //   1) URL param:  ?iap_diag_btn=1
    //   2) localStorage: beesmart_iap_diag_btn=1
    // Once visible, it can enable the overlay and show the key info immediately.
    try {
      const qs = new URLSearchParams(window.location && window.location.search ? window.location.search : '');
      const enabledByUrl = qs.get('iap_diag_btn') === '1';
      let enabledByStorage = false;
      try {
        enabledByStorage = (window.localStorage && window.localStorage.getItem('beesmart_iap_diag_btn') === '1');
      } catch (e) { /* ignore */ }

      if (!enabledByUrl && !enabledByStorage) return;

      const id = 'beesmart-iap-diag-btn';
      if (document.getElementById(id)) return;

      const btn = document.createElement('button');
      btn.id = id;
      btn.type = 'button';
      btn.textContent = 'IAP Diag';
      btn.style.cssText = [
        'position:fixed',
        'right:10px',
        'bottom:10px',
        'z-index:2147483647',
        'padding:10px 12px',
        'border-radius:12px',
        'border:1px solid rgba(255,255,255,0.22)',
        'background:rgba(0,0,0,0.72)',
        'color:#fff',
        'font:600 13px/1 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',
        'box-shadow:0 8px 24px rgba(0,0,0,0.28)'
      ].join(';');

      btn.addEventListener('click', function () {
        const enabled = toggleDiagFlag();
        const cap = window.Capacitor;
        const plugin = getNativePlugin();
        const availableKeys = (cap && cap.Plugins) ? Object.keys(cap.Plugins) : [];
        const platform = (cap && typeof cap.getPlatform === 'function') ? cap.getPlatform() : null;
        const hasCap = !!cap;
        const found = !!plugin;

        const msg = [
          'IAP diagnostics ' + (enabled ? 'ENABLED' : 'DISABLED'),
          'Capacitor: ' + (hasCap ? 'YES' : 'NO'),
          'Platform: ' + (platform || '(unknown)'),
          'Plugin found: ' + (found ? 'YES' : 'NO'),
          'Plugins: ' + (availableKeys.length ? availableKeys.join(', ') : '(none)')
        ].join('\n');

        // Try to copy the info so it can be pasted into chat.
        try {
          if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(msg).catch(function () { /* ignore */ });
          }
        } catch (e) { /* ignore */ }

        alert(msg + '\n\n(Info copied if clipboard access is allowed.)');

        // If enabling, reload to trigger overlay.
        if (enabled) {
          try { window.location.reload(); } catch (e) { /* ignore */ }
        }
      });

      (document.body ? document.body : document.documentElement).appendChild(btn);
    } catch (e) { /* ignore */ }
  }

  function toggleDiagFlag() {
    try {
      const cur = window.localStorage && window.localStorage.getItem('beesmart_iap_diag');
      const next = (cur === '1') ? '0' : '1';
      if (window.localStorage) window.localStorage.setItem('beesmart_iap_diag', next);
      return next === '1';
    } catch (e) {
      return false;
    }
  }

  function installDiagGesture() {
    // Hidden gesture: tap bottom-left corner 5 times within 2.5s.
    // Then we toggle diagnostics and reload to make the overlay appear.
    try {
      let taps = 0;
      let t0 = 0;

      document.addEventListener('click', function (ev) {
        try {
          const x = (ev && typeof ev.clientX === 'number') ? ev.clientX : null;
          const y = (ev && typeof ev.clientY === 'number') ? ev.clientY : null;
          if (x === null || y === null) return;

          // 70x70px hotspot
          if (x > 70) return;
          if (y < (window.innerHeight - 70)) return;

          const now = Date.now();
          if (!t0 || (now - t0) > 2500) {
            t0 = now;
            taps = 0;
          }
          taps++;

          if (taps >= 5) {
            taps = 0;
            t0 = 0;
            const enabled = toggleDiagFlag();
            alert('IAP diagnostics ' + (enabled ? 'enabled' : 'disabled') + '.\nReloading…');
            try { window.location.reload(); } catch (e) { /* ignore */ }
          }
        } catch (e) { /* ignore */ }
      }, true);
    } catch (e) {
      // ignore
    }
  }

  try {
    // Always install a hidden gesture so diagnostics can be enabled in TestFlight
    // without needing to manually type a URL.
    installDiagGesture();

  // Optional: show a visible button when explicitly enabled.
  ensureDiagButton();

    // Optional on-device diagnostics.
    // Enable via `?iap_diag=1` OR localStorage flag `beesmart_iap_diag=1`.
    // This is intentionally low-risk: it logs to console and shows a small overlay.
    if (isDiagEnabled()) {
      const cap = window.Capacitor;
      const plugin = getNativePlugin();
      const availableKeys = (cap && cap.Plugins) ? Object.keys(cap.Plugins) : [];
      const platform = (cap && typeof cap.getPlatform === 'function') ? cap.getPlatform() : null;
      const hasCap = !!cap;
      const found = !!plugin;

      console.log('[BeeSmartIAP][diag] hasCapacitor=', hasCap,
        'platform=', platform,
        'plugins=', availableKeys,
        'pluginFound=', found);

      // Tiny overlay for cases where Web Inspector isn't available.
      try {
        const id = 'beesmart-iap-diag-overlay';
        if (!document.getElementById(id)) {
          const el = document.createElement('div');
          el.id = id;
          el.style.cssText = [
            'position:fixed',
            'left:8px',
            'bottom:8px',
            'z-index:2147483647',
            'max-width:92vw',
            'padding:8px 10px',
            'border-radius:10px',
            'background:rgba(0,0,0,0.72)',
            'color:#fff',
            'font:12px/1.35 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',
            'box-shadow:0 8px 24px rgba(0,0,0,0.28)',
            'pointer-events:none',
            'white-space:pre-wrap'
          ].join(';');
          const keysStr = availableKeys.length ? availableKeys.join(', ') : '(none)';
          el.textContent = `IAP diag\nCapacitor: ${hasCap ? 'YES' : 'NO'}\nPlatform: ${platform || '(unknown)'}\nPlugin found: ${found ? 'YES' : 'NO'}\nPlugins: ${keysStr}`;

          // Add after DOM is ready.
          (document.body ? document.body : document.documentElement).appendChild(el);
        }
      } catch (e2) { /* ignore */ }
    }

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
