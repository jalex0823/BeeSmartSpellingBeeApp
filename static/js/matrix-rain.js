/**
 * Matrix Rain Effect - Yellow/Gold Falling Alphabet
 * Creates a falling character animation similar to The Matrix
 * but with yellow/gold colors and alphabet characters
 */

class MatrixRain {
    constructor(canvasId) {
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
        
        // Initialize drop positions
        this.initDrops();
    }
    
    resize() {
        // Detect device type on resize
        this.isMobile = window.innerWidth < 768;
        this.fontSize = this.isMobile ? 12 : 16;
        this.speed = this.isMobile ? 0.5 : 1;
        
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        // Fewer columns on mobile for cleaner effect
        const columnSpacing = this.isMobile ? this.fontSize * 1.5 : this.fontSize;
        this.columns = Math.floor(this.canvas.width / columnSpacing);
        
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
        this.ctx.fillStyle = `rgba(0, 0, 0, ${fadeOpacity})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set font with better rendering for mobile
        this.ctx.font = `bold ${this.fontSize}px 'Courier New', monospace`;
        
        // Calculate column spacing (wider on mobile)
        const columnSpacing = this.isMobile ? this.fontSize * 1.5 : this.fontSize;
        
        // Draw characters
        for (let i = 0; i < this.drops.length; i++) {
            // Random character
            const char = this.characters[Math.floor(Math.random() * this.characters.length)];
            
            // Calculate position with proper spacing
            const x = i * columnSpacing;
            const y = this.drops[i] * this.fontSize;
            
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
            if (y > this.canvas.height && Math.random() > 0.975) {
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
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// Export for use in templates
if (typeof window !== 'undefined') {
    window.MatrixRain = MatrixRain;
}
