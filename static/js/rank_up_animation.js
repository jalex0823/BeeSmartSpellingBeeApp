/**
 * Buzz Dust Rank-Up Animation System
 * Displays celebratory animation when user achieves a new Bee Class rank
 */

class RankUpAnimator {
    constructor() {
        this.isAnimating = false;
        this.animationDuration = 2000; // 2 seconds
    }

    /**
     * Trigger rank-up animation
     * @param {Object} oldClass - Previous bee class {id, label, emoji}
     * @param {Object} newClass - New bee class {id, label, emoji}
     * @param {number} totalBuzzDust - User's total Buzz Dust
     */
    trigger(oldClass, newClass, totalBuzzDust) {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        
        // Create overlay
        const overlay = this.createOverlay();
        document.body.appendChild(overlay);
        
        // Animate in
        requestAnimationFrame(() => {
            overlay.classList.add('active');
            this.playAnimation(overlay, oldClass, newClass, totalBuzzDust);
        });
        
        // Auto-dismiss after animation
        setTimeout(() => {
            this.dismiss(overlay);
        }, this.animationDuration);
    }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'rank-up-overlay';
        overlay.innerHTML = `
            <div class="rank-up-container">
                <div class="rank-up-header">
                    <div class="sparkle-burst"></div>
                    <h1 class="rank-up-title">RANK UP!</h1>
                </div>
                
                <div class=\"rank-transition\">
                    <div class=\"old-rank slide-out-left\">
                        <img class=\"rank-badge-img\" src=\"\" alt=\"\" style=\"display:none;\">
                        <span class=\"rank-emoji\"></span>
                        <span class=\"rank-label\"></span>
                    </div>
                    
                    <div class=\"rank-arrow\">→</div>
                    
                    <div class=\"new-rank slide-in-right\">
                        <img class=\"rank-badge-img\" src=\"\" alt=\"\" style=\"display:none;\">
                        <span class=\"rank-emoji\"></span>
                        <span class=\"rank-label\"></span>
                    </div>
                </div>
                
                <div class="rank-description"></div>
                
                <div class="buzz-dust-display">
                    <span class="dust-icon">✨</span>
                    <span class="dust-amount"></span>
                    <span class="dust-label">Total Buzz Dust</span>
                </div>
                
                <button class="dismiss-button">Continue</button>
            </div>
        `;
        
        // Click to dismiss
        overlay.querySelector('.dismiss-button').addEventListener('click', () => {
            this.dismiss(overlay);
        });
        
        return overlay;
    }

    playAnimation(overlay, oldClass, newClass, totalBuzzDust) {
        // Populate old rank
        const oldRankEl = overlay.querySelector('.old-rank');
        const oldBadgeImg = oldRankEl.querySelector('.rank-badge-img');
        const oldEmoji = oldRankEl.querySelector('.rank-emoji');
        
        if (oldClass.badge_image) {
            oldBadgeImg.src = `/static/assets/badges/${oldClass.badge_image}`;
            oldBadgeImg.alt = oldClass.label;
            oldBadgeImg.style.display = 'block';
            oldEmoji.style.display = 'none';
        } else {
            oldEmoji.textContent = oldClass.emoji;
            oldBadgeImg.style.display = 'none';
            oldEmoji.style.display = 'block';
        }
        oldRankEl.querySelector('.rank-label').textContent = oldClass.label;
        
        // Populate new rank
        const newRankEl = overlay.querySelector('.new-rank');
        const newBadgeImg = newRankEl.querySelector('.rank-badge-img');
        const newEmoji = newRankEl.querySelector('.rank-emoji');
        
        if (newClass.badge_image) {
            newBadgeImg.src = `/static/assets/badges/${newClass.badge_image}`;
            newBadgeImg.alt = newClass.label;
            newBadgeImg.style.display = 'block';
            newEmoji.style.display = 'none';
        } else {
            newEmoji.textContent = newClass.emoji;
            newBadgeImg.style.display = 'none';
            newEmoji.style.display = 'block';
        }
        newRankEl.querySelector('.rank-label').textContent = newClass.label;
        
        // Description
        const description = overlay.querySelector('.rank-description');
        description.textContent = `You are now ${newClass.label.includes('a') ? 'an' : 'a'} ${newClass.label}! ${newClass.description || 'Keep collecting Buzz Dust!'}`;
        
        // Buzz Dust
        overlay.querySelector('.dust-amount').textContent = totalBuzzDust.toLocaleString();
        
        // Trigger animations
        setTimeout(() => {
            oldRankEl.style.opacity = '0';
            oldRankEl.style.transform = 'translateX(-100px)';
        }, 300);
        
        setTimeout(() => {
            newRankEl.style.opacity = '1';
            newRankEl.style.transform = 'translateX(0) scale(1.2)';
            this.createSparkles(overlay.querySelector('.new-rank'));
        }, 600);
        
        setTimeout(() => {
            newRankEl.style.transform = 'translateX(0) scale(1)';
        }, 1000);
    }

    createSparkles(container) {
        for (let i = 0; i < 20; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.style.left = `${Math.random() * 100}%`;
            sparkle.style.top = `${Math.random() * 100}%`;
            sparkle.style.animationDelay = `${Math.random() * 0.5}s`;
            container.appendChild(sparkle);
            
            setTimeout(() => sparkle.remove(), 1500);
        }
    }

    dismiss(overlay) {
        overlay.classList.remove('active');
        overlay.classList.add('dismissing');
        
        setTimeout(() => {
            overlay.remove();
            this.isAnimating = false;
        }, 300);
    }
}

// Global instance
window.rankUpAnimator = new RankUpAnimator();

/**
 * Helper function to check for rank-up after quiz
 * Call this from quiz results page
 */
function checkForRankUp() {
    fetch('/api/check-rank-up', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.ranked_up) {
            window.rankUpAnimator.trigger(
                data.old_class,
                data.new_class,
                data.total_buzz_dust
            );
        }
    })
    .catch(error => {
        console.error('Error checking rank-up:', error);
    });
}

// Auto-check on page load if flag is set
document.addEventListener('DOMContentLoaded', () => {
    const checkRankUp = document.body.dataset.checkRankUp;
    if (checkRankUp === 'true') {
        setTimeout(checkForRankUp, 500);
    }
});
