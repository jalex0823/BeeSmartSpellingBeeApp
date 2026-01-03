/**
 * BeeSmart Avatar & Badge Intro FX Controller
 * Manages GLB avatar loading and intro animations
 * November 30, 2025
 */

class AvatarIntroFX {
    constructor(options = {}) {
        this.options = {
            defaultEffect: 'honey-glow',
            enableParticles: true,
            particleCount: 12,
            autoPlay: true,
            disabled: false,
            randomEffects: false, // Set to true for random effects
            ...options
        };

        this.effects = {
            'honey-glow': this.honeyGlow.bind(this),
            'hex-reveal': this.hexReveal.bind(this),
            'buzz-dust': this.buzzDust.bind(this),
            'wing-sweep': this.wingSweep.bind(this),
            'honey-drip': this.honeyDrip.bind(this),
            'golden-flash': this.goldenFlash.bind(this),
            'portal': this.portal.bind(this),
            'swipe-glow': this.swipeGlow.bind(this),
            'drop-bounce': this.dropBounce.bind(this),
            'shape-morph': this.shapeMorph.bind(this)
        };

        this.effectNames = Object.keys(this.effects);
    }

    /**
     * Get a random effect name
     */
    getRandomEffect() {
        const randomIndex = Math.floor(Math.random() * this.effectNames.length);
        return this.effectNames[randomIndex];
    }

    /**
     * Initialize avatar with intro effect
     * @param {HTMLElement} container - Avatar container element
     * @param {string} effectName - Name of effect to apply (null for random if enabled)
     * @param {Object} customOptions - Effect-specific options
     */
    init(container, effectName = null, customOptions = {}) {
        if (this.options.disabled) {
            return;
        }
        if (!container) {
            console.warn('AvatarIntroFX: No container provided');
            return;
        }

        let effect = effectName;
        
        // Use random effect if enabled and no specific effect requested
        if (!effect && this.options.randomEffects) {
            effect = this.getRandomEffect();
        } else if (!effect) {
            effect = this.options.defaultEffect;
        }

        const effectFunction = this.effects[effect];

        if (!effectFunction) {
            console.warn(`AvatarIntroFX: Unknown effect "${effect}", using default`);
            this.honeyGlow(container, customOptions);
            return;
        }

        effectFunction(container, customOptions);
    }

    /**
     * 1. Honey-Glow Fade Effect
     */
    honeyGlow(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-honey-glow');
        
        // Optional: Add ambient glow div
        if (options.addAmbientGlow) {
            const glow = document.createElement('div');
            glow.className = 'ambient-honey-glow';
            glow.style.cssText = `
                position: absolute;
                inset: -20%;
                background: radial-gradient(circle, rgba(250, 204, 21, 0.3) 0%, transparent 70%);
                pointer-events: none;
                z-index: -1;
                animation: pulseGlow 2s ease-in-out infinite;
            `;
            container.appendChild(glow);
        }
    }

    /**
     * 2. Hex-Pixel Reveal Effect
     */
    hexReveal(container, options = {}) {
        const tileCount = options.tileCount || 24;
        const staggerDelay = options.staggerDelay || 20;

        container.classList.add('avatar-hex-reveal');
        
        // Create hex tile grid overlay
        const tiles = [];
        for (let i = 0; i < tileCount; i++) {
            const tile = document.createElement('div');
            tile.className = 'avatar-hex-tile';
            tile.style.cssText = `
                position: absolute;
                width: ${100 / Math.sqrt(tileCount)}%;
                height: ${100 / Math.sqrt(tileCount)}%;
                top: ${Math.floor(i / Math.sqrt(tileCount)) * (100 / Math.sqrt(tileCount))}%;
                left: ${(i % Math.sqrt(tileCount)) * (100 / Math.sqrt(tileCount))}%;
                clip-path: polygon(50% 0%, 95% 25%, 95% 75%, 50% 100%, 5% 75%, 5% 25%);
                background: rgba(251, 191, 36, 0.1);
                pointer-events: none;
            `;
            tile.style.animationDelay = `${i * staggerDelay}ms`;
            container.appendChild(tile);
            tiles.push(tile);
        }

        // Clean up tiles after animation
        setTimeout(() => {
            tiles.forEach(tile => tile.remove());
        }, 1000 + (tileCount * staggerDelay));
    }

    /**
     * 3. Buzz-Dust Particle Effect
     */
    buzzDust(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-buzz-dust');

        if (!this.options.enableParticles) return;

        const particleCount = options.particleCount || this.options.particleCount;
        const particles = [];

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'buzz-particle';
            
            const angle = (Math.PI * 2 * i) / particleCount;
            const radius = 40 + Math.random() * 20;
            const x = 50 + Math.cos(angle) * radius;
            const y = 50 + Math.sin(angle) * radius;
            
            particle.style.cssText = `
                left: ${x}%;
                top: ${y}%;
            `;
            particle.style.animationDelay = `${i * 60}ms`;
            
            container.appendChild(particle);
            particles.push(particle);
        }

