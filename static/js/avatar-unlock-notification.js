/**
 * Avatar Unlock Notification System
 * Shows celebratory modal when user unlocks new avatars
 */

(function() {
    'use strict';

    /**
     * Show avatar unlock notification
     * @param {Array} unlockedAvatars - Array of newly unlocked avatar objects with name, description, thumbnail
     */
    window.showAvatarUnlockNotification = function(unlockedAvatars) {
        if (!unlockedAvatars || unlockedAvatars.length === 0) {
            return;
        }

        // Take first unlocked avatar (or could show multiple)
        const avatar = unlockedAvatars[0];
        
        console.log('🎉 Showing avatar unlock notification for:', avatar);

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'avatar-unlock-modal';
        modal.innerHTML = `
            <div class="unlock-modal-content">
                <div class="unlock-modal-icon">🎉</div>
                <h1 class="unlock-modal-title">Congratulations!</h1>
                <h2 class="unlock-modal-subtitle">You've Unlocked ${avatar.name}!</h2>
                
                <div class="unlock-modal-avatar-preview">
                    ${avatar.thumbnail ? `<img src="${avatar.thumbnail}" alt="${avatar.name}">` : '<div style="font-size: 100px;">🐝</div>'}
                </div>
                
                <p class="unlock-modal-description">
                    ${avatar.description || `${avatar.name} is now available in your avatar collection!`}
                </p>
                
                <div class="unlock-modal-buttons">
                    <button class="unlock-modal-btn" onclick="window.avatarUnlock.viewAvatar()">
                        🐝 View Avatar
                    </button>
                    <button class="unlock-modal-btn secondary" onclick="window.avatarUnlock.dismiss()">
                        Continue
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add confetti effect (optional)
        createConfetti(modal);

        // Store modal reference and avatar slug for navigation
        window.avatarUnlock = {
            modal: modal,
            avatarSlug: avatar.slug,
            
            viewAvatar: function() {
                // Navigate to avatar picker with selected avatar
                window.location.href = '/honeycomb-picker';
            },
            
            dismiss: function() {
                if (this.modal && this.modal.parentNode) {
                    this.modal.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => {
                        this.modal.remove();
                    }, 300);
                }
            }
        };

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                window.avatarUnlock.dismiss();
            }
        });

        // Optional: Play celebration sound
        try {
            const audio = new Audio('/static/sounds/unlock.mp3');
            audio.volume = 0.5;
            audio.play().catch(err => console.log('Sound play failed:', err));
        } catch (err) {
            // Silently fail if sound not available
        }
    };

    /**
     * Create confetti animation
     */
    function createConfetti(container) {
        const colors = ['#FFD700', '#FFA500', '#FF8C00', '#FFFF00', '#FF6347'];
        const confettiCount = 50;

        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'unlock-confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDelay = Math.random() * 2 + 's';
                confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
                container.appendChild(confetti);

                // Remove after animation
                setTimeout(() => {
                    confetti.remove();
                }, 5000);
            }, i * 30); // Stagger confetti appearance
        }
    }

    /**
     * Check quiz response for newly unlocked avatars
     * Call this after quiz completion
     */
    window.checkForNewlyUnlockedAvatars = function(quizResponse) {
        if (quizResponse && quizResponse.newly_unlocked_avatars && quizResponse.newly_unlocked_avatars.length > 0) {
            // Show notification after a brief delay to let quiz results settle
            setTimeout(() => {
                window.showAvatarUnlockNotification(quizResponse.newly_unlocked_avatars);
            }, 1000);
        }
    };

    console.log('✅ Avatar unlock notification system loaded');

    // Add fadeOut animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
})();
