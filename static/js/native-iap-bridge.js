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

  // Regression guard: we never want to present a dead-end “browser session” message
  // inside TestFlight/native wrappers. If any caller reintroduces this wording,
  // surface a console warning to make it obvious during QA.
  try {
    const _warn = console.warn;
    console.warn = function () {
      try {
        const args = Array.prototype.slice.call(arguments);
        const joined = args.map(function (x) { return String(x); }).join(' ');
        if (joined.toLowerCase().indexOf('browser session') !== -1) {
          _warn.call(console, '[BeeSmartIAP][guard] Detected "browser session" wording. This should not be shown to users.');
        }
      } catch (e) { /* ignore */ }
      return _warn.apply(console, arguments);
    };
  } catch (e) { /* ignore */ }

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

  function isIapDebugEnabled() {
    // Unified gating with the rest of the app: keep any diagnostic UI hidden
    // unless explicitly enabled.
    // NOTE: unified_menu.html sets window.BEESMART_IAP_DEBUG early.
    try { if (window.BEESMART_IAP_DEBUG === true) return true; } catch (e) { /* ignore */ }

    // Fallbacks in case the template hasn't defined the flag yet.
    try {
      const qs = new URLSearchParams(window.location && window.location.search ? window.location.search : '');
      if (qs.get('iap_debug') === '1') return true;
    } catch (e) { /* ignore */ }

    try {
      const v = window.localStorage && window.localStorage.getItem('BEESMART_IAP_DEBUG');
      if (v === '1' || v === 'true' || v === 'yes' || v === 'on') return true;
    } catch (e) { /* ignore */ }

    return false;
  }

  function ensureDiagButton() {
    // Visible debug control for TestFlight (and anywhere else): always show a button
    // that reveals a diagnostics panel and attempts to copy the info.
    // This avoids invisible-gating problems and gives you a single obvious control.
    try {
      const btnId = 'beesmart-iap-diag-btn';
      const panelId = 'beesmart-iap-diag-panel';

      if (document.getElementById(btnId)) return;

      function buildDiagnosticsText() {
        const cap = window.Capacitor;
        const plugin = getNativePlugin();
        const availableKeys = (cap && cap.Plugins) ? Object.keys(cap.Plugins) : [];
        const platform = (cap && typeof cap.getPlatform === 'function') ? cap.getPlatform() : null;
        const hasCap = !!cap;
        const found = !!plugin;
        const bridgeReady = hasBridge();

        return [
          'BeeSmart IAP Diagnostics',
          'Capacitor: ' + (hasCap ? 'YES' : 'NO'),
          'Platform: ' + (platform || '(unknown)'),
          'Plugin found: ' + (found ? 'YES' : 'NO'),
          'Bridge ready (window.BeeSmartIAP): ' + (bridgeReady ? 'YES' : 'NO'),
          'Plugins: ' + (availableKeys.length ? availableKeys.join(', ') : '(none)'),
          'URL: ' + String(window.location && window.location.href ? window.location.href : '(unknown)')
        ].join('\n');
      }

      function ensurePanel() {
        let panel = document.getElementById(panelId);
        if (panel) return panel;

        panel = document.createElement('div');
        panel.id = panelId;
        panel.style.cssText = [
          'position:fixed',
          'left:10px',
          'right:10px',
          'bottom:56px',
          'z-index:2147483647',
          'max-height:45vh',
          'overflow:auto',
          'padding:12px',
          'border-radius:12px',
          'border:1px solid rgba(255,255,255,0.22)',
          'background:rgba(0,0,0,0.78)',
          'color:#fff',
          'font:500 12px/1.35 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',
          'box-shadow:0 10px 30px rgba(0,0,0,0.35)'
        ].join(';');

        const row = document.createElement('div');
        row.style.cssText = 'display:flex;gap:8px;align-items:center;justify-content:flex-end;margin-bottom:8px;';

        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.textContent = 'Copy';
        copyBtn.style.cssText = 'padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,0.18);background:rgba(255,255,255,0.12);color:#fff;font:600 12px/1 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;';

        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.textContent = 'Close';
        closeBtn.style.cssText = 'padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,0.18);background:rgba(255,255,255,0.12);color:#fff;font:600 12px/1 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;';
        closeBtn.addEventListener('click', function () {
          try { panel.remove(); } catch (e) { /* ignore */ }
        });

        row.appendChild(copyBtn);
        row.appendChild(closeBtn);

        const pre = document.createElement('pre');
        pre.style.cssText = 'margin:0;white-space:pre-wrap;word-break:break-word;';
        pre.textContent = buildDiagnosticsText();

        copyBtn.addEventListener('click', function () {
          const txt = buildDiagnosticsText();
          pre.textContent = txt;
          try {
            if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
              navigator.clipboard.writeText(txt).catch(function () { /* ignore */ });
            }
          } catch (e) { /* ignore */ }
        });

        panel.appendChild(row);
        panel.appendChild(pre);
        (document.body ? document.body : document.documentElement).appendChild(panel);
        return panel;
      }

      const btn = document.createElement('button');
      btn.id = btnId;
      btn.type = 'button';
      btn.textContent = 'IAP Diagnostics';
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
        'font:700 13px/1 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',
        'box-shadow:0 8px 24px rgba(0,0,0,0.28)'
      ].join(';');

      btn.addEventListener('click', function () {
        // Keep existing overlay behavior available, but don't require reload or alerts.
        try {
          if (window.localStorage) window.localStorage.setItem('beesmart_iap_diag', '1');
        } catch (e) { /* ignore */ }

        const panel = ensurePanel();
        try {
          const pre = panel && panel.querySelector ? panel.querySelector('pre') : null;
          if (pre) pre.textContent = buildDiagnosticsText();
        } catch (e) { /* ignore */ }

        // Attempt an immediate copy.
        try {
          const txt = buildDiagnosticsText();
          if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(txt).catch(function () { /* ignore */ });
          }
        } catch (e) { /* ignore */ }

        // If the bridge is not ready yet, try initializing once more now.
        try { initBridgeOnce(); } catch (e) { /* ignore */ }
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

    // Safety: older builds may have left this flag enabled, causing the black
    // overlay to reappear unexpectedly. We now gate diagnostics UI behind the
    // unified debug flag, so clear the legacy flag unless debug is enabled.
    try {
      if (!isIapDebugEnabled() && window.localStorage && window.localStorage.getItem('beesmart_iap_diag') === '1') {
        window.localStorage.setItem('beesmart_iap_diag', '0');
      }
    } catch (e) { /* ignore */ }

    // Only show the visible diagnostics button when debug/diagnostics are enabled.
    // (Avoid exposing developer UI in production/review builds.)
    if (isIapDebugEnabled() || isDiagEnabled()) {
      ensureDiagButton();
    }

    // Optional on-device diagnostics overlay.
    // Keep this completely hidden unless unified debug is explicitly enabled.
    // (The visible diagnostics button/panel is enough when debug is on.)
    if (isIapDebugEnabled() && isDiagEnabled()) {
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
