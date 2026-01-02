// BeeSmart - Global randomized button press SFX
// Plays one random sound on any button-like press.
// - Prefers /static/sounds/ButtonPresses/*.mp3 (if present on the server)
// - Falls back to /static/sounds/button-click.mp3
(function () {
  if (window.BeeSmartButtonSfx) return;

  const FALLBACK_FILES = ['/static/sounds/button-click.mp3'];

  // Keep FILES as a stable reference (other pages may read BeeSmartButtonSfx.files)
  // and mutate it in-place when the server provides a playlist.
  const FILES = Array.from(FALLBACK_FILES);

  function replaceFilesInPlace(next) {
    try {
      if (!Array.isArray(next) || !next.length) return;
      FILES.length = 0;
      for (const url of next) {
        if (typeof url === 'string' && url.trim()) FILES.push(url);
      }
      if (!FILES.length) {
        FILES.push.apply(FILES, FALLBACK_FILES);
      }
    } catch (_) {
      // leave FILES as-is
    }
  }

  // Try to load the server-side playlist (if the folder exists). Non-fatal if missing.
  try {
    fetch('/api/button-press-sfx', { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : []))
      .then(replaceFilesInPlace)
      .catch(() => {});
  } catch (_) {}

  const STORAGE_KEY = 'beesmart_sfx_enabled_v1';
  const state = { lastAt: 0, lastUrl: null };

  function getEnabled() {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      if (v === null) return true;
      return v !== '0';
    } catch (_) {
      return true;
    }
  }

  function setEnabled(on) {
    try {
      localStorage.setItem(STORAGE_KEY, on ? '1' : '0');
    } catch (_) {}
  }

  function wasJustPlayed(ms) {
    const windowMs = typeof ms === 'number' ? ms : 180;
    return Date.now() - state.lastAt < windowMs;
  }

  function getRandomUrl() {
    if (!FILES.length) return null;
    const idx = Math.floor(Math.random() * FILES.length);
    return FILES[idx];
  }

  function playRandom(opts) {
    try {
      if (!getEnabled()) return;
      if (wasJustPlayed(90)) return;
      const url = getRandomUrl();
      if (!url) return;

      state.lastAt = Date.now();
      state.lastUrl = url;

      const audio = new Audio(url);
      audio.volume = opts && typeof opts.volume === 'number' ? opts.volume : 0.32;
      const p = audio.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    } catch (_) {
      // no-op
    }
  }

  function findButtonTarget(target) {
    try {
      if (!target || !target.closest) return null;
      const el = target.closest(
        'button, input[type="button"], input[type="submit"], input[type="reset"], [role="button"], .btn, .btn-action, .action-btn, .quiz-button, .menu-option'
      );
      if (!el) return null;
      if (el.getAttribute && el.getAttribute('data-no-button-sfx') === '1') return null;
      if (el.disabled) return null;
      if (String((el.getAttribute && el.getAttribute('aria-disabled')) || '').toLowerCase() === 'true') return null;
      return el;
    } catch (_) {
      return null;
    }
  }

  function onPointerDown(e) {
    const btn = findButtonTarget(e.target);
    if (!btn) return;
    playRandom({ volume: 0.32 });
  }

  function onKeyDown(e) {
    const k = e && e.key;
    if (k !== 'Enter' && k !== ' ') return;
    const btn = findButtonTarget(document.activeElement);
    if (!btn) return;
    playRandom({ volume: 0.32 });
  }

  window.BeeSmartButtonSfx = {
    files: FILES,
    getEnabled,
    setEnabled,
    wasJustPlayed,
    getRandomUrl,
    playRandom,
  };

  document.addEventListener('pointerdown', onPointerDown, true);
  document.addEventListener('keydown', onKeyDown, true);
})();
