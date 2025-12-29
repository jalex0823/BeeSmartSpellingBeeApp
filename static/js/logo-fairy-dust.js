// BeeSmart Logo Fairy Dust Trail: directional dust stream (head + taper tail)
(function () {
    'use strict';

    const DEFAULTS = {
        logoSelector: '.brand-logo.crest-logo, img.crest-logo, img.brand-logo',
        zIndex: 12, // logo is z=10 in unified_menu, so we sit above it
        durationMs: 3200,
        particleIntervalMs: 26,
        trailLifetimeMs: 900,
        maxParticles: 140,
        headColor: '#FFF8C9',
        tailColor: '#FFD36A',
        glowColor: 'rgba(255, 215, 0, 0.65)',
        // Path behavior
        loops: 1.15, // how many times it snakes around
        wobbleAmp: 10,
        wobbleFreq: 6.5,
        // Dissipation
        fadeStartT: 0.72,
        // Sparkle burst
        burstCount: 10,
        burstLingerMs: 520,
    };

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
        if (el && el.getBoundingClientRect) return el;
        return null;
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
            'pointer-events: none',
            'overflow: visible',
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
            `z-index: ${zIndex}`,
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
        grad.addColorStop(0.3, 'rgba(255,255,255,0.85)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();

        ctx.shadowColor = opts.glowColor;
        ctx.shadowBlur = size * 2.2;
        ctx.fillStyle = 'rgba(255,215,0,0.45)';
        ctx.beginPath();
        ctx.arc(x, y, size * 0.62, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    function drawTail(ctx, from, to, t, opts) {
        // Tail is drawn as a series of fading beads behind the head.
        const steps = 9;
        for (let i = 1; i <= steps; i++) {
            const k = i / steps;
            const x = lerp(from.x, to.x, k);
            const y = lerp(from.y, to.y, k);

            const base = 7.8 * (1 - k);
            const size = Math.max(0.8, base * (1 - t * 0.25));

            // Dissipation as we approach the top
            const fadeT = t > opts.fadeStartT ? (1 - (t - opts.fadeStartT) / (1 - opts.fadeStartT)) : 1;
            const alpha = 0.24 * (1 - k) * fadeT;

            const grad = ctx.createRadialGradient(x, y, 0, x, y, size);
            grad.addColorStop(0, `rgba(255,211,106,${alpha})`);
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

            document.body.appendChild(sparkle);
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
        document.body.appendChild(pop);

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
        
        if (prefersReducedMotion()) {
            console.log('[FairyDust] Reduced motion preference detected, skipping');
            return;
        }

        const logo = findLogo(opts.logoSelector);
        console.log('[FairyDust] Logo element:', logo);
        if (!logo) {
            console.warn('[FairyDust] Logo not found with selector:', opts.logoSelector);
            return;
        }

        const container = ensureContainer();
        console.log('[FairyDust] Container created/found:', container);
        
        const canvas = ensureCanvas(container, opts.zIndex);
        console.log('[FairyDust] Canvas created/found:', canvas);
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('[FairyDust] Could not get 2d context');
            return;
        }
        console.log('[FairyDust] Animation starting...');

        let running = true;
        let particles = [];
        let lastSpawnAt = 0;
        let lastPoint = null;
        const startAt = nowMs();

        function cleanup() {
            running = false;
            particles = [];
            lastPoint = null;
            // Keep canvas around (cheap) but clear it.
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function frame() {
            if (!running) return;

            const dpr = resizeCanvas(canvas);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

            const tRaw = (nowMs() - startAt) / opts.durationMs;
            const t = clamp(tRaw, 0, 1);
            const eased = easeInOutCubic(t);

            const rect = logo.getBoundingClientRect();
            const p = computePathPoint(rect, eased, opts);

            // Spawn particle(s)
            const ts = nowMs();
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
                const headSize = lerp(10.5, 5.0, pt.t) * (0.85 + (1 - life) * 0.15);

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

        // Auto-run on pages where the crest logo shows up (safe no-op if not).
        // Delay slightly so `brand-logo-replacer.js` can swap logo src first.
        setTimeout(() => {
            console.log('[FairyDust] Auto-starting after 600ms delay...');
            startFairyDust(DEFAULTS);
        }, 600);
    }

    if (document.readyState === 'loading') {
        console.log('[FairyDust] Document still loading, waiting for DOMContentLoaded');
        document.addEventListener('DOMContentLoaded', init);
    } else {
        console.log('[FairyDust] Document already loaded, initializing immediately');
        init();
    }
})();
