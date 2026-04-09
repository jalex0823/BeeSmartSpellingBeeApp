/**
 * BeeSmart Avatar Theme System
 * Provides unique visual themes and audio cues for each avatar
 * Activates on avatar selection in the honeycomb picker
 */

// Avatar theme definitions with colors, backgrounds, and personality traits
const AVATAR_THEMES = {
    // === CLASSIC BEES ===
    'al-bee': {
        primary: '#FFD700',
        secondary: '#FFA500',
        accent: '#FF8C00',
        bgGradient: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
        borderGlow: '0 0 30px rgba(255, 215, 0, 0.8)',
        personality: 'intelligent',
        soundCue: 'classic-bee.mp3'
    },
    'anxious-bee': {
        primary: '#87CEEB',
        secondary: '#4682B4',
        accent: '#1E90FF',
        bgGradient: 'linear-gradient(135deg, #87CEEB 0%, #4682B4 100%)',
        borderGlow: '0 0 30px rgba(70, 130, 180, 0.8)',
        personality: 'cautious',
        soundCue: 'anxious-bee.mp3'
    },
    'mascot-bee': {
        primary: '#FFD700',
        secondary: '#FF8C00',
        accent: '#FFA500',
        bgGradient: 'linear-gradient(135deg, #FFD700 0%, #FF8C00 50%, #FFA500 100%)',
        borderGlow: '0 0 40px rgba(255, 215, 0, 1)',
        personality: 'friendly',
        soundCue: 'mascot-bee.mp3'
    },
    'monster-bee': {
        primary: '#8B0000',
        secondary: '#FF4500',
        accent: '#FF6347',
        bgGradient: 'linear-gradient(135deg, #8B0000 0%, #FF4500 100%)',
        borderGlow: '0 0 30px rgba(255, 69, 0, 0.8)',
        personality: 'fierce',
        soundCue: 'monster-bee.mp3'
    },
    'professor-bee': {
        primary: '#4169E1',
        secondary: '#1E90FF',
        accent: '#00BFFF',
        bgGradient: 'linear-gradient(135deg, #4169E1 0%, #1E90FF 100%)',
        borderGlow: '0 0 30px rgba(30, 144, 255, 0.8)',
        personality: 'wise',
        soundCue: 'professor-bee.mp3'
    },
    'rocker-bee': {
        primary: '#8B00FF',
        secondary: '#9370DB',
        accent: '#DA70D6',
        bgGradient: 'linear-gradient(135deg, #8B00FF 0%, #9370DB 100%)',
        borderGlow: '0 0 30px rgba(139, 0, 255, 0.8)',
        personality: 'rebellious',
        soundCue: 'rocker-bee.mp3'
    },
    'vamp-bee': {
        primary: '#8B0000',
        secondary: '#DC143C',
        accent: '#FF1493',
        bgGradient: 'linear-gradient(135deg, #000000 0%, #8B0000 50%, #DC143C 100%)',
        borderGlow: '0 0 30px rgba(220, 20, 60, 0.8)',
        personality: 'mysterious',
        soundCue: 'vamp-bee.mp3'
    },
    'ware-bee': {
        primary: '#696969',
        secondary: '#A9A9A9',
        accent: '#C0C0C0',
        bgGradient: 'linear-gradient(135deg, #2F4F4F 0%, #696969 100%)',
        borderGlow: '0 0 30px rgba(105, 105, 105, 0.8)',
        personality: 'wild',
        soundCue: 'ware-bee.mp3'
    },
    'zom-bee': {
        primary: '#556B2F',
        secondary: '#6B8E23',
        accent: '#9ACD32',
        bgGradient: 'linear-gradient(135deg, #2F4F2F 0%, #556B2F 100%)',
        borderGlow: '0 0 30px rgba(107, 142, 35, 0.8)',
        personality: 'undead',
        soundCue: 'zom-bee.mp3'
    },

    // === GLB AVATARS - ADVENTURE & SPECIALTY ===
    'astro-bee': {
        primary: '#000080',
        secondary: '#4169E1',
        accent: '#87CEEB',
        bgGradient: 'linear-gradient(135deg, #000080 0%, #000033 50%, #1E1E3F 100%)',
        borderGlow: '0 0 40px rgba(135, 206, 235, 0.9)',
        personality: 'adventurous',
        soundCue: 'space-bee.mp3'
    },
    'space-bee': {
        primary: '#000080',
        secondary: '#4169E1',
        accent: '#00CED1',
        bgGradient: 'linear-gradient(135deg, #000033 0%, #191970 50%, #4169E1 100%)',
        borderGlow: '0 0 40px rgba(0, 206, 209, 0.9)',
        personality: 'cosmic',
        soundCue: 'space-bee.mp3'
    },
    'brother-bee': {
        primary: '#FF6347',
        secondary: '#FF4500',
        accent: '#FFD700',
        bgGradient: 'linear-gradient(135deg, #FF6347 0%, #FF4500 100%)',
        borderGlow: '0 0 30px rgba(255, 99, 71, 0.8)',
        personality: 'friendly',
        soundCue: 'brother-bee.mp3'
    },
    'builder-bee': {
        primary: '#DAA520',
        secondary: '#B8860B',
        accent: '#FFD700',
        bgGradient: 'linear-gradient(135deg, #D2691E 0%, #DAA520 100%)',
        borderGlow: '0 0 30px rgba(218, 165, 32, 0.8)',
        personality: 'hardworking',
        soundCue: 'builder-bee.mp3'
    },
    'cool-bee': {
        primary: '#00CED1',
        secondary: '#20B2AA',
        accent: '#48D1CC',
        bgGradient: 'linear-gradient(135deg, #00CED1 0%, #20B2AA 100%)',
        borderGlow: '0 0 30px rgba(0, 206, 209, 0.8)',
        personality: 'relaxed',
        soundCue: 'cool-bee.mp3'
    },
    'cutie-bee': {
        primary: '#FFB6C1',
        secondary: '#FF69B4',
        accent: '#FF1493',
        bgGradient: 'linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%)',
        borderGlow: '0 0 30px rgba(255, 105, 180, 0.8)',
        personality: 'adorable',
        soundCue: 'cutie-bee.mp3'
    },
    'detective-bee': {
        primary: '#8B4513',
        secondary: '#A0522D',
        accent: '#D2691E',
        bgGradient: 'linear-gradient(135deg, #654321 0%, #8B4513 100%)',
        borderGlow: '0 0 30px rgba(160, 82, 45, 0.8)',
        personality: 'analytical',
        soundCue: 'detective-bee.mp3'
    },
    'diva-bee': {
        primary: '#FF1493',
        secondary: '#FFD700',
        accent: '#FF69B4',
        bgGradient: 'linear-gradient(135deg, #FF1493 0%, #FFD700 50%, #FF69B4 100%)',
        borderGlow: '0 0 40px rgba(255, 20, 147, 1)',
        personality: 'glamorous',
        soundCue: 'diva-bee.mp3'
    },
    'doctor-bee': {
        primary: '#FFFFFF',
        secondary: '#FF0000',
        accent: '#00CED1',
        bgGradient: 'linear-gradient(135deg, #FFFFFF 0%, #E0FFFF 100%)',
        borderGlow: '0 0 30px rgba(0, 206, 209, 0.8)',
        personality: 'caring',
        soundCue: 'doctor-bee.mp3'
    },
    'explorer-bee': {
        primary: '#87CEEB',
        secondary: '#4682B4',
        accent: '#5F9EA0',
        bgGradient: 'linear-gradient(135deg, #87CEEB 0%, #4682B4 50%, #5F9EA0 100%)',
        borderGlow: '0 0 40px rgba(135, 206, 235, 0.9)',
        personality: 'adventurous',
        soundCue: 'explorer-bee.mp3'
    },
    'franken-bee': {
        primary: '#228B22',
        secondary: '#32CD32',
        accent: '#ADFF2F',
        bgGradient: 'linear-gradient(135deg, #2F4F2F 0%, #228B22 100%)',
        borderGlow: '0 0 30px rgba(34, 139, 34, 0.8)',
        personality: 'quirky',
        soundCue: 'franken-bee.mp3'
    },
    'inventor-bee': {
        primary: '#FFB74D',
        secondary: '#FFA726',
        accent: '#FF9800',
        bgGradient: 'linear-gradient(135deg, #FFE082 0%, #FFB74D 100%)',
        borderGlow: '0 0 35px rgba(255, 152, 0, 0.9)',
        personality: 'innovative',
        soundCue: 'inventor-bee.mp3'
    },
    'knight-bee': {
        primary: '#4682B4',
        secondary: '#708090',
        accent: '#B0C4DE',
        bgGradient: 'linear-gradient(135deg, #2F4F4F 0%, #4682B4 50%, #708090 100%)',
        borderGlow: '0 0 40px rgba(70, 130, 180, 0.9)',
        personality: 'brave',
        soundCue: 'knight-bee.mp3'
    },
    'motorcycle-bee': {
        primary: '#FF4500',
        secondary: '#FF6347',
        accent: '#FFD700',
        bgGradient: 'linear-gradient(135deg, #000000 0%, #FF4500 100%)',
        borderGlow: '0 0 30px rgba(255, 69, 0, 0.8)',
        personality: 'daring',
        soundCue: 'motorcycle-bee.mp3'
    },
    'queen-bee': {
        primary: '#FFD700',
        secondary: '#FF1493',
        accent: '#DA70D6',
        bgGradient: 'linear-gradient(135deg, #FFD700 0%, #FF1493 50%, #DA70D6 100%)',
        borderGlow: '0 0 50px rgba(255, 215, 0, 1)',
        personality: 'regal',
        soundCue: 'queen-bee.mp3'
    },
    'robo-bee': {
        primary: '#708090',
        secondary: '#4682B4',
        accent: '#00CED1',
        bgGradient: 'linear-gradient(135deg, #2F4F4F 0%, #708090 100%)',
        borderGlow: '0 0 30px rgba(0, 206, 209, 0.8)',
        personality: 'mechanical',
        soundCue: 'robo-bee.mp3'
    },
    'sea-bee': {
        primary: '#1E90FF',
        secondary: '#00BFFF',
        accent: '#87CEEB',
        bgGradient: 'linear-gradient(135deg, #006994 0%, #1E90FF 50%, #00BFFF 100%)',
        borderGlow: '0 0 30px rgba(0, 191, 255, 0.8)',
        personality: 'aquatic',
        soundCue: 'sea-bee.mp3'
    },
    'super-bee': {
        primary: '#FF0000',
        secondary: '#FFD700',
        accent: '#0000FF',
        bgGradient: 'linear-gradient(135deg, #FF0000 0%, #FFD700 50%, #0000FF 100%)',
        borderGlow: '0 0 50px rgba(255, 0, 0, 1)',
        personality: 'heroic',
        soundCue: 'super-bee.mp3'
    },
    'obee': {
        primary: '#228B22',
        secondary: '#32CD32',
        accent: '#FFD700',
        bgGradient: 'linear-gradient(135deg, #006400 0%, #228B22 100%)',
        borderGlow: '0 0 30px rgba(34, 139, 34, 0.8)',
        personality: 'irish',
        soundCue: 'obee.mp3'
    }
};