        // Clean up particles
        setTimeout(() => {
            particles.forEach(p => p.remove());
        }, 1500);
    }

    /**
     * 4. Bee-Wing Sweep Effect
     */
    wingSweep(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-wing-sweep');
    }

    /**
     * 5. Honey-Drip Wipe Effect
     */
    honeyDrip(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        container.classList.add('avatar-honey-drip');
        
        const wipe = document.createElement('div');
        wipe.className = 'honey-wipe-overlay';
        container.appendChild(wipe);

        setTimeout(() => wipe.remove(), 1000);
    }

    /**
     * 6. Golden Flash Effect (Premium)
     */
    goldenFlash(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-golden-flash');
    }

    /**
     * 7. Honeycomb Portal Effect
     */
    portal(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-portal');

        // Add rotating honeycomb halo
        const halo = document.createElement('div');
        halo.className = 'honeycomb-halo';
        halo.innerHTML = `
            <svg viewBox="0 0 100 100" style="width: 100%; height: 100%;">
                <defs>
                    <pattern id="honeycomb-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                        <polygon points="10,0 20,6 20,14 10,20 0,14 0,6" 
                                 fill="none" 
                                 stroke="rgba(251, 191, 36, 0.6)" 
                                 stroke-width="0.5"/>
                    </pattern>
                </defs>
                <rect width="100" height="100" fill="url(#honeycomb-pattern)"/>
            </svg>
        `;
        container.appendChild(halo);

        setTimeout(() => halo.remove(), 1200);
    }

    /**
     * 8. Side-Swipe Glow Effect
     */
    swipeGlow(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-swipe-glow');
    }

    /**
     * 9. Soft Drop-In + Bounce Effect
     */
    dropBounce(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-drop-bounce');
    }

    /**
     * 10. Shape-Morph Fade Effect
     */
    shapeMorph(container, options = {}) {
        const avatar = container.querySelector('.avatar-img, canvas, img');
        if (!avatar) return;

        avatar.classList.add('avatar-shape-morph');
    }

    /**
     * Badge intro animations
     */
    badgeIntro(badgeElement, effectType = 'glow-pulse') {
        if (!badgeElement) return;

        const effects = {
            'glow-pulse': 'badge-glow-pulse',
            'spin-in': 'badge-spin-in',
            'collect': 'badge-collect'
        };

        const className = effects[effectType] || effects['glow-pulse'];
        badgeElement.classList.add(className);
    }

    /**
     * Get random badge effect
     */
    getRandomBadgeEffect() {
        const effects = ['glow-pulse', 'spin-in', 'collect'];
        const randomIndex = Math.floor(Math.random() * effects.length);
        return effects[randomIndex];
    }

    /**
     * Apply random effects to all badges
     */
    autoApplyBadges(selector = '.badge-intro', stagger = true) {
        const badges = document.querySelectorAll(selector);
        badges.forEach((badge, index) => {
            const delay = stagger ? index * 150 : 0;
            const randomEffect = this.getRandomBadgeEffect();
            setTimeout(() => {
                this.badgeIntro(badge, randomEffect);
            }, delay);
        });
    }

    /**
     * Combined avatar + badge intro
     */
    avatarBadgeCombo(container, avatarEffect = 'honey-glow', badgeEffect = 'glow-pulse') {
        this.init(container, avatarEffect);

        const badge = container.querySelector('.badge-overlay');
        if (badge) {
            setTimeout(() => {
                this.badgeIntro(badge, badgeEffect);
            }, 500);
        }
    }

    /**
     * Auto-detect and apply effect to all avatars on page
     * @param {string} selector - CSS selector for avatar containers
     * @param {string} effect - Specific effect name (null for random if enabled)
     * @param {boolean} stagger - Whether to stagger animations
     */
    autoApply(selector = '.avatar-fx-container', effect = null, stagger = true) {
        if (this.options.disabled) {
            return;
        }
        const containers = document.querySelectorAll(selector);
        containers.forEach((container, index) => {
            const delay = stagger ? index * 100 : 0;
            setTimeout(() => {
                this.init(container, effect);
            }, delay);
        });
    }

    /**
     * Apply random effects to all avatars
     */
    autoApplyRandom(selector = '.avatar-fx-container', stagger = true) {
        if (this.options.disabled) {
            return;
        }
        const containers = document.querySelectorAll(selector);
        containers.forEach((container, index) => {
            const delay = stagger ? index * 100 : 0;
            const randomEffect = this.getRandomEffect();
            setTimeout(() => {
                this.init(container, randomEffect);
            }, delay);
        });
    }

    /**
     * Get effect based on avatar tier/category
     */
    getEffectForTier(tier) {
        const tierEffects = {
            'free': 'drop-bounce',
            'earn': 'honey-glow',
            'premium': 'golden-flash',
            'mascot': 'portal',
            'special': 'wing-sweep'
        };
        return tierEffects[tier] || 'honey-glow';
    }
}

function __beeSmartShouldDisableIntroFx() {
    try {
        if (window.__beesmartDisableSweepOverlays) return true;
        if (window.__beesmartDisableBackgroundAnimations) return true;
        const de = document.documentElement;
        if (de && (de.classList.contains('beesmart-no-sweep-overlays') || de.classList.contains('beesmart-no-bg-anim'))) return true;
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return true;
    } catch (_e) {}
    return false;
}

const __beeIntroFxDisabled = __beeSmartShouldDisableIntroFx();

// Global instance (keep available for callers, but disable when kill-switch is active)
window.AvatarFX = new AvatarIntroFX({
    randomEffects: !__beeIntroFxDisabled,
    enableParticles: !__beeIntroFxDisabled,
    disabled: __beeIntroFxDisabled
});

// Auto-initialize on DOM ready (skip when disabled)
if (!__beeIntroFxDisabled) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('✨ Avatar Intro FX system ready');

            // Auto-apply random effects to all avatars and badges
            setTimeout(() => {
                window.AvatarFX.autoApplyRandom('.avatar-fx-container', true);
                window.AvatarFX.autoApplyBadges('.badge-intro', true);
            }, 100);
        });
    } else {
        console.log('✨ Avatar Intro FX system ready');

        // Auto-apply random effects to all avatars and badges
        setTimeout(() => {
            window.AvatarFX.autoApplyRandom('.avatar-fx-container', true);
            window.AvatarFX.autoApplyBadges('.badge-intro', true);
        }, 100);
    }
} else {
    console.log('✨ Avatar Intro FX disabled (kill-switch / reduced motion)');
}
