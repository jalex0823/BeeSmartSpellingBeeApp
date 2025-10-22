/**
 * Bee Swarm Animation System
 * Creates animated bees that swarm around the 3D bee hive in the quiz interface
 */

class BeeSwarmAnimation {
    constructor(canvasId = 'beeSwarmCanvas') {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn('🐝 Bee swarm canvas not found');
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.bees = [];
        this.hiveCenter = { x: 0, y: 0 };
        this.hiveRadius = 120;
        this.beeCount = 8; // Number of bees to animate
        this.animationId = null;
        this.isAnimating = false;
        this.time = 0;

        // Initialize canvas size
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());

        // Create bees
        this.createBees();

        // Start animation
        this.startAnimation();

        console.log('🐝 Bee Swarm Animation initialized with', this.beeCount, 'bees');
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        // No fixed hive center - bees will fly around the entire screen
        this.hiveCenter.x = this.canvas.width / 2;
        this.hiveCenter.y = this.canvas.height / 2;
    }

    createBees() {
        this.bees = [];
        for (let i = 0; i < this.beeCount; i++) {
            const angle = (i / this.beeCount) * Math.PI * 2;
            const distance = this.hiveRadius + 30;
            
            this.bees.push({
                id: i,
                x: this.hiveCenter.x + Math.cos(angle) * distance,
                y: this.hiveCenter.y + Math.sin(angle) * distance,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                angle: angle,
                baseRadius: this.hiveRadius + 30 + Math.sin(i) * 40,
                phase: (i / this.beeCount) * Math.PI * 2,
                size: 6 + Math.random() * 2
            });
        }
    }

    drawBee(bee) {
        const x = bee.x;
        const y = bee.y;
        const size = bee.size;

        // Bee body (yellow and black stripes)
        this.ctx.fillStyle = '#FFD700'; // Golden yellow
        this.ctx.beginPath();
        this.ctx.ellipse(x, y, size * 1.5, size, bee.angle, 0, Math.PI * 2);
        this.ctx.fill();

        // Black stripes
        this.ctx.strokeStyle = '#2C1810';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.ellipse(x - size * 0.4, y, size * 0.3, size * 0.8, bee.angle, 0, Math.PI * 2);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.ellipse(x + size * 0.4, y, size * 0.3, size * 0.8, bee.angle, 0, Math.PI * 2);
        this.ctx.stroke();

        // Bee head
        this.ctx.fillStyle = '#FFB300';
        this.ctx.beginPath();
        const headX = x + Math.cos(bee.angle) * size * 1.2;
        const headY = y + Math.sin(bee.angle) * size * 1.2;
        this.ctx.arc(headX, headY, size * 0.7, 0, Math.PI * 2);
        this.ctx.fill();

        // Eyes
        this.ctx.fillStyle = '#000000';
        this.ctx.beginPath();
        this.ctx.arc(headX - size * 0.2, headY - size * 0.2, size * 0.2, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.beginPath();
        this.ctx.arc(headX + size * 0.2, headY - size * 0.2, size * 0.2, 0, Math.PI * 2);
        this.ctx.fill();

        // Wings
        this.ctx.strokeStyle = 'rgba(200, 220, 255, 0.6)';
        this.ctx.lineWidth = 1.5;
        const wingAngle = Math.sin(this.time * 0.05) * 0.3;

        // Left wing
        this.ctx.beginPath();
        const leftWingX = x - size * 0.8;
        const leftWingY = y - size * 0.5;
        this.ctx.moveTo(leftWingX, leftWingY);
        this.ctx.quadraticCurveTo(
            leftWingX - size * 1.5,
            leftWingY - size + wingAngle * 5,
            leftWingX - size * 0.5,
            leftWingY - size * 1.8
        );
        this.ctx.stroke();

        // Right wing
        this.ctx.beginPath();
        const rightWingX = x + size * 0.8;
        const rightWingY = y - size * 0.5;
        this.ctx.moveTo(rightWingX, rightWingY);
        this.ctx.quadraticCurveTo(
            rightWingX + size * 1.5,
            rightWingY - size - wingAngle * 5,
            rightWingX + size * 0.5,
            rightWingY - size * 1.8
        );
        this.ctx.stroke();
    }

    drawHive() {
        const x = this.hiveCenter.x;
        const y = this.hiveCenter.y;
        const size = this.hiveRadius;

        // Hive structure (hexagonal shape)
        this.ctx.fillStyle = 'rgba(139, 90, 43, 0.3)'; // Brown with transparency
        this.ctx.strokeStyle = 'rgba(139, 90, 43, 0.6)';
        this.ctx.lineWidth = 2;

        // Draw hexagon (hive shape)
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2 - Math.PI / 2;
            const px = x + Math.cos(angle) * size;
            const py = y + Math.sin(angle) * size;
            if (i === 0) this.ctx.moveTo(px, py);
            else this.ctx.lineTo(px, py);
        }
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();

        // Inner hexagons (honeycomb detail)
        this.ctx.strokeStyle = 'rgba(255, 200, 100, 0.4)';
        this.ctx.lineWidth = 1;
        for (let i = 0; i < 3; i++) {
            const innerSize = size * (0.6 - i * 0.2);
            this.ctx.beginPath();
            for (let j = 0; j < 6; j++) {
                const angle = (j / 6) * Math.PI * 2 - Math.PI / 2;
                const px = x + Math.cos(angle) * innerSize;
                const py = y + Math.sin(angle) * innerSize;
                if (j === 0) this.ctx.moveTo(px, py);
                else this.ctx.lineTo(px, py);
            }
            this.ctx.closePath();
            this.ctx.stroke();
        }
    }

    updateBeePosition(bee, index) {
        // Bees orbit around the STATIONARY hive center in circular patterns
        const time = this.time * 0.01;
        
        // Each bee has its own orbital radius that varies slightly
        const baseRadius = this.hiveRadius + 50; // Distance from hive center
        const radiusVariation = Math.sin(time * 0.5 + index * 0.5) * 30; // Slight in/out motion
        const radius = baseRadius + radiusVariation;
        
        // Each bee travels at its own speed around the hive
        const speed = 0.3 + (index % 3) * 0.1; // Varying speeds: 0.3, 0.4, 0.5
        const angle = time * speed + (index / this.beeCount) * Math.PI * 2;
        
        // Calculate position orbiting around FIXED hive center
        bee.x = this.hiveCenter.x + Math.cos(angle) * radius;
        bee.y = this.hiveCenter.y + Math.sin(angle) * radius;
        
        // Bee points in direction of travel (tangent to circle)
        bee.angle = angle + Math.PI / 2;

        // Add subtle bobbing motion (up/down)
        bee.y += Math.sin(time * 3 + index) * 8;
    }

    animate = () => {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw STATIC hive in center first
        this.drawHive();

        // Draw bees orbiting around the hive
        for (let i = 0; i < this.bees.length; i++) {
            this.updateBeePosition(this.bees[i], i);
            this.drawBee(this.bees[i]);
        }

        this.time++;

        if (this.isAnimating) {
            this.animationId = requestAnimationFrame(this.animate);
        }
    }

    startAnimation() {
        if (this.isAnimating) return;
        this.isAnimating = true;
        this.animate();
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    pauseAnimation() {
        this.isAnimating = false;
    }

    resumeAnimation() {
        if (!this.isAnimating) {
            this.isAnimating = true;
            this.animate();
        }
    }

    // Pause when user loses focus (tab switch)
    setupVisibilityHandler() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAnimation();
            } else {
                this.resumeAnimation();
            }
        });
    }
}

// Export for use in quiz page
window.BeeSwarmAnimation = BeeSwarmAnimation;