// Add themes for new GLB avatars to ensure consistent styling
AVATAR_THEMES['buda-bee'] = {
    primary: '#DAA520',
    secondary: '#B8860B',
    accent: '#FFD700',
    bgGradient: 'linear-gradient(135deg, #F6E27A 0%, #DAA520 100%)',
    borderGlow: '0 0 40px rgba(255, 215, 0, 1)',
    personality: 'zen'
};

AVATAR_THEMES['jrock-bee'] = {
    primary: '#8B00FF',
    secondary: '#000000',
    accent: '#FFD700',
    bgGradient: 'linear-gradient(135deg, #0f0f0f 0%, #4b0082 100%)',
    borderGlow: '0 0 40px rgba(139, 0, 255, 0.9)',
    personality: 'rockstar'
};

AVATAR_THEMES['lumberjack-bee'] = {
    primary: '#8B4513',
    secondary: '#228B22',
    accent: '#FFD700',
    bgGradient: 'linear-gradient(135deg, #3B1F0A 0%, #228B22 60%, #8B4513 100%)',
    borderGlow: '0 0 40px rgba(139, 69, 19, 0.8)',
    personality: 'rugged',
    soundCue: 'mascot-bee.mp3'
};

// Avatar Theme Manager Class
class AvatarThemeManager {
    constructor() {
        this.currentTheme = null;
        this.currentAvatarSlug = null;
        this.themeTransitionDuration = 500; // ms
        this.audioContext = null;
        this.soundEffects = {};
        
        // Initialize audio context (for future sound implementation)
        this.initAudio();
    }

