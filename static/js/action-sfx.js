// BeeSmart - Action outcome SFX (success / error)
// - No external audio files required (uses WebAudio)
// - Respects the global button SFX enabled toggle if present (BeeSmartButtonSfx)
(function () {
  if (window.BeeSmartActionSfx) return;

  let _ctx = null;

  function _isEnabled() {
    try {
      if (window.BeeSmartButtonSfx && typeof window.BeeSmartButtonSfx.getEnabled === 'function') {
        return !!window.BeeSmartButtonSfx.getEnabled();
      }
      return true;
    } catch (_) {
      return true;
    }
  }

  function _ctxNow() {
    return _ctx ? _ctx.currentTime : 0;
  }

  function _getCtx() {
    if (_ctx) return _ctx;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    _ctx = new Ctx();
    return _ctx;
  }

  function _safeResume() {
    try {
      if (_ctx && _ctx.state === 'suspended') _ctx.resume();
    } catch (_) {}
  }

  function _tone(freq, start, dur, type, gain) {
    try {
      const ctx = _getCtx();
      if (!ctx) return;
      _safeResume();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = type || 'sine';
      o.frequency.setValueAtTime(Math.max(40, freq || 440), start);
      g.gain.setValueAtTime(0.0001, start);
      g.gain.exponentialRampToValueAtTime(Math.max(0.0001, gain || 0.08), start + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, start + Math.max(0.03, dur || 0.12));
      o.connect(g);
      g.connect(ctx.destination);
      o.start(start);
      o.stop(start + Math.max(0.03, dur || 0.12) + 0.02);
    } catch (_) {}
  }

  function _chirp(startFreq, endFreq, start, dur, type, gain) {
    try {
      const ctx = _getCtx();
      if (!ctx) return;
      _safeResume();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = type || 'triangle';
      o.frequency.setValueAtTime(Math.max(40, startFreq || 440), start);
      o.frequency.exponentialRampToValueAtTime(Math.max(40, endFreq || 220), start + Math.max(0.03, dur || 0.18));
      g.gain.setValueAtTime(0.0001, start);
      g.gain.exponentialRampToValueAtTime(Math.max(0.0001, gain || 0.09), start + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, start + Math.max(0.03, dur || 0.18));
      o.connect(g);
      g.connect(ctx.destination);
      o.start(start);
      o.stop(start + Math.max(0.03, dur || 0.18) + 0.02);
    } catch (_) {}
  }

  function success() {
    try {
      if (!_isEnabled()) return;
      const ctx = _getCtx();
      if (!ctx) return;
      const t0 = _ctxNow() + 0.005;
      // bright two-note "ding"
      _tone(880, t0, 0.11, 'sine', 0.08);
      _tone(1174, t0 + 0.09, 0.14, 'sine', 0.075);
      // tiny sparkle shimmer
      _chirp(1600, 2400, t0 + 0.02, 0.12, 'triangle', 0.03);
    } catch (_) {}
  }

  function error() {
    try {
      if (!_isEnabled()) return;
      const ctx = _getCtx();
      if (!ctx) return;
      const t0 = _ctxNow() + 0.005;
      // short descending "buzz"
      _chirp(240, 120, t0, 0.18, 'square', 0.07);
      _tone(90, t0 + 0.05, 0.14, 'square', 0.03);
    } catch (_) {}
  }

  // Optional attribute-based hooks: <button data-action-sfx="success|error">
  function _onClick(e) {
    try {
      const el = e && e.target && e.target.closest ? e.target.closest('[data-action-sfx]') : null;
      if (!el) return;
      const v = String(el.getAttribute('data-action-sfx') || '').toLowerCase().trim();
      if (v === 'success') success();
      else if (v === 'error' || v === 'fail' || v === 'failure') error();
    } catch (_) {}
  }

  window.BeeSmartActionSfx = { success, error };
  document.addEventListener('click', _onClick, true);
})();

