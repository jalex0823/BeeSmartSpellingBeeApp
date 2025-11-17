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
        this.fontSize = 16;
        this.columns = 0;
        this.drops = [];
        this.animationId = null;
        
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
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
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
        // Very transparent background for fade effect - allows honeycomb to show through
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.02)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set font
        this.ctx.font = `${this.fontSize}px 'Courier New', monospace`;
        
        // Draw characters
        for (let i = 0; i < this.drops.length; i++) {
            // Random character
            const char = this.characters[Math.floor(Math.random() * this.characters.length)];
            
            // Create gradient from bright gold to darker gold
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            // Brightest characters at the head
            if (Math.random() > 0.975) {
                this.ctx.fillStyle = '#FFFF00'; // Bright yellow
            } else if (Math.random() > 0.95) {
                this.ctx.fillStyle = '#FFD700'; // Gold
            } else {
                this.ctx.fillStyle = '#DAA520'; // Goldenrod
            }
            
            // Draw character
            this.ctx.fillText(char, x, y);
            
            // Reset drop to top when it reaches bottom
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            // Move drop down
            this.drops[i]++;
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