    /**
     * Initialize Web Audio API context
     */
    initAudio() {
        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
            console.log('🔊 Audio context initialized for avatar themes');
        } catch (e) {
            console.warn('⚠️ Web Audio API not available:', e);
        }
    }

    /**
     * Get theme configuration for an avatar
     */
    getTheme(avatarSlug) {
        const theme = AVATAR_THEMES[avatarSlug];
        if (!theme) {
            console.warn(`⚠️ No theme found for ${avatarSlug}, using default`);
            return AVATAR_THEMES['mascot-bee']; // Default fallback
        }
        return theme;
    }

    /**
     * Activate theme for selected avatar
     */
    activateTheme(avatarSlug, targetElement = null) {
        console.log(`🎨 Activating theme for: ${avatarSlug}`);
        
        const theme = this.getTheme(avatarSlug);
        this.currentTheme = theme;
        this.currentAvatarSlug = avatarSlug;

        // Apply theme to target element (the clicked avatar card)
        if (targetElement) {
            this.applyThemeToElement(targetElement, theme);
        }

        // Apply theme to preview panel
        this.applyThemeToPreviewPanel(theme);

        // Apply global theme effects
        this.applyGlobalTheme(theme);

        // Play sound cue (if available)
        this.playSoundCue(theme.soundCue);

        // Dispatch custom event for other systems to react
        window.dispatchEvent(new CustomEvent('avatarThemeActivated', {
            detail: { slug: avatarSlug, theme: theme }
        }));

        return theme;
    }

    /**
     * Apply theme styles to specific element (avatar card)
     */
    applyThemeToElement(element, theme) {
        // Animate the selection with theme colors
        element.style.transition = `all ${this.themeTransitionDuration}ms ease-out`;
        element.style.boxShadow = theme.borderGlow;
        element.style.borderColor = theme.primary;
        
        // Add pulsing animation
        element.style.animation = 'theme-pulse 2s infinite';
    }

    /**
     * Apply theme to preview panel
     */
    applyThemeToPreviewPanel(theme) {
        const previewPanel = document.querySelector('.avatar-preview-panel');
        if (!previewPanel) return;

        previewPanel.style.transition = `all ${this.themeTransitionDuration}ms ease-out`;
        previewPanel.style.background = theme.bgGradient;
        previewPanel.style.boxShadow = `inset ${theme.borderGlow}, ${theme.borderGlow}`;

        // Update text colors for contrast
        const previewName = previewPanel.querySelector('.preview-name');
        const previewDesc = previewPanel.querySelector('.preview-description');
        
        if (previewName) {
            previewName.style.color = theme.primary;
            previewName.style.textShadow = `0 0 20px ${theme.primary}`;
        }
        
        if (previewDesc) {
            previewDesc.style.color = theme.secondary;
        }

        // Update button with theme colors
        const chooseBtn = previewPanel.querySelector('.preview-choose-btn');
        if (chooseBtn) {
            chooseBtn.style.background = theme.bgGradient;
            chooseBtn.style.borderColor = theme.primary;
            chooseBtn.style.boxShadow = theme.borderGlow;
        }
    }

    /**
     * Apply global theme effects (subtle background influence)
     */
    applyGlobalTheme(theme) {
        const body = document.body;
        
        // Create a subtle overlay with theme colors
        let themeOverlay = document.getElementById('avatar-theme-overlay');
        if (!themeOverlay) {
            themeOverlay = document.createElement('div');
            themeOverlay.id = 'avatar-theme-overlay';
            themeOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1;
                transition: opacity ${this.themeTransitionDuration}ms ease-out;
                opacity: 0;
            `;
            body.appendChild(themeOverlay);
        }

        // Apply theme gradient with low opacity
        themeOverlay.style.background = theme.bgGradient;
        themeOverlay.style.opacity = '0.1';
    }

    /**
     * Play sound cue for avatar selection (placeholder for future implementation)
     */
    playSoundCue(soundFile) {
        // TODO: Implement actual audio playback
        // For now, just log
        console.log(`🔊 Playing sound: ${soundFile}`);
        
        // Future implementation:
        // - Load sound file
        // - Play through Web Audio API
        // - Apply audio effects based on personality
    }

    /**
     * Clear current theme
     */
    clearTheme() {
        const themeOverlay = document.getElementById('avatar-theme-overlay');
        if (themeOverlay) {
            themeOverlay.style.opacity = '0';
        }

        // Clear preview panel theme
        const previewPanel = document.querySelector('.avatar-preview-panel');
        if (previewPanel) {
            previewPanel.style.background = '';
            previewPanel.style.boxShadow = '';
        }

        this.currentTheme = null;
        this.currentAvatarSlug = null;
    }

    /**
     * Get personality trait for avatar
     */
    getPersonality(avatarSlug) {
        const theme = this.getTheme(avatarSlug);
        return theme.personality || 'friendly';
    }

    /**
     * Generate personality-based message
     */
    getPersonalityMessage(avatarSlug, messageType = 'greeting') {
        const personality = this.getPersonality(avatarSlug);
        
        const messages = {
            greeting: {
                intelligent: "Greetings! Ready to expand your vocabulary? 📚",
                cautious: "Um... hello! Let's spell carefully together... 😊",
                friendly: "Hey there, friend! Let's have fun spelling! 🐝",
                fierce: "Let's crush these words! 💪",
                wise: "Welcome, young scholar. Knowledge awaits! 🎓",
                rebellious: "Let's rock and spell! 🎸",
                mysterious: "Welcome to the spelling night... 🌙",
                wild: "Arooo! Time to hunt down some words! 🐺",
                undead: "Braaaains... I mean... spelling! 🧟",
                adventurous: "Adventure awaits! Let's explore words! 🚀",
                cosmic: "Prepare for lift-off to spelling success! 🚀",
                hardworking: "Let's build your spelling skills! 🔨",
                relaxed: "Chill out and spell, dude! 😎",
                adorable: "You're so cute! Let's spell together! 💕",
                analytical: "Let's investigate these words! 🔍",
                glamorous: "Fabulous! Let's spell with style! ✨",
                caring: "Take care of your spelling health! 🏥",
                quirky: "It's alive! Let's spell! ⚡",
                brave: "For honor and spelling! ⚔️",
                daring: "Rev up for some spelling action! 🏍️",
                regal: "Your Majesty, let's spell royally! 👑",
                mechanical: "System initialized. Spelling mode activated. 🤖",
                aquatic: "Dive deep into spelling! 🌊",
                heroic: "With great spelling comes great responsibility! 🦸",
                irish: "Top o' the mornin'! Let's spell! 🍀",
                rugged: "Timber! Let's chop through these words! 🪓"
            }
        };

        return messages[messageType][personality] || messages[messageType]['friendly'];
    }
}

// Create global instance
window.avatarThemeManager = new AvatarThemeManager();

// Add CSS animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes theme-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    .avatar-hex-position.theme-active {
        animation: theme-pulse 2s infinite;
    }

    /* Smooth theme transitions */
    .avatar-preview-panel,
    .preview-choose-btn {
        transition: all 500ms ease-out;
    }
`;
document.head.appendChild(styleSheet);

console.log('✅ Avatar Theme System initialized with', Object.keys(AVATAR_THEMES).length, 'themes');
