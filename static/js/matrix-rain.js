/**
 * Matrix Rain Effect - Yellow/Gold Falling Alphabet
 * Creates a falling character animation similar to The Matrix
 * but with yellow/gold colors and alphabet characters
 */

class MatrixRain {
    constructor(canvasId) {
        // Respect explicit global kill-switches used by the app to avoid jank.
        // IMPORTANT: Do not infer-disable just because we're on iOS/mobile;
        // this effect is intentionally enabled for iOS Safari and iOS app WebViews.
        try {
            const de = document.documentElement;
            // NOTE: "sweep overlays" are a separate effect family.
            // Disabling sweep overlays MUST NOT disable Matrix Rain; we want Matrix Rain
            // to keep running during the loader even when sweep overlays are off.
            // This flag is still read here as an explicit app-level switch, but it is
            // intentionally NOT treated as a Matrix Rain disable by itself.
            const _sweepOverlaysDisabled = !!(window.__beesmartDisableSweepOverlays);
            const disabled = !!(window.__beesmartDisableBackgroundAnimations)
                || (de && de.classList && de.classList.contains('beesmart-no-bg-anim'))
                || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
            if (disabled) {
                this.disabled = true;
                this.start = function(){ /* disabled */ };
                this.stop = function(){ /* disabled */ };
                this.clear = function(){ /* disabled */ };
                return;
            }
        } catch (_e) {
            // ignore
        }

        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Matrix canvas not found:', canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
        
        // Responsive font size based on device width
        this.isMobile = window.innerWidth < 768;
        this.fontSize = this.isMobile ? 12 : 16;
        
        this.columns = 0;
        this.drops = [];
        this.animationId = null;
        this.speed = this.isMobile ? 0.5 : 1; // Slower on mobile for better visibility
        
        this.init();
    }
    
    init() {
        // Set canvas to full window size
        this.resize();
        window.addEventListener('resize', () => this.resize());
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => this.resize());
            window.visualViewport.addEventListener('scroll', () => this.resize());
        }
        
        // Initialize drop positions
        this.initDrops();
    }
    
    resize() {
        // Detect device type on resize
        this.isMobile = window.innerWidth < 768;
        this.fontSize = this.isMobile ? 12 : 16;
        this.speed = this.isMobile ? 0.5 : 1;
        
        // Get device pixel ratio for crisp rendering
        const dpr = window.devicePixelRatio || 1;
        
        // Use full viewport - prefer visualViewport on mobile for correct height when chrome shows/hides
        const vp = window.visualViewport;
        const w = vp ? vp.width : window.innerWidth;
        const h = Math.max(
            vp ? vp.height : window.innerHeight,
            document.documentElement.clientHeight || window.innerHeight
        );
        
        // Set actual canvas size (accounting for high DPI displays)
        this.canvas.width = w * dpr;
        this.canvas.height = h * dpr;
        
        // Scale canvas back to CSS size
        this.canvas.style.width = w + 'px';
        this.canvas.style.height = h + 'px';
        
        // Scale context to match device pixel ratio
        this.ctx.scale(dpr, dpr);
        
        // Wider column spacing on mobile to prevent overlap (per MATRIX_RAIN_MOBILE_FIX.md)
        const columnSpacing = this.isMobile ? this.fontSize * 2 : this.fontSize;
        this.columns = Math.floor(w / columnSpacing);
        
        this.initDrops();
    }
    
    initDrops() {
        this.drops = [];
        for (let i = 0; i < this.columns; i++) {
            // Start at random positions for more natural effect
            this.drops[i] = Math.random() * -100;
        }
    }
    
    draw() {
        // Slightly more opaque fade on mobile for better trail visibility
        const fadeOpacity = this.isMobile ? 0.04 : 0.02;
        const vp = window.visualViewport;
        const w = vp ? vp.width : window.innerWidth;
        const h = Math.max(vp ? vp.height : window.innerHeight, document.documentElement.clientHeight || window.innerHeight);
        this.ctx.fillStyle = `rgba(0, 0, 0, ${fadeOpacity})`;
        this.ctx.fillRect(0, 0, w, h);
        
        // Set font with better rendering for mobile
        this.ctx.font = `bold ${this.fontSize}px 'Courier New', monospace`;
        this.ctx.textBaseline = 'top'; // Consistent text alignment
        
        // Calculate column spacing (wider on mobile to prevent overlap)
        const columnSpacing = this.isMobile ? this.fontSize * 2 : this.fontSize;
        
        // Draw characters
        for (let i = 0; i < this.drops.length; i++) {
            // Random character
            const char = this.characters[Math.floor(Math.random() * this.characters.length)];
            
            // Calculate position with proper spacing and alignment
            const x = Math.floor(i * columnSpacing + columnSpacing / 2);
            const y = Math.floor(this.drops[i] * this.fontSize);
            
            // Enhanced brightness gradient for mobile visibility
            const brightThreshold = this.isMobile ? 0.95 : 0.975;
            const midThreshold = this.isMobile ? 0.85 : 0.95;
            
            // Brightest characters at the head
            if (Math.random() > brightThreshold) {
                this.ctx.fillStyle = '#FFFF00'; // Bright yellow
                this.ctx.shadowColor = '#FFD700';
                this.ctx.shadowBlur = this.isMobile ? 4 : 2;
            } else if (Math.random() > midThreshold) {
                this.ctx.fillStyle = '#FFD700'; // Gold
                this.ctx.shadowBlur = 0;
            } else {
                this.ctx.fillStyle = '#DAA520'; // Goldenrod
                this.ctx.shadowBlur = 0;
            }
            
            // Draw character
            this.ctx.fillText(char, x, y);
            
            // Reset shadow for next character
            this.ctx.shadowBlur = 0;
            
            // Reset drop to top when it reaches bottom
            const h = Math.max((window.visualViewport && window.visualViewport.height) || window.innerHeight, document.documentElement.clientHeight || window.innerHeight);
            if (y > h && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            // Move drop down at appropriate speed
            this.drops[i] += this.speed;
        }
    }
    
    start() {
        if (this.animationId) return; // Already running
        
        const animate = () => {
            this.draw();
            this.animationId = requestAnimationFrame(animate);
        };
        
        animate();
        console.log('🌧️ Matrix rain started');
    }
    
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
            console.log('🛑 Matrix rain stopped');
        }
    }
    
    clear() {
        const w = (window.visualViewport && window.visualViewport.width) || window.innerWidth;
        const h = Math.max((window.visualViewport && window.visualViewport.height) || window.innerHeight, document.documentElement.clientHeight || window.innerHeight);
        this.ctx.clearRect(0, 0, w, h);
    }
}

// Export for use in templates
if (typeof window !== 'undefined') {
    window.MatrixRain = MatrixRain;
}
