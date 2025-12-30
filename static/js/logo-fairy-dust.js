// BeeSmart Logo Fairy Dust Trail: directional dust stream (head + taper tail)
(function () {
    'use strict';

    const DEFAULTS = {
        // Prefer the actual IMG element first; include a stable id if present.
        logoSelector: '#beesmartCrestLogo, #beesmartCrestLogoLoader, img.brand-logo.crest-logo, img.crest-logo, img.brand-logo',
        zIndex: 12, // logo is z=10 in unified_menu, so we sit above it
        durationMs: 3200,
        // Spawn particles frequently and keep them alive longer for a dense, continuous tail.
        particleIntervalMs: 14,      // slightly denser, still light on CPU
        trailLifetimeMs: 1400,       // smoother, more "magical" tail
        maxParticles: 160,           // less CPU, still dense
        headColor: '#FFF8C9',
        tailColor: '#FFD36A',
        glowColor: 'rgba(255, 215, 0, 0.65)',
        // Path behavior
        loops: 2.0,                  // snake around twice for more motion
        wobbleAmp: 18,               // stronger wobble for whimsical path
        wobbleFreq: 5.0,             // slightly slower wobble oscillation
        // Dissipation
        fadeStartT: 0.65,
        // Sparkle burst
        burstCount: 10,
        burstLingerMs: 520,
    };

    function _getUrlParams() {
        try {
            return new URLSearchParams(window.location.search || '');
        } catch (_e) {
            return null;
        }
    }

    function isForceEnabled() {
        // Safari users often have Reduce Motion enabled (system-wide).
        // Allow an explicit override so we can still show the effect when requested.
        const params = _getUrlParams();
        const qp = params ? (params.get('fx') || params.get('logo_fx') || '') : '';
        if (String(qp).toLowerCase() === 'on') return true;

        try {
            const ls = (window.localStorage && window.localStorage.getItem)
                ? window.localStorage.getItem('BeeSmartLogoFXForce')
                : null;
            return String(ls || '').toLowerCase() === 'on';
        } catch (_e) {
            return false;
        }
    }

    function isDebugEnabled() {
        const params = _getUrlParams();
        const qp = params ? (params.get('fx_debug') || '') : '';
        if (String(qp).toLowerCase() === '1') return true;
        try {
            const ls = (window.localStorage && window.localStorage.getItem)
                ? window.localStorage.getItem('BeeSmartLogoFXDebug')
                : null;
            return String(ls || '').toLowerCase() === '1';
        } catch (_e) {
            return false;
        }
    }

    function setDebugBadge(text, ok = true) {
        if (!isDebugEnabled()) return;
        try {
            let el = document.getElementById('logoFxDebugBadge');
            if (!el) {
                el = document.createElement('div');
                el.id = 'logoFxDebugBadge';
                el.style.cssText = [
                    'position: fixed',
                    'right: 10px',
                    'bottom: 10px',
                    'z-index: 99999',
                    'font: 12px/1.2 -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
                    'padding: 8px 10px',
                    'border-radius: 10px',
                    'background: rgba(0,0,0,0.65)',
                    'color: #fff',
                    'backdrop-filter: blur(6px)',
                    'max-width: 70vw',
                    'box-shadow: 0 8px 20px rgba(0,0,0,0.25)',
                ].join(';');
                document.body.appendChild(el);
            }
            el.textContent = text;
            el.style.border = ok ? '1px solid rgba(90, 255, 150, 0.55)' : '1px solid rgba(255, 90, 90, 0.65)';
        } catch (_e) {
            // no-op
        }
    }

    function prefersReducedMotion() {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    function clamp(n, a, b) {
        return Math.max(a, Math.min(b, n));
    }

    function easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function nowMs() {
        return performance && performance.now ? performance.now() : Date.now();
    }

    function findLogo(selector) {
        const el = document.querySelector(selector);
        return isRenderableLogo(el) ? el : null;
    }

    function isRenderableLogo(el) {
        if (!el || !el.getBoundingClientRect) return false;

        const r = el.getBoundingClientRect();
        if (!r || r.width < 24 || r.height < 24) return false;

        // If it's an <img>, ensure it is loaded successfully
        if (el.tagName === 'IMG') {
            if (!el.complete) return false;
            if (!el.naturalWidth || el.naturalWidth === 0) return false;
        }

        // Also ensure it's not display:none / hidden via opacity
        try {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        } catch (_e) {
            // If computedStyle fails for any reason, fall back to trusting layout.
        }

        return true;
    }

    // Back-compat alias for older guidance/docs.
    // (We keep findLogo() calling isRenderableLogo() so behavior stays consistent.)
    const isRenderableCrest = isRenderableLogo;

    function waitForLogoAndStart(opts) {
        const start = nowMs();
        const timeoutMs = 6000;
        let done = false;
        let pollTimer = null;
        let rafId = null;
        let obs = null;

        const stop = () => {
            done = true;
            if (rafId != null) {
                try { cancelAnimationFrame(rafId); } catch (_) {}
                rafId = null;
            }
            if (pollTimer != null) {
                try { clearTimeout(pollTimer); } catch (_) {}
                pollTimer = null;
            }
            if (obs) {
                try { obs.disconnect(); } catch (_) {}
                obs = null;
            }
        };

        const tryStart = () => {
            if (done) return true;
            const logo = findLogo(opts.logoSelector);
            if (logo) {
                stop();
                startFairyDust(opts);
                return true;
            }
            return false;
        };

        // Try immediately first.
        if (tryStart()) return;

        // Fast path: try on a few animation frames first (logo often appears right after layout)
        let rafTries = 0;
        const rafTick = () => {
            if (tryStart()) return;
            rafTries++;
            if (rafTries < 20 && (nowMs() - start) < timeoutMs) {
                rafId = requestAnimationFrame(rafTick);
                return;
            }
            rafId = null;
        };
        rafId = requestAnimationFrame(rafTick);

        // Slow path: polling (covers delayed loaders)
        const poll = () => {
            if (tryStart()) return;
            if ((nowMs() - start) >= timeoutMs) {
                stop();
                setDebugBadge('Logo FX: logo not renderable before timeout', false);
                return;
            }
            pollTimer = setTimeout(poll, 200);
        };
        pollTimer = setTimeout(poll, 200);

        // Mutation observer remains helpful
        try {
            obs = new MutationObserver(() => {
                if (tryStart()) return;
            });
            obs.observe(document.documentElement || document.body, { childList: true, subtree: true });
            setTimeout(() => { stop(); }, timeoutMs);
        } catch (_e) {
            // no-op
        }
    }

    function ensureContainer() {
        let container = document.getElementById('logoFairyDustLayer');
        if (container) return container;

        container = document.createElement('div');
        container.id = 'logoFairyDustLayer';
        container.style.cssText = [
            'position: fixed',
            'left: 0',
            'top: 0',
            'width: 100vw',
            'height: 100vh',
            // Safari: make sure we sit above other stacking contexts.
            'z-index: 9999',
            'pointer-events: none',
            'overflow: visible',
            // Safari: encourage a stable compositing layer.
            'transform: translateZ(0)',
        ].join(';');

        document.body.appendChild(container);
        return container;
    }

    function ensureCanvas(container, zIndex) {
        let canvas = document.getElementById('logoFairyDustCanvas');
        if (canvas) return canvas;

        canvas = document.createElement('canvas');
        canvas.id = 'logoFairyDustCanvas';
        canvas.style.cssText = [
            'position: absolute',
            'left: 0',
            'top: 0',
            'width: 100%',
            'height: 100%',
            // Use the container z-index for stacking; keep this simple.
            `z-index: ${zIndex}`,
            // Safari: avoid accidental blending/filters that can zero out alpha.
            'mix-blend-mode: normal',
        ].join(';');

        container.appendChild(canvas);
        return canvas;
    }

    function resizeCanvas(canvas) {
        const dpr = window.devicePixelRatio || 1;
        const w = Math.max(1, Math.floor(window.innerWidth * dpr));
        const h = Math.max(1, Math.floor(window.innerHeight * dpr));
        if (canvas.width !== w || canvas.height !== h) {
            canvas.width = w;
            canvas.height = h;
        }
        return dpr;
    }

    function computePathPoint(logoRect, t, opts) {
        // Anchor points
        const cx = logoRect.left + logoRect.width / 2;
        const bottomY = logoRect.bottom;
        const topY = logoRect.top;

        // Base ascent along the logo height, starting at bottom boundary.
        const y = lerp(bottomY - 2, topY + 6, t);

        // Snake around perimeter: use an ellipse-like radius that follows logo bounds.
        const rx = logoRect.width * 0.52;
        const ry = logoRect.height * 0.48;

        // Angle wraps around while ascending.
        const theta = (Math.PI * 2) * (opts.loops * t) - Math.PI / 2;

        // Optional wobble (fluid, magical)
        const wobble = Math.sin((t * Math.PI * 2 * opts.wobbleFreq) + (theta * 0.35)) * opts.wobbleAmp;

        // Blend between perimeter wrap and centerline as we approach the top so it terminates cleanly.
        const blendToCenter = clamp((t - 0.82) / 0.18, 0, 1);

        const px = cx + Math.cos(theta) * rx + wobble;
        const py = (logoRect.top + logoRect.height / 2) + Math.sin(theta) * ry;

        const x = lerp(px, cx, blendToCenter);
        const y2 = lerp(py, y, 0.55);

        return { x, y: y2 };
    }

    function drawHead(ctx, x, y, size, opts) {
        const grad = ctx.createRadialGradient(x, y, 0, x, y, size);
        grad.addColorStop(0, opts.headColor);
        grad.addColorStop(0.35, 'rgba(255,255,255,0.95)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();

        ctx.shadowColor = opts.glowColor;
        ctx.shadowBlur = size * 3.2;
        ctx.fillStyle = 'rgba(255,140,0,0.80)';
        ctx.beginPath();
        ctx.arc(x, y, size * 0.62, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    function drawTail(ctx, from, to, t, opts) {
        // Tail is drawn as a series of fading beads behind the head.
        // More beads + shallower taper makes the tail read as a smooth trail.
        const steps = 18;
        for (let i = 1; i <= steps; i++) {
            const k = i / steps;
            const x = lerp(from.x, to.x, k);
            const y = lerp(from.y, to.y, k);

            // Larger initial size and shallower taper
            const base = 14.0 * (1 - k);
            const size = Math.max(0.6, base * (1 - t * 0.2));

            // Dissipation as we approach the top
            const fadeT = t > opts.fadeStartT ? (1 - (t - opts.fadeStartT) / (1 - opts.fadeStartT)) : 1;
            // Brighter tail with gradual fade
            const alpha = 0.55 * (1 - k) * fadeT;

            const grad = ctx.createRadialGradient(x, y, 0, x, y, size);
            grad.addColorStop(0, `rgba(255,211,106,${alpha})`);
            // Softer inner glow (two stops)
            grad.addColorStop(0.5, `rgba(255,245,160,${alpha * 0.7})`);
            grad.addColorStop(1, 'rgba(255,211,106,0)');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function spawnBurst(container, x, y, opts) {
        // Tiny, short-lived sparkle accent. Uses existing app `.sparkle` style if present.
        for (let i = 0; i < opts.burstCount; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';

            const angle = (i / opts.burstCount) * Math.PI * 2;
            const distance = 14 + Math.random() * 26;
            const ox = Math.cos(angle) * distance;
            const oy = Math.sin(angle) * distance;

            sparkle.style.left = `${x + ox}px`;
            sparkle.style.top = `${y + oy}px`;
            sparkle.style.setProperty('--sparkle-color', ['#FFD700', '#FFA500', '#FFE082', '#FFEB3B', '#FFF59D'][Math.floor(Math.random() * 5)]);
            sparkle.style.zIndex = `${opts.zIndex + 2}`;

            container.appendChild(sparkle);
            setTimeout(() => sparkle.remove(), opts.burstLingerMs);
        }

        // Also add a single bright pop directly at the termination point.
        const pop = document.createElement('div');
        pop.setAttribute('aria-hidden', 'true');
        // Use vmin-based sizing (viewport-relative) to adapt across device sizes/orientations.
        pop.style.cssText = [
            'position: fixed',
            `left: ${x}px`,
            `top: ${y}px`,
            'width: 2.2vmin',
            'height: 2.2vmin',
            'border-radius: 50%',
            'transform: translate(-50%, -50%) scale(0.4)',
            `background: radial-gradient(circle, ${opts.headColor} 0%, rgba(255,255,255,0) 70%)`,
            `box-shadow: 0 0 20px ${opts.glowColor}`,
            `z-index: ${opts.zIndex + 2}`,
            'pointer-events: none',
            'opacity: 0',
            'transition: transform 180ms ease-out, opacity 180ms ease-out',
        ].join(';');
    container.appendChild(pop);

        requestAnimationFrame(() => {
            pop.style.opacity = '1';
            pop.style.transform = 'translate(-50%, -50%) scale(1.2)';
        });

        setTimeout(() => {
            pop.style.opacity = '0';
            pop.style.transform = 'translate(-50%, -50%) scale(0.2)';
            setTimeout(() => pop.remove(), 220);
        }, 220);
    }

    function startFairyDust(opts) {
        console.log('[FairyDust] Starting with opts:', opts);

        // Mark run attempt so loader/system-check code can detect that FX has been kicked off.
        // (If Reduce Motion blocks it, we intentionally leave this false.)
        try { window.__logoFairyDustRunning = true; } catch (_e) {}

        const forced = isForceEnabled();
        const reduced = prefersReducedMotion();

        // Always show *something* even when Reduce Motion is enabled.
        // We respect accessibility by switching to a low-motion profile instead of skipping.
        // Users can still force full FX with ?fx=on.
        if (reduced && !forced) {
            opts = Object.assign({}, opts, {
                // much lighter visual motion + CPU
                durationMs: Math.max(2200, Math.round(opts.durationMs * 0.75)),
                particleIntervalMs: Math.max(28, Math.round(opts.particleIntervalMs * 2.0)),
                trailLifetimeMs: Math.max(700, Math.round(opts.trailLifetimeMs * 0.65)),
                maxParticles: Math.min(70, Math.max(40, Math.round(opts.maxParticles * 0.45))),
                loops: Math.min(1.0, opts.loops),
                wobbleAmp: Math.max(6, Math.round(opts.wobbleAmp * 0.45)),
                wobbleFreq: Math.max(2.0, opts.wobbleFreq * 0.65),
                burstCount: Math.min(6, opts.burstCount),
            });
            console.log('[FairyDust] Reduce Motion detected: using low-motion profile');
            setDebugBadge('Logo FX: running (low-motion profile)', true);
        }
        if (reduced && forced) {
            console.log('[FairyDust] Reduced motion is ON but fx=on override enabled');
            setDebugBadge('Logo FX: forced ON (Reduce Motion override)', true);
        }

        const logo = findLogo(opts.logoSelector);
        console.log('[FairyDust] Logo element:', logo);
        if (!logo) {
            console.warn('[FairyDust] Logo not found with selector:', opts.logoSelector);
            setDebugBadge('Logo FX: logo not found (yet)', false);
            return;
        }

        const container = ensureContainer();
        // Allow callers (like the loader) to force the container above everything.
        if (typeof opts.containerZIndex === 'number' && Number.isFinite(opts.containerZIndex)) {
            try {
                container.style.zIndex = String(opts.containerZIndex);
            } catch (e) {
                // Non-fatal; just ignore.
            }
        }
        console.log('[FairyDust] Container created/found:', container);
        
        const canvas = ensureCanvas(container, opts.zIndex);
        console.log('[FairyDust] Canvas created/found:', canvas);
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('[FairyDust] Could not get 2d context');
            setDebugBadge('Logo FX: canvas 2D context unavailable', false);
            return;
        }
        console.log('[FairyDust] Animation starting...');
        setDebugBadge('Logo FX: running', true);

        let running = true;
        let particles = [];
        let lastSpawnAt = 0;
        let lastPoint = null;
        const startAt = nowMs();

        let cachedDpr = 0;
        let lastW = 0;
        let lastH = 0;

        function ensureCanvasSize() {
            const dpr = window.devicePixelRatio || 1;
            const w = window.innerWidth;
            const h = window.innerHeight;

            if (dpr !== cachedDpr || w !== lastW || h !== lastH) {
                cachedDpr = dpr;
                lastW = w;
                lastH = h;
                resizeCanvas(canvas);
            }
            return cachedDpr;
        }

    const debug = isDebugEnabled();

        function cleanup() {
            running = false;
            particles = [];
            lastPoint = null;
            // Keep canvas around (cheap) but clear it.
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function frame() {
            if (!running) return;

            const ts = nowMs();
            const dpr = ensureCanvasSize();
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

            const tRaw = (ts - startAt) / opts.durationMs;
            const t = clamp(tRaw, 0, 1);
            const eased = easeInOutCubic(t);

            const rect = logo.getBoundingClientRect();
            const p = computePathPoint(rect, eased, opts);

            // Spawn particle(s)
            if (ts - lastSpawnAt >= opts.particleIntervalMs && particles.length < opts.maxParticles) {
                particles.push({
                    bornAt: ts,
                    x: p.x,
                    y: p.y,
                    t: eased,
                    last: lastPoint ? { x: lastPoint.x, y: lastPoint.y } : { x: p.x, y: p.y },
                });
                lastSpawnAt = ts;
            }

            lastPoint = p;

            // Clear
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (debug) {
                // Outline the logo bounds so we can confirm coordinates match what Safari reports.
                ctx.save();
                ctx.globalAlpha = 0.85;
                ctx.lineWidth = 2;
                ctx.strokeStyle = 'rgba(255, 0, 180, 0.85)';
                // Since ctx is scaled by DPR, DOMRect is already in CSS px.
                ctx.strokeRect(rect.left, rect.top, rect.width, rect.height);
                ctx.fillStyle = 'rgba(0, 255, 160, 0.95)';
                ctx.beginPath();
                ctx.arc(p.x, p.y, 7.0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            // Draw particles (oldest first so head renders on top)
            const alive = [];
            for (let i = 0; i < particles.length; i++) {
                const pt = particles[i];
                const age = ts - pt.bornAt;
                const life = age / opts.trailLifetimeMs;
                if (life >= 1) continue;

                // Fade and shrink by age and by global ascent.
                const fadeT = pt.t > opts.fadeStartT ? (1 - (pt.t - opts.fadeStartT) / (1 - opts.fadeStartT)) : 1;
                const alpha = (1 - life) * fadeT;
                // Make the effect more visible on Safari by slightly increasing size.
                // Bigger head at the bottom, smaller near the top; slightly larger when newly born.
                const headSize = lerp(12.0, 4.0, pt.t) * (0.9 + (1 - life) * 0.2);

                ctx.globalAlpha = alpha;
                drawTail(ctx, pt.last, { x: pt.x, y: pt.y }, pt.t, opts);
                drawHead(ctx, pt.x, pt.y, headSize, opts);
                ctx.globalAlpha = 1;

                alive.push(pt);
            }
            particles = alive;

            if (tRaw >= 1) {
                // Termination burst at top of logo.
                const topRect = logo.getBoundingClientRect();
                const end = computePathPoint(topRect, 1, opts);
                spawnBurst(container, end.x, end.y, opts);

                // Let tail linger briefly, then cleanup.
                setTimeout(cleanup, 520);
                return;
            }

            requestAnimationFrame(frame);
        }

        // Handle resizes
        const onResize = () => resizeCanvas(canvas);
        window.addEventListener('resize', onResize);

        // Stop listener after the animation
        setTimeout(() => {
            window.removeEventListener('resize', onResize);
        }, opts.durationMs + 1200);

        requestAnimationFrame(frame);
    }

    function init() {
        console.log('[FairyDust] Initializing...');
        // Expose a tiny API for manual triggering.
        window.BeeSmartLogoFX = window.BeeSmartLogoFX || {};
        window.BeeSmartLogoFX.startFairyDust = function (override = {}) {
            console.log('[FairyDust] Manual trigger called');
            startFairyDust(Object.assign({}, DEFAULTS, override));
        };

        // Back-compat / convenience alias used by templates and loader checks.
        // Keeps the call site simple: window.startLogoFairyDust({ ...overrides })
        window.startLogoFairyDust = function (override = {}) {
            try {
                window.BeeSmartLogoFX.startFairyDust(override);
            } catch (e) {
                console.warn('[FairyDust] startLogoFairyDust failed:', e);
            }
        };

        // Auto-run by default.
        // startFairyDust() already respects Reduce Motion (unless forced), so we can safely
        // initialize here without extra gating.
        // Start as soon as the crest is actually renderable (image loaded + laid out).
        (() => {
            const tryStart = () => {
                const logo = findLogo(DEFAULTS.logoSelector);
                if (logo) {
                    startFairyDust(DEFAULTS);
                    return true;
                }
                return false;
            };

            // Try now
            if (tryStart()) return;

            // If the image exists but hasn't loaded yet, bind to its load event
            try {
                const img = document.querySelector(DEFAULTS.logoSelector);
                if (img && img.tagName === 'IMG') {
                    img.addEventListener('load', () => tryStart(), { once: true });
                }
            } catch (_e) {}

            // Fallback: DOM swaps, delayed layout, or slow loaders
            waitForLogoAndStart(DEFAULTS);
        })();
    }

    if (document.readyState === 'loading') {
        console.log('[FairyDust] Document still loading, waiting for DOMContentLoaded');
        document.addEventListener('DOMContentLoaded', init);
    } else {
        console.log('[FairyDust] Document already loaded, initializing immediately');
        init();
    }
})();
