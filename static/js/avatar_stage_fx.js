/*
  BeeSmart - Avatar Stage FX
  - Config-driven visual FX behind the registered user's GLB avatar.
  - Safe defaults, quick cleanup, no GLB/Three.js interference.
*/

(function () {
  'use strict';

  const CONFIG_URL = '/static/config/avatar_fx.json?v=20260106';
  const ICON_BASE = '/static/fx/icons/';
  const DEFAULT_AVATAR_NAME = 'Mascot Bee Avatar';

  let _configPromise = null;
  let _config = null;

  function _shouldDisableFx() {
    try {
      if (window && window.__beesmartDisableAnimations === true) return true;
    } catch (_e) { /* ignore */ }
    try {
      return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (_e2) {
      return false;
    }
  }

  function _now() {
    return (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
  }

  function _loadConfig() {
    if (_configPromise) return _configPromise;
    _configPromise = fetch(CONFIG_URL, { credentials: 'same-origin' })
      .then((r) => {
        if (!r || !r.ok) throw new Error('avatar_fx.json fetch failed');
        return r.json();
      })
      .then((j) => {
        _config = j || {};
        return _config;
      })
      .catch((e) => {
        console.warn('[AvatarFX] Config load failed; disabling stage FX:', e);
        _config = null;
        return null;
      });
    return _configPromise;
  }

  function _getStageEl(stageOrId) {
    if (!stageOrId) return null;
    if (typeof stageOrId === 'string') return document.getElementById(stageOrId);
    if (stageOrId && stageOrId.nodeType === 1) return stageOrId;
    return null;
  }

  function _ensureFxLayer(stageEl) {
    if (!stageEl) return null;
    let fx = stageEl.querySelector('.stage-fx');
    if (!fx) {
      fx = document.createElement('div');
      fx.className = 'stage-fx';
      fx.setAttribute('aria-hidden', 'true');
      stageEl.insertBefore(fx, stageEl.firstChild);
    }
    return fx;
  }

  function _pickPreset(avatarName, cfg) {
    const defaults = (cfg && cfg.defaults) || {};
    const avatars = (cfg && cfg.avatars) || {};
    const presets = (cfg && cfg.presets) || {};

    const safeName = (avatarName && String(avatarName).trim()) ? String(avatarName).trim() : DEFAULT_AVATAR_NAME;
    const presetKey = avatars[safeName] || avatars[DEFAULT_AVATAR_NAME] || 'royal';
    const preset = presets[presetKey] || {};

    return {
      cooldownMs: Number(preset.cooldownMs ?? defaults.cooldownMs ?? 900),
      particleCount: Number(preset.particleCount ?? defaults.particleCount ?? 16),
      particleAnim: String(preset.particleAnim ?? defaults.particleAnim ?? 'fxBurst'),
      tint: String(preset.tint ?? 'rgba(255,213,64,1)'),
      icons: Array.isArray(preset.icons) ? preset.icons : ['sparkle'],
      scan: !!preset.scan,
    };
  }

  function _rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function _spawnTint(fxLayer, tint) {
    const el = document.createElement('div');
    el.className = 'fx-tint';
    el.style.background = tint;
    fxLayer.appendChild(el);
    setTimeout(() => { try { el.remove(); } catch (_e) {} }, 1100);
  }

  function _spawnScan(fxLayer, tint) {
    const el = document.createElement('div');
    el.className = 'fx-scan';
    // Subtle: reuse tint but clamp opacity via CSS.
    el.style.setProperty('--fx-scan-tint', tint);
    fxLayer.appendChild(el);
    setTimeout(() => { try { el.remove(); } catch (_e) {} }, 1200);
  }

  function _spawnParticles(fxLayer, preset) {
    const rect = fxLayer.getBoundingClientRect();
    const w = rect && rect.width ? rect.width : 400;
    const h = rect && rect.height ? rect.height : 400;

    const count = Math.max(6, Math.min(40, preset.particleCount));
    const icons = preset.icons.length ? preset.icons : ['sparkle'];

    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'fx-particle';

      const iconKey = icons[Math.floor(Math.random() * icons.length)];
      const iconUrl = ICON_BASE + iconKey + '.svg';
      // Use SVG as mask so we can tint with background-color.
      p.style.webkitMaskImage = `url(${iconUrl})`;
      p.style.maskImage = `url(${iconUrl})`;
      p.style.backgroundColor = preset.tint;

      const size = _rand(12, 22);
      p.style.width = `${size}px`;
      p.style.height = `${size}px`;

      // Launch from near the center (avatar center), with variation.
      const cx = w * 0.5 + _rand(-10, 10);
      const cy = h * 0.5 + _rand(-10, 10);

      const dx = _rand(-0.42 * w, 0.42 * w);
      const dy = _rand(-0.38 * h, 0.15 * h);

      p.style.left = `${cx}px`;
      p.style.top = `${cy}px`;
      p.style.setProperty('--fx-dx', `${dx}px`);
      p.style.setProperty('--fx-dy', `${dy}px`);
      p.style.setProperty('--fx-rot', `${_rand(-220, 220)}deg`);

      // Stagger to avoid a single dense clump.
      p.style.animationDelay = `${_rand(0, 120)}ms`;
      p.style.animationName = preset.particleAnim;

      fxLayer.appendChild(p);
      setTimeout(() => { try { p.remove(); } catch (_e) {} }, 1350);
    }
  }

  async function playStageFX(stageOrId, avatarName) {
    if (_shouldDisableFx()) return;
    const stageEl = _getStageEl(stageOrId) || document.getElementById('avatarStage') || document.getElementById('avatarFxHost');
    if (!stageEl) return;

    const cfg = _config || (await _loadConfig());
    if (!cfg) return;

    const name = avatarName || stageEl.getAttribute('data-avatar-name') || DEFAULT_AVATAR_NAME;
    const preset = _pickPreset(name, cfg);

    const last = Number(stageEl.getAttribute('data-fx-last') || '0');
    const t = _now();
    if (last && (t - last) < preset.cooldownMs) return;
    stageEl.setAttribute('data-fx-last', String(t));

    const fxLayer = _ensureFxLayer(stageEl);
    if (!fxLayer) return;

    _spawnTint(fxLayer, preset.tint);
    if (preset.scan) _spawnScan(fxLayer, preset.tint);
    _spawnParticles(fxLayer, preset);
  }

  function _autoBind() {
    try {
      const stage = document.getElementById('avatarStage') || document.getElementById('avatarFxHost');
      if (!stage) return;

      // Prefer binding to the GLB host/container so Three.js controls still work.
      const glbHost = stage.querySelector('.stage-glb') || document.getElementById('avatarControls3D') || stage;

      const fire = () => {
        try {
          const name = stage.getAttribute('data-avatar-name') || DEFAULT_AVATAR_NAME;
          playStageFX(stage, name);
        } catch (_e) { /* ignore */ }
      };

      // Pointer events are best (no 300ms click delay), but keep fallbacks for older iOS/Safari.
      if (window && 'PointerEvent' in window) {
        glbHost.addEventListener('pointerup', fire, { passive: true });
      } else {
        glbHost.addEventListener('touchend', fire, { passive: true });
        glbHost.addEventListener('click', fire, { passive: true });
      }
    } catch (e) {
      console.warn('[AvatarFX] bind failed:', e);
    }
  }

  // Expose public API
  window.playStageFX = playStageFX;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      _autoBind();
      // Preload config opportunistically; ignore failures.
      _loadConfig();
    }, { once: true });
  } else {
    _autoBind();
    _loadConfig();
  }
})();
