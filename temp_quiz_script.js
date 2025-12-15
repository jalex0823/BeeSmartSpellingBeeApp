console.log('✅ Quiz script loading - Dec 13, 2025 @ 6:15pm - VISUALIZATION REMOVED');

// ⚠️ CRITICAL: Define core classes FIRST before any other code
// This ensures they're available even if other code fails

// 🎭 MorphController class REMOVED (was causing JavaScript errors)
// Using simplified CountdownTimer only

// ⏱️ Countdown Timer Class (formerly HoneyJarTimer)
class CountdownTimer {
    constructor(config = {}) {
        this.duration = config.duration || 30000; // Default 30 seconds
        this.onTick = config.onTick || (() => {});
        this.onComplete = config.onComplete || (() => {});
        this.onWarning = config.onWarning || (() => {}); // Callback when < 10s left
        
        this.startTime = null;
        this.remaining = this.duration;
        this.running = false;
        this.intervalId = null;
        this.warningTriggered = false;
    }
    
    start() {
        if (this.running) return;
        
        this.startTime = Date.now();
        this.running = true;
        this.warningTriggered = false;
        
        this.intervalId = setInterval(() => {
            const elapsed = Date.now() - this.startTime;
            this.remaining = Math.max(0, this.duration - elapsed);
            
            // Trigger warning callback when < 10 seconds
            if (!this.warningTriggered && this.remaining < 10000) {
                this.warningTriggered = true;
                this.onWarning(this.remaining);
            }
            
            this.onTick(this.remaining);
            
            if (this.remaining === 0) {
                this.stop();
                this.onComplete();
            }
        }, 100); // Update every 100ms for smooth countdown
    }
    
    stop() {
        this.running = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    reset(newDuration) {
        this.stop();
        if (newDuration !== undefined) {
            this.duration = newDuration;
        }
        this.remaining = this.duration;
        this.warningTriggered = false;
    }
    
    getRemaining() {
        return this.remaining;
    }
    
    isRunning() {
        return this.running;
    }
}

// ✅ Register classes on window for global access
window.CountdownTimer = CountdownTimer;

console.log('✅ Core classes registered:', {
    CountdownTimer: typeof window.CountdownTimer !== 'undefined'
});

// Note: QuizManager will be registered later in this script after its definition

// Frontend safety blanker - hide target word if it appears in definitions/sentences
function hideTargetWord(text, word) {
    if (!text || !word) return text || '';
    const esc = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return text.replace(new RegExp(`\\b${esc}\\b`, 'gi'), '_____');
}

class BeeSoundboard {
    constructor() {
        this.supported = typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
        this.ctx = null;
        this.unlocked = false;
        this.cachedVoice = null; // Cache voice for consistency
        this.setupUnlock();
    }

    setupUnlock() {
        if (!this.supported || this.unlocked) {
            return;
        }

        const unlock = () => {
            if (!this.supported) {
                return;
            }
            const Ctx = window.AudioContext || window.webkitAudioContext;
            if (!this.ctx && Ctx) {
                this.ctx = new Ctx();
            }
            if (this.ctx && this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
            this.unlocked = true;
            document.removeEventListener('pointerdown', unlock, true);
            document.removeEventListener('keydown', unlock, true);
        };

        document.addEventListener('pointerdown', unlock, true);
        document.addEventListener('keydown', unlock, true);
    }

    play(type) {
        if (!this.supported || !this.ctx || !this.unlocked) {
            return;
        }

        switch (type) {
            case 'correct':
                this.sequence([
                    { freq: 660, duration: 0.16, gain: 0.18, wave: 'sine', fade: true },
                    { freq: 880, duration: 0.2, gain: 0.16, wave: 'triangle', fade: true, delay: 0.12 },
                    { freq: 990, duration: 0.22, gain: 0.12, wave: 'sine', fade: true, delay: 0.14 }
                ]);
                break;
            case 'incorrect':
                this.sequence([
                    { freq: 220, duration: 0.24, gain: 0.22, wave: 'sawtooth', slide: 150, fade: true },
                    { freq: 180, duration: 0.18, gain: 0.15, wave: 'triangle', fade: true, delay: 0.08 }
                ]);
                break;
            case 'skip':
                this.sequence([
                    { freq: 320, duration: 0.16, gain: 0.14, wave: 'triangle', fade: true },
                    { freq: 260, duration: 0.18, gain: 0.12, wave: 'sine', fade: true, delay: 0.08 }
                ]);
                break;
            case 'speak':
                this.sequence([
                    { freq: 480, duration: 0.14, gain: 0.12, wave: 'sine', fade: true },
                    { freq: 720, duration: 0.18, gain: 0.1, wave: 'triangle', fade: true, delay: 0.1 }
                ]);
                break;
            case 'button-hover':
                this.sequence([
                    { freq: 600, duration: 0.08, gain: 0.08, wave: 'sine', fade: true }
                ]);
                break;
            case 'button-click':
                this.sequence([
                    { freq: 800, duration: 0.06, gain: 0.1, wave: 'triangle', fade: true },
                    { freq: 1000, duration: 0.08, gain: 0.08, wave: 'sine', fade: true, delay: 0.02 }
                ]);
                break;
            case 'button-primary':
                this.sequence([
                    { freq: 880, duration: 0.1, gain: 0.12, wave: 'triangle', fade: true },
                    { freq: 1320, duration: 0.12, gain: 0.1, wave: 'sine', fade: true, delay: 0.05 }
                ]);
                break;
            case 'buzz-hover':
                // Quick buzz sound on hover
                this.sequence([
                    { freq: 220, duration: 0.05, gain: 0.08, wave: 'sawtooth', fade: true }
                ]);
                break;
            case 'buzz-click':
                // Satisfying buzz click
                this.sequence([
                    { freq: 440, duration: 0.08, gain: 0.15, wave: 'triangle', fade: true },
                    { freq: 550, duration: 0.06, gain: 0.12, wave: 'sine', fade: true, delay: 0.04 }
                ]);
                break;
            case 'honey-collect':
                // Sweet honey collection sound
                this.sequence([
                    { freq: 660, duration: 0.1, gain: 0.1, wave: 'sine' },
                    { freq: 880, duration: 0.12, gain: 0.12, wave: 'triangle', fade: true, delay: 0.08 }
                ]);
                break;
            case 'jeopardy-tick':
                // Classic Jeopardy countdown tick sound
                this.sequence([
                    { freq: 800, duration: 0.06, gain: 0.14, wave: 'square', fade: true },
                    { freq: 600, duration: 0.04, gain: 0.10, wave: 'sine', fade: true, delay: 0.02 }
                ]);
                break;
            case 'timer-warning':
                // Urgent warning beep (10 seconds left)
                this.sequence([
                    { freq: 880, duration: 0.1, gain: 0.16, wave: 'square', fade: true },
                    { freq: 1100, duration: 0.08, gain: 0.14, wave: 'triangle', fade: true, delay: 0.04 }
                ]);
                break;
            case 'timer-critical':
                // Critical alarm (3 seconds left)
                this.sequence([
                    { freq: 1200, duration: 0.12, gain: 0.20, wave: 'square', fade: true },
                    { freq: 1400, duration: 0.10, gain: 0.18, wave: 'sawtooth', fade: true, delay: 0.05 }
                ]);
                break;
            case 'timer-buzzer':
                // LOUD buzzing alarm for time's up!
                this.sequence([
                    { freq: 220, duration: 0.15, gain: 0.30, wave: 'sawtooth', fade: false },
                    { freq: 180, duration: 0.15, gain: 0.28, wave: 'square', fade: false, delay: 0.02 },
                    { freq: 220, duration: 0.15, gain: 0.30, wave: 'sawtooth', fade: false, delay: 0.02 },
                    { freq: 180, duration: 0.15, gain: 0.28, wave: 'square', fade: false, delay: 0.02 },
                    { freq: 220, duration: 0.2, gain: 0.32, wave: 'sawtooth', fade: true, delay: 0.02 }
                ]);
                break;
            case 'morph-to-timer':
                // Smooth magical transition sound - morphing to honey jar timer (LOUDER)
                this.sequence([
                    { freq: 523, duration: 0.15, gain: 0.28, wave: 'sine', fade: false },  // C5
                    { freq: 659, duration: 0.15, gain: 0.32, wave: 'sine', fade: false, delay: 0.08 },  // E5
                    { freq: 784, duration: 0.25, gain: 0.36, wave: 'sine', fade: true, delay: 0.08 }   // G5
                ]);
                break;
            case 'morph-to-visualization':
                // Bright ascending chime - morphing back to voice visualization (LOUDER)
                this.sequence([
                    { freq: 784, duration: 0.12, gain: 0.32, wave: 'sine', fade: false },  // G5
                    { freq: 987, duration: 0.12, gain: 0.36, wave: 'sine', fade: false, delay: 0.06 },  // B5
                    { freq: 1319, duration: 0.20, gain: 0.40, wave: 'sine', fade: true, delay: 0.06 }   // E6
                ]);
                break;
        }
    }

    sequence(steps) {
        if (!this.ctx) {
            return;
        }

        let start = this.ctx.currentTime;
        steps.forEach((step) => {
            const duration = step.duration ?? 0.2;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = step.wave || 'sine';
            osc.frequency.setValueAtTime(step.freq, start);
            if (typeof step.slide === 'number') {
                osc.frequency.linearRampToValueAtTime(step.slide, start + duration);
            }

            const gainValue = Math.max(step.gain ?? 0.14, 0.0001);
            gain.gain.setValueAtTime(gainValue, start);
            if (step.fade) {
                gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
            }

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(start);
            osc.stop(start + duration + 0.01);

            start += step.delay ?? duration;
        });
    }

    speakWord(word, onEndCallback = null, rate = 0.92) {
        if (!word || !('speechSynthesis' in window)) {
            if (onEndCallback) onEndCallback();
            return;
        }
        
        speechSynthesis.cancel();
        
        const speak = () => {
            const utterance = new SpeechSynthesisUtterance(word);
            utterance.pitch = 1.35;
            utterance.rate = rate; // Use provided rate instead of fixed 0.92
            utterance.volume = 0.9;
            utterance.text = word;
            
            // Visualizer elements
            const visualizer = document.getElementById('voiceVisualizer');
            const statusEl = document.getElementById('voiceStatus');
            
            // Add event listeners for voice visualizer
            if (onEndCallback) {
                utterance.addEventListener('end', onEndCallback);
                utterance.addEventListener('error', onEndCallback);
            }
            
            // Use enhanced voice selection for natural-sounding female voices
            if (!this.cachedVoice) {
                this.cachedVoice = this.selectBestFemaleVoice();
                
                if (this.cachedVoice) {
                    console.log('🎤 speakWord using enhanced voice:', this.cachedVoice.name, this.cachedVoice.lang, 
                               'Quality:', this.cachedVoice.quality || 'default', 
                               'Local:', this.cachedVoice.localService);
                } else {
                    console.warn('⚠️ speakWord: No suitable voice found, using browser default');
                }
            }
            
            if (this.cachedVoice) {
                utterance.voice = this.cachedVoice;
            }
            
            // Sync visual display with announcer + morph to voice visualizer
            utterance.onstart = () => {
                if (visualizer) visualizer.classList.add('speaking');
                if (statusEl) statusEl.textContent = this.cachedVoice
                    ? `🎙️ Speaking (${this.cachedVoice.lang} • ${this.cachedVoice.name})`
                    : '🎙️ Speaking';
                
                // ⚠️ NO morphing here - only morph after "timer starts now" announcement
            };
            
            utterance.onboundary = (event) => {
                // Word-level micro pauses for natural cadence
                if (event.name === 'word' || event.charLength > 0) {
                    if (visualizer) {
                        visualizer.classList.remove('speaking');
                        visualizer.classList.add('pausing', 'word-pulse');
                        setTimeout(() => {
                            visualizer.classList.remove('pausing', 'word-pulse');
                            visualizer.classList.add('speaking');
                        }, 150);
                    }
                }
                // Longer pause at sentence punctuation
                const char = (utterance.text || '').charAt(event.charIndex || 0);
                if (char === ',' || char === ';' || char === '.' || char === '!' || char === '?') {
                    if (visualizer) {
                        visualizer.classList.remove('speaking');
                        visualizer.classList.add('pausing');
                        setTimeout(() => {
                            visualizer.classList.remove('pausing');
                            visualizer.classList.add('speaking');
                        }, 400);
                    }
                }
            };
            
            utterance.onend = () => {
                if (visualizer) visualizer.classList.remove('speaking', 'word-pulse', 'pausing');
                if (statusEl) statusEl.textContent = '🐝 Ready';
                
                // ⚠️ NO morphing here - only morph after "timer starts now" announcement
            };
            
            utterance.onerror = () => {
                if (visualizer) visualizer.classList.remove('speaking', 'word-pulse', 'pausing');
                if (statusEl) statusEl.textContent = '⚠️ Voice error';
                
                // ⚠️ NO morphing here - only morph after "timer starts now" announcement
            };

            try {
                speechSynthesis.speak(utterance);
            } catch (err) {
                console.error('speechSynthesis.speak failed:', err);
                if (onEndCallback) onEndCallback();
            }
        };
        
        // iOS Safari fix: Better voice loading with timeout
        const voices = speechSynthesis.getVoices();
        if (voices.length > 0) {
            speak();
        } else {
            // iOS often needs a delay
            let timeout = setTimeout(() => {
                console.warn('⚠️ Voice loading timeout - speaking anyway');
                speak();
            }, 2000);
            
            speechSynthesis.addEventListener('voiceschanged', () => {
                clearTimeout(timeout);
                speak();
            }, { once: true });
        }
    }
    
    // Enhanced voice selection algorithm for natural-sounding female voices
    selectBestFemaleVoice() {
        const voices = speechSynthesis.getVoices();
        
        // Score voices based on multiple criteria
        const scoredVoices = voices
            .filter(voice => voice.lang.startsWith('en')) // English only
            .map(voice => {
                let score = 0;
                const name = voice.name.toLowerCase();
                
                // Language preference (US English gets highest priority)
                if (voice.lang === 'en-US') score += 100;
                else if (voice.lang.startsWith('en-')) score += 50;
                
                // Quality indicators
                if (voice.quality === 'high') score += 50;
                else if (voice.quality === 'enhanced') score += 40;
                
                // Local voices often sound better
                if (voice.localService) score += 30;
                
                // Explicit female voice indicators
                if (name.includes('female')) score += 80;
                if (name.includes('woman')) score += 80;
                
                // Premium/Natural voice names
                if (name.includes('natural')) score += 60;
                if (name.includes('premium')) score += 60;
                if (name.includes('neural')) score += 60;
                
                // Known high-quality female voices
                const premiumVoices = {
                    'samantha': 90, 'aria': 85, 'jenny': 85, 'alex': 85,
                    'victoria': 80, 'nova': 80, 'zira': 75, 'allison': 70
                };
                
                for (const [voiceName, points] of Object.entries(premiumVoices)) {
                    if (name.includes(voiceName)) {
                        score += points;
                        break;
                    }
                }
                
                return { voice, score };
            })
            .sort((a, b) => b.score - a.score);
        
        if (scoredVoices.length > 0) {
            return scoredVoices[0].voice;
        }
        
        return null;
    }
}

// ⚠️ DUPLICATE CLASS REMOVED - MorphController was intentionally removed
// All MorphController references have been disabled throughout the quiz

// DUPLICATE CountdownTimer CLASS REMOVED (It is defined at the top of the file)

class BeeDelightManager {
    constructor() {
        this.quizCard = document.getElementById('quizCard');
        this.inputWrapper = document.getElementById('beeInputWrapper');
        this.feedbackArea = document.getElementById('feedbackArea');
        this.phoneticHint = document.getElementById('phoneticHint');
        this.honeyFill = document.getElementById('honeyFillRect');  // SVG rect element
        this.mascot = document.getElementById('beeMascot');
        this.soundboard = new BeeSoundboard();
        this.totalQuestions = 0;
        this.mascotTimer = null;
        this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.cursorTrailLast = 0;

        this.registerButtonSparkles();
        this.registerCursorTrail();
        this.setupButtonEffects();
        this.setupExitQuiz();
    }

    setupExitQuiz() {
        const exitButton = document.getElementById('exitQuizButton');
        const nextWordButton = document.getElementById('nextWordButton');
        const exitModal = document.getElementById('exitModal');
        const stayButton = document.getElementById('stayButton');
        const confirmExitButton = document.getElementById('confirmExitButton');

        // Show exit confirmation modal
        exitButton?.addEventListener('click', () => {
            this.showExitModal();
        });

        // Next Word button - manual advance after retry window closes
        nextWordButton?.addEventListener('click', async () => {
            console.log('⏭️ Next Word button clicked');
            // Hide the Next Word button
            if (nextWordButton) {
                nextWordButton.style.display = 'none';
                console.log('✅ Next Word button hidden');
            }
            // Hide feedback area
            const feedbackArea1 = document.getElementById('feedbackArea');
            if (feedbackArea1) feedbackArea1.style.display = 'none';
            this.soundboard?.play('button-primary');
            // Call loadNextWord on the global quizManager instance
            if (window.quizManager && typeof window.quizManager.loadNextWord === 'function') {
                await window.quizManager.loadNextWord();
            }
        });

        // Stay and continue practicing
        stayButton?.addEventListener('click', () => {
            this.hideExitModal();
            this.soundboard.play('button-primary');
        });

        // Confirm exit and go to menu
        confirmExitButton?.addEventListener('click', () => {
            this.confirmExit();
        });

        // Close modal on backdrop click
        exitModal?.addEventListener('click', (e) => {
            if (e.target === exitModal) {
                this.hideExitModal();
            }
        });
    }

    showExitModal() {
        const exitModal = document.getElementById('exitModal');
        const exitStats = document.getElementById('exitStats');
        
        // Update stats in the modal
        const correctCount = document.getElementById('correctCount')?.textContent || '0';
        const incorrectCount = document.getElementById('incorrectCount')?.textContent || '0';
        const streakCount = document.getElementById('streakCount')?.textContent || '0';
        
        exitStats.innerHTML = `
            <div>📝 Words spelled: ${parseInt(correctCount) + parseInt(incorrectCount)}</div>
            <div>✅ Correct answers: ${correctCount}</div>
            <div>🔥 Current streak: ${streakCount}</div>
        `;
        
        exitModal.style.display = 'flex';
        this.soundboard.play('button-hover');
    }

    hideExitModal() {
        const exitModal = document.getElementById('exitModal');
        exitModal.style.display = 'none';
    }

    confirmExit() {
        this.soundboard.play('success');
        
        // Add a friendly exit message
        const exitModal = document.getElementById('exitModal');
        const modalContent = exitModal.querySelector('.exit-modal-content');
        
        modalContent.innerHTML = `
            <div class="exit-modal-header">
                <h3>🌟 Great job spelling today!</h3>
            </div>
            <div class="exit-modal-body">
                <p>🐝 You're becoming a spelling superstar!</p>
                <p>Come back anytime to practice more words!</p>
            </div>
        `;
        
        // Redirect after a short delay
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    setupButtonEffects() {
        // Add sound and visual effects to all action buttons
        const buttons = document.querySelectorAll('.action-btn');
        buttons.forEach((button) => {
            // Hover effects
            button.addEventListener('mouseenter', () => {
                this.soundboard.play('button-hover');
            });

            // Click effects
            button.addEventListener('click', (event) => {
                if (button.classList.contains('primary')) {
                    this.soundboard.play('button-primary');
                    this.addButtonEffect(button, 'ripple-effect');
                } else if (button.classList.contains('exit')) {
                    this.soundboard.play('button-click');
                    this.addButtonEffect(button, 'buzz-effect');
                } else {
                    this.soundboard.play('button-click');
                    this.addButtonEffect(button, 'buzz-effect');
                }
                
                // Add sparkle magic on button press
                if (!this.reducedMotion) {
                    this.createSparkleBurst(button);
                }
            });
        });
    }

    addButtonEffect(button, effectClass) {
        button.classList.add(effectClass);
        setTimeout(() => {
            button.classList.remove(effectClass);
        }, 400);
    }

    registerButtonSparkles() {
        const buttons = document.querySelectorAll('.quiz-buttons .quiz-button');
        buttons.forEach((button) => {
            button.addEventListener('click', () => {
                if (!this.reducedMotion) {
                    this.createSparkleBurst(button);
                }
            });
        });
    }

    registerCursorTrail() {
        if (this.reducedMotion) {
            return;
        }

        document.addEventListener('pointermove', (event) => {
            const now = performance.now();
            if (now - this.cursorTrailLast < 60) {
                return;
            }
            this.cursorTrailLast = now;

            const trail = document.createElement('div');
            trail.className = 'cursor-trail';
            trail.style.left = `${event.clientX - 9}px`;
            trail.style.top = `${event.clientY - 9}px`;
            document.body.appendChild(trail);
            setTimeout(() => trail.remove(), 600);
        });
    }

    setTotalQuestions(total) {
        if (Number.isFinite(total) && total > 0) {
            this.totalQuestions = total;
        }
    }

    updateProgress(progress = {}) {
        if (!this.honeyFill) {
            return;
        }

        const total = progress.total ?? this.totalQuestions;
        if (Number.isFinite(total) && total > 0) {
            this.totalQuestions = total;
        }

        const workingTotal = this.totalQuestions || total;
        if (!workingTotal) {
            return;
        }

        const correct = Math.max(progress.correct ?? 0, 0);
        const ratio = Math.min(correct / workingTotal, 1);
        
        // Update SVG honey fill
        const jarHeight = 110; // SVG jar body height
        const minHeight = 13; // 12% of 110
        const fillHeight = minHeight + (ratio * (jarHeight - minHeight));
        const fillY = 35 + (jarHeight - fillHeight);
        
        this.honeyFill.setAttribute('height', Math.max(minHeight, Math.round(fillHeight)));
        this.honeyFill.setAttribute('y', fillY);
    }

    handleDefinition() {
        this.showPhonetic('');
        this.clearFeedbackState();
    }

    handlePronounce(data, onEndCallback = null) {
        this.soundboard.play('speak');
        if (data?.word) {
            // Speak a friendly prompt and the word twice
            const phrase = `Spell the word ${data.word}. ${data.word}.`;
            const rate = data.rate || 0.92; // Use provided rate or default
            this.soundboard.speakWord(phrase, onEndCallback, rate);
        } else if (onEndCallback) {
            onEndCallback();
        }
        this.setMascotState('speaking', 1600);
        const speakButton = document.getElementById('speakButton');
        if (!this.reducedMotion && speakButton) {
            this.createSparkleBurst(speakButton, 7);
        }
    }

    handleFeedback(result) {
        if (!this.quizCard) {
            return;
        }

        this.quizCard.classList.remove('correct', 'incorrect');
        this.quizCard.classList.add('quiz-feedback');

        if (result.correct) {
            this.quizCard.classList.add('correct');
            this.soundboard.play('correct');
            this.setMascotState('happy', 1700);
            if (!this.reducedMotion) {
                this.createSparkleBurst(this.inputWrapper || this.quizCard, 8);
            }
            this.showPhonetic('');
        } else {
            this.quizCard.classList.add('incorrect');
            this.soundboard.play(result.skipped ? 'skip' : 'incorrect');
            this.setMascotState(result.skipped ? 'speaking' : 'sad', result.skipped ? 1000 : 1400);
            // ❌ DO NOT show phonetic on first attempt - user hasn't chosen yet
            this.showPhonetic('');
        }
    }

    handleSkip() {
        this.soundboard.play('skip');
        this.setMascotState('sad', 1000);
    }

    showPhonetic(text) {
        if (!this.phoneticHint) {
            return;
        }

        if (!text) {
            this.phoneticHint.textContent = '';
            this.phoneticHint.classList.add('hidden');
            return;
        }

        this.phoneticHint.textContent = `Phonetic: ${text}`;
        this.phoneticHint.classList.remove('hidden');
    }

    clearFeedbackState() {
        if (this.quizCard) {
            this.quizCard.classList.remove('quiz-feedback', 'correct', 'incorrect');
        }
    }

    setMascotState(state, duration = 1500) {
        if (!this.mascot) {
            return;
        }

        const classes = {
            happy: 'is-happy',
            sad: 'is-sad',
            speaking: 'is-speaking'
        };

        Object.values(classes).forEach(cls => this.mascot.classList.remove(cls));

        if (state && classes[state]) {
            this.mascot.classList.add(classes[state]);
            clearTimeout(this.mascotTimer);
            if (duration > 0) {
                this.mascotTimer = setTimeout(() => {
                    this.mascot?.classList.remove(classes[state]);
                }, duration);
            }
        }
    }

    createSparkleBurst(target, count = 8) {
        if (!target) {
            return;
        }
        const rect = target.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        for (let i = 0; i < count; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            
            // Create more magical spread pattern
            const angle = (i / count) * Math.PI * 2;
            const distance = 30 + Math.random() * 40;
            const offsetX = Math.cos(angle) * distance + (Math.random() - 0.5) * 20;
            const offsetY = Math.sin(angle) * distance + (Math.random() - 0.5) * 20;
            
            sparkle.style.left = `${centerX + offsetX}px`;
            sparkle.style.top = `${centerY + offsetY}px`;
            
            // Add random sparkle colors
            const colors = ['#FFD700', '#FFA500', '#FFE082', '#FFEB3B', '#FFF59D'];
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            sparkle.style.setProperty('--sparkle-color', randomColor);
            
            // Add random delay for more magical effect
            sparkle.style.animationDelay = `${Math.random() * 0.3}s`;
            
            document.body.appendChild(sparkle);
            setTimeout(() => sparkle.remove(), 900);
        }
    }
}

class QuizManager {
    constructor(options = {}) {
        console.log('🏗️ QuizManager constructor called');
        this.delight = options.delight || null;
        this.smartyBee = options.smartyBee || null;
        this.soundboard = (this.delight && this.delight.soundboard) || new BeeSoundboard(); // Get soundboard from delight or create new
        this.isAnswering = false;
        this.lastPronounceData = null;
        this.currentWordData = null;
        this.totalWords = 0;
        this.quizStarted = false;
        
        // ⏱️ Countdown Timer Settings (Updated to 60s with auto-advance)
        this.timerEnabled = true; // Can be toggled in settings
        this.timerDuration = 60; // Default 60 seconds
        this.timerMode = 'normal'; // 'easy' (90s), 'normal' (60s), 'challenge' (30s), 'dynamic'
        this.timerStrictMode = true; // Auto-advance when time expires (changed from false)
        this.countdownTimer = null;
        
        // 🏆 Points System Settings
        this.pointsEnabled = true; // Enable points tracking
        this.sessionPoints = 0; // Total points for current session
        this.currentStreak = 0; // Consecutive correct answers
        this.maxStreak = 0; // Best streak this session
        
        // 💡 Hint tracking for current word
        this.hintUsedThisWord = false; // Track if hint was used for current word
        
        // 🔄 Retry System Tracking
        this.retryAvailable = false; // Can the user retry this word?
        this.hasRetried = false; // Has user already used their retry?
        this.isRetryAttempt = false; // Is current attempt a retry?
        this.retryTimeoutId = null; // Timeout for auto-advance after retry
        
        // Get student name - prioritize server-provided name for logged-in users
        {% if user_name is defined and user_name %}
        this.studentName = {{ user_name|tojson }};
        // Save to localStorage for consistency
        localStorage.setItem('studentName', this.studentName);
        console.log('👤 Using logged-in user name:', this.studentName);
        {% else %}
        // Check sessionStorage for guest name, then localStorage
        this.studentName = sessionStorage.getItem('guestName') || localStorage.getItem('studentName') || '';
        console.log('👤 Using guest/localStorage name:', this.studentName);
        {% endif %}
        
        // Reset honey jar to 0% at start
        this.resetHoneyJar();
        
        // Randomized positive feedback messages (without names - we'll add dynamically)
        this.positiveFeedback = [
            "🐝 BEE-utiful! That's absolutely correct!",
            "🍯 Sweet spelling! You nailed it!",
            "✨ Buzz-tastic! Perfect spelling!",
            "🌟 Honey of a job! You got it!",
            "🎯 Bulls-bee! Spelled perfectly!",
            "💛 Golden! That's the right spelling!",
            "🐝 Bee-lieve it! You're amazing!",
            "🏆 Hive five! Excellent work!",
            "⭐ Un-bee-lievable! That's correct!",
            "🍯 Sweet success! Well done!",
            "🎉 Buzz worthy! Perfect spelling!",
            "🌺 Bee-autiful work! Correct!",
            "💪 Bee strong! You aced it!",
            "🎊 What a honey! Fantastic!",
            "🌈 Spectacular spelling!",
            "🐝 Brilliant! Absolutely brilliant!",
            "🍯 You're on fire! Keep it up!",
            "⭐ Magnificent spelling!",
            "🎯 Perfect! Just perfect!"
        ];
        
        // Randomized negative feedback messages (without names - we'll add dynamically)
        this.negativeFeedback = [
            "🐝 Oops! That's not quite right. Try again!",
            "🍯 Not quite! Don't worry, even bees make mistakes!",
            "💫 Almost there! Give it another buzz!",
            "🌸 Not this time! Keep trying, you can do it!",
            "🐝 Whoops! Let's try that spelling again!",
            "🎯 Not quite hitting the hive! Try once more!",
            "🌟 Close, but not quite! You've got this!",
            "🐝 Bee-lieve in yourself and try again!",
            "💛 That's not it, but don't give up!",
            "🍯 Sweeter spelling needed! Give it another go!",
            "🌺 Not the right buzz! Try again!",
            "🎪 Oopsie-daisy! Let's spell it again!",
            "🐝 Buzz! That's incorrect, but keep going!",
            "💫 Not quite right! You can do this!",
            "🌟 Almost! Give it another try!",
            "🍯 Nice try! Let's practice more!",
            "🐝 That's okay! Learning is a journey!",
            "💫 Keep buzzing! You'll get it!"
        ];
        
        // 📣 Word introduction announcements - multiple variations for variety
        this.wordIntroAnnouncements = [
            "Your word is",
            "Here's your word:",
            "Next word coming up:",
            "Ready? Your word is:",
            "Let's try this word:",
            "Your spelling challenge is:",
            "This word for you:",
            "Can you spell this word:",
            "Focus on this word:",
            "Pay attention! Your word is:",
            "Listen carefully! Word is:",
            "Spell this one:"
        ];
        
        // ⏱️ Randomized timer start announcements
        this.timerStartAnnouncements = [
            "Your 60 seconds to spell the word begins now!",
            "Ready? Your timer starts now!",
            "The clock is ticking! 60 seconds begins now!",
            "Let's see how fast you can spell this! Timer starting!",
            "You have 60 seconds! Go!",
            "Timer activated! Spell away!",
            "The honey jar is draining! Start spelling!",
            "60 seconds on the clock! Begin!",
            "Time's running! Spell the word now!",
            "Your countdown begins right now!",
            "The timer has started! Good luck!",
            "60 seconds to show your spelling skills! Go!",
            "Clock's ticking! Let's spell!",
            "Timer's rolling! Start spelling!",
            "You're on the clock! 60 seconds!"
        ];
        
        // Audio announcements for correct answers (name removed to avoid repetition)
        this.correctAnnouncements = [
            "Fantastic! That's absolutely correct!",
            "Excellent spelling! You're doing great!",
            "Perfect! You got it right!",
            "Amazing work! That's correct!",
            "Brilliant! You spelled it perfectly!",
            "Wonderful! That's the right spelling!",
            "Outstanding! You're a spelling star!",
            "Superb! You nailed that word!",
            "Marvelous! Correct spelling!",
            "Spectacular! You're on fire!"
        ];
        
        // Audio announcements for incorrect answers (name removed to avoid repetition)
        this.incorrectAnnouncements = [
            "Not quite right, but don't give up!",
            "That's not it, but keep trying!",
            "Oops, let's try that again!",
            "Not this time, but you're learning!",
            "Almost there! Give it another try!",
            "That's not the spelling, but keep going!",
            "Nice try! Let's practice more!",
            "Not quite, but you're getting closer!",
            "That's okay! Every mistake helps us learn!",
            "Keep trying! You'll get it next time!"
        ];

        // Voice announcer settings
        this.announcerEnabled = localStorage.getItem('announcerEnabled') !== 'false'; // Default ON
        this.voiceUnlocked = false; // iOS requires user interaction
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        this.isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        
        // Background music settings
        this.musicEnabled = localStorage.getItem('musicEnabled') !== 'false'; // Default ON
        this.backgroundMusic = null;
        
        console.log('🎤 Voice System Initialization:');
        console.log('   - announcerEnabled:', this.announcerEnabled);
        console.log('   - voiceUnlocked:', this.voiceUnlocked);
        console.log('   - isIOS:', this.isIOS);
        console.log('   - isSafari:', this.isSafari);
        console.log('   - localStorage announcerEnabled:', localStorage.getItem('announcerEnabled'));
        console.log('🎵 Music System Initialization:');
        console.log('   - musicEnabled:', this.musicEnabled);
        
        try {
            this.initializeEventListeners();
        } catch (e) {
            console.error('❌ Error in initializeEventListeners:', e);
        }
        
        // 🍎 iOS-specific optimizations
        if (this.isIOS || this.isSafari) {
            this.setupiOSKeyboardHandling();
        }
        
        // Show iOS voice intro modal if needed, otherwise show regular intro
        if ((this.isIOS || this.isSafari) && !sessionStorage.getItem('voiceIntroShown')) {
            console.log('📱 Showing iOS/Safari voice intro modal');
            this.updateVoiceToggleUI(); // Initialize UI to match state
            this.updateMusicToggleUI(); // Initialize music UI to match state
            this.showVoiceIntroModal();
        } else {
            console.log('💻 Desktop/Non-iOS browser detected - voice unlocked immediately');
            this.voiceUnlocked = true; // Non-iOS can use voice immediately
            this.updateVoiceToggleUI(); // Initialize UI to match state
            this.updateMusicToggleUI(); // Initialize music UI to match state
            this.showIntroAnnouncer();
        }
        
        // Start background music if enabled
        if (this.musicEnabled) {
            // Delay music start slightly to avoid autoplay blocking
            setTimeout(() => this.playBackgroundMusic(), 500);
        }
    }
    
    // 🍎 iOS-specific keyboard and viewport handling
    setupiOSKeyboardHandling() {
        const spellingInput = document.getElementById('spellingInput');
        if (!spellingInput) return;
        
        console.log('🍎 Setting up iOS keyboard handling');
        
        // Prevent page zoom when focusing input (already handled by 16px font size)
        // Scroll input into view when keyboard appears
        spellingInput.addEventListener('focus', () => {
            console.log('🍎 iOS input focused - ensuring visibility');
            
            // Small delay to let keyboard animate in
            setTimeout(() => {
                // Scroll the input into view smoothly
                spellingInput.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center',
                    inline: 'nearest'
                });
            }, 300);
        });
        
        // Handle blur (keyboard dismissal)
        spellingInput.addEventListener('blur', () => {
            console.log('🍎 iOS input blurred - keyboard likely dismissed');
            
            // Scroll back to top of quiz area if needed
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
        });
        
        // Prevent unwanted scrolling during keyboard appearance
        document.body.addEventListener('touchmove', (e) => {
            // Only prevent if input is focused and at the edges of scroll
            if (document.activeElement === spellingInput) {
                const target = e.target;
                const scrollable = this.findScrollableParent(target);
                
                if (!scrollable || scrollable === document.body) {
                    // No scrollable parent, prevent default
                    // e.preventDefault(); // Commented out to allow normal scrolling
                }
            }
        }, { passive: true });
        
        console.log('✅ iOS keyboard handling configured');
    }
    
    // Helper to find scrollable parent element
    findScrollableParent(element) {
        if (!element || element === document.body) return null;
        
        const overflowY = window.getComputedStyle(element).overflowY;
        const isScrollable = overflowY === 'scroll' || overflowY === 'auto';
        
        if (isScrollable && element.scrollHeight > element.clientHeight) {
            return element;
        }
        
        return this.findScrollableParent(element.parentElement);
    }
    
    // Helper function to remove emojis and special characters for speech
    cleanTextForSpeech(text) {
        // Remove emojis and special symbols, keep only letters, numbers, punctuation
        return text.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim();
    }
    
    // Enhanced voice selection algorithm for natural-sounding female voices
    selectBestFemaleVoice() {
        const voices = speechSynthesis.getVoices();
        console.log('🎤 Analyzing', voices.length, 'available voices for best female selection');
        
        // Score voices based on multiple criteria
        const scoredVoices = voices
            .filter(voice => voice.lang.startsWith('en')) // English only
            .map(voice => {
                let score = 0;
                const name = voice.name.toLowerCase();
                
                // Language preference (US English gets highest priority)
                if (voice.lang === 'en-US') score += 100;
                else if (voice.lang.startsWith('en-')) score += 50;
                
                // Quality indicators (higher quality = more natural)
                if (voice.quality === 'high') score += 50;
                else if (voice.quality === 'enhanced') score += 40;
                else if (voice.quality === 'normal') score += 20;
                
                // Local voices often sound more natural than cloud-based
                if (voice.localService) score += 30;
                
                // Explicit female voice indicators
                if (name.includes('female')) score += 80;
                if (name.includes('woman')) score += 80;
                
                // Premium/Natural voice names (typically higher quality)
                if (name.includes('natural')) score += 60;
                if (name.includes('premium')) score += 60;
                if (name.includes('neural')) score += 60;
                
                // Known high-quality female voices (ordered by naturalness)
                const premiumVoices = {
                    'samantha': 90,     // macOS - very natural
                    'alex': 85,         // macOS - excellent quality
                    'victoria': 80,     // Windows - natural sounding
                    'zira': 75,         // Windows - clear and natural
                    'aria': 85,         // Modern Windows neural
                    'jenny': 85,        // Modern neural voice
                    'nova': 80,         // Modern neural voice
                    'allison': 70,      // Traditional but good
                    'ava': 70,          // Traditional but good
                    'joanna': 65,       // Amazon Polly style
                    'susan': 60,        // Traditional
                    'karen': 55,        // Traditional
                    'moira': 50         // Traditional Irish
                };
                
                // Check for premium voice names
                for (const [voiceName, points] of Object.entries(premiumVoices)) {
                    if (name.includes(voiceName)) {
                        score += points;
                        break;
                    }
                }
                
                // Avoid robotic or synthetic-sounding voices
                if (name.includes('robot')) score -= 50;
                if (name.includes('synthetic')) score -= 30;
                if (name.includes('microsoft') && !name.includes('aria')) score -= 10; // Modern MS voices are better
                
                // Log voice evaluation for debugging
                console.log(`🎤 Voice: ${voice.name} (${voice.lang}) - Score: ${score}`, {
                    quality: voice.quality || 'default',
                    local: voice.localService,
                    voiceURI: voice.voiceURI
                });
                
                return { voice, score };
            })
            .sort((a, b) => b.score - a.score); // Sort by highest score first
        
        if (scoredVoices.length > 0) {
            const bestVoice = scoredVoices[0].voice;
            console.log(`🏆 Selected best voice: ${bestVoice.name} (${bestVoice.lang}) with score ${scoredVoices[0].score}`);
            console.log(`   Quality: ${bestVoice.quality || 'default'}, Local: ${bestVoice.localService}, URI: ${bestVoice.voiceURI}`);
            return bestVoice;
        }
        
        console.warn('⚠️ No suitable female voice found in', voices.length, 'available voices');
        return null;
    }
    
    speakAnnouncement(text) {
        // Check if announcer is enabled
        if (!this.announcerEnabled) {
            console.log('🔇 Announcer is muted');
            return Promise.resolve(); // Return resolved promise immediately
        }
        
        // Check if voice is unlocked (important for iOS)
        if ((this.isIOS || this.isSafari) && !this.voiceUnlocked) {
            console.log('🔒 Voice not unlocked on iOS - skipping announcement');
            return Promise.resolve();
        }
        
        // 🍎 iOS FIX: Cancel any ongoing speech to prevent echo
        if ('speechSynthesis' in window && speechSynthesis.speaking) {
            console.log('🔊 Cancelling ongoing speech to prevent iOS echo');
            speechSynthesis.cancel();
            // Small delay for iOS to process cancellation
            return new Promise(resolve => {
                setTimeout(() => {
                    this.speakAnnouncementInternal(text).then(resolve);
                }, 100);
            });
        }
        
        return this.speakAnnouncementInternal(text);
    }
    
    speakAnnouncementInternal(text) {
        // Clean text by removing emojis before speaking
        const cleanText = this.cleanTextForSpeech(text);
        
        // Get visualizer elements
        const visualizer = document.getElementById('voiceVisualizer');
        const status = document.getElementById('voiceStatus');
        
        // Start visualizer animation
        if (visualizer && status) {
            console.log('🎤 Starting voice visualizer for announcement');
            visualizer.classList.add('speaking');
            status.textContent = '🗣️ Speaking...';
        }
        
        // Return a promise that resolves when speech is done
        return new Promise((resolve) => {
            // Use Web Speech API to announce results
            if (!('speechSynthesis' in window)) {
                // Stop visualizer if no speech synthesis
                if (visualizer && status) {
                    visualizer.classList.remove('speaking');
                    status.textContent = '🐝 Ready';
                }
                resolve(); // If no speech synthesis, resolve immediately
                return;
            }
            
            // Function to speak with the selected voice
            const speak = () => {
                const utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.rate = 1.0;  // Normal speed for US English
                utterance.pitch = 1.1;
                utterance.volume = 0.85;
                
                // Cache the selected voice to ensure consistency using enhanced selection
                if (!this.cachedVoice) {
                    this.cachedVoice = this.selectBestFemaleVoice();
                    
                    if (this.cachedVoice) {
                        const voiceType = this.cachedVoice.lang === 'en-US' 
                            ? '🎤 Enhanced US Female' : '🗣️ Enhanced Female English';
                        console.log(`🎤 Selected enhanced voice for session: ${this.cachedVoice.name} (${this.cachedVoice.lang}) [${voiceType}]`);
                    } else {
                        console.warn('⚠️ No suitable enhanced female voice found, using browser default');
                    }
                }
                
                if (this.cachedVoice) {
                    utterance.voice = this.cachedVoice;
                }
                
                // Word boundary event - pulse animation on each word with natural pauses
                utterance.onboundary = (event) => {
                    if (!visualizer) return;
                    
                    // Pulse effect on word boundaries with brief natural pause
                    if (event.name === 'word') {
                        console.log('🎤 Word boundary:', event.charIndex);
                        visualizer.classList.add('word-pulse');
                        // Briefly switch from speaking→pausing→speaking for a visible dip
                        visualizer.classList.remove('speaking');
                        visualizer.classList.add('pausing');
                        setTimeout(() => {
                            visualizer.classList.remove('pausing', 'word-pulse');
                            visualizer.classList.add('speaking');
                        }, 130);
                    }
                    
                    // Natural pause on sentence boundaries (longer, amber bars)
                    const utterText = (utterance.text || '');
                    const ch = utterText.charAt(event.charIndex);
                    if (ch === '.' || ch === '!' || ch === '?' || event.name === 'sentence') {
                        console.log('🎤 Sentence boundary - natural pause');
                        visualizer.classList.remove('speaking');
                        visualizer.classList.add('pausing');
                        setTimeout(() => {
                            visualizer.classList.remove('pausing');
                            visualizer.classList.add('speaking');
                        }, 400);
                    }
                };
                
                // Add event listener for when speech actually starts
                utterance.onstart = () => {
                    console.log('🎤 Speech started - activating visualizer');
                    if (visualizer && status) {
                        visualizer.classList.add('speaking');
                        status.textContent = '🗣️ Speaking...';
                    }
                    
                    // ⚠️ NO morphing here - only morph after "timer starts now" announcement
                };
                
                // Add event listeners to resolve promise when speech ends
                utterance.onend = () => {
                    console.log('✅ Speech finished');
                    // Stop visualizer animation
                    if (visualizer && status) {
                        console.log('🎤 Stopping voice visualizer for announcement');
                        visualizer.classList.remove('speaking', 'word-pulse', 'pausing');
                        status.textContent = '🐝 Ready';
                    }
                    
                    // ⚠️ NO morphing here - only morph after "timer starts now" announcement
                    
                    resolve();
                };
                
                utterance.onerror = (event) => {
                    console.warn('⚠️ Speech error:', event.error);
                    // Stop visualizer animation on error
                    if (visualizer && status) {
                        visualizer.classList.remove('speaking', 'word-pulse', 'pausing');
                        status.textContent = '🐝 Ready';
                    }
                    
                    // 🎭 MorphController removed - using CSS transitions instead
                    
                    resolve(); // Resolve even on error to prevent blocking
                };
                
                speechSynthesis.speak(utterance);
            };
            
            // Ensure voices are loaded
            if (speechSynthesis.getVoices().length > 0) {
                speak();
            } else {
                speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
            }
        });
    }
    
    createExplosion() {
        // Create buzz-worthy explosion effect for correct answers
        const container = document.createElement('div');
        container.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 9999;
        `;
        
        // Create multiple particles
        const particleCount = 30;
        const emojis = ['🐝', '🍯', '⭐', '✨', '💛', '🌟', '🎉', '🎊'];
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            const emoji = emojis[Math.floor(Math.random() * emojis.length)];
            const angle = (Math.PI * 2 * i) / particleCount;
            const velocity = 100 + Math.random() * 100;
            const tx = Math.cos(angle) * velocity;
            const ty = Math.sin(angle) * velocity;
            
            particle.textContent = emoji;
            particle.style.cssText = `
                position: absolute;
                font-size: ${20 + Math.random() * 20}px;
                left: 0;
                top: 0;
                animation: explode 1s ease-out forwards;
                --tx: ${tx}px;
                --ty: ${ty}px;
            `;
            
            container.appendChild(particle);
        }
        
        document.body.appendChild(container);
        
        // Remove after animation
        setTimeout(() => container.remove(), 1000);
    }
    
    showIntroAnnouncer() {
        const feedbackArea = document.getElementById('feedbackArea');
        feedbackArea.style.display = 'block';
        feedbackArea.className = 'feedback-area feedback-success';
        
        // Check if mobile device (mobile autoplay policies can block speech)
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // Mobile gets "Tap to Start" button for better control
        if (isMobile) {
            // Check if iOS device
            const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
            
            if (isIOS) {
                // 🍎 iOS-specific intro with "Tap to Hear Voice" button
                feedbackArea.innerHTML = `
                    <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">
                        🐝 Welcome to BeeSmart Spelling! 🐝
                    </div>
                    <div style="margin-bottom: 1.5rem; color: #666; font-size: 1.1rem;">
                        I'm Buzzy, your announcer bee! 🍯
                    </div>
                    <div style="margin-bottom: 1.2rem;">
                        <button id="iosVoiceBtn" style="
                            background: linear-gradient(135deg, #4CAF50, #45a049);
                            border: 3px solid #388E3C;
                            border-radius: 15px;
                            padding: 15px 30px;
                            font-size: 1.2rem;
                            font-weight: 700;
                            color: white;
                            cursor: pointer;
                            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
                            min-height: 44px;
                            width: 85%;
                            max-width: 300px;
                            touch-action: manipulation;
                        ">
                            � Tap to Hear My Voice
                        </button>
                    </div>
                    <div id="iosVoiceStatus" style="margin: 1rem 0; font-size: 0.95rem; color: #666;">
                        Then we'll start spelling!
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <button id="skipVoiceBtn" style="
                            background: transparent;
                            border: 2px solid #ccc;
                            border-radius: 10px;
                            padding: 10px 20px;
                            font-size: 0.9rem;
                            color: #666;
                            cursor: pointer;
                            min-height: 44px;
                            touch-action: manipulation;
                        ">
                            Skip Intro (Start Now)
                        </button>
                    </div>
                `;
            } else {
                // Android/other mobile - standard tap to start
                feedbackArea.innerHTML = `
                    <div style="font-size: 1.2rem; font-weight: 700;">
                        �🐝 Welcome to BeeSmart Spelling! 🐝
                    </div>
                    <div style="margin-top: 0.8rem;">
                        🍯 I'm your announcer bee, Buzzy! 🍯
                    </div>
                    <div style="margin-top: 0.5rem;">
                        🌟 Listen carefully to each word, then spell it correctly! 🌟
                    </div>
                    <div style="margin-top: 1.2rem;">
                        <button id="startQuizBtn" style="
                            background: linear-gradient(135deg, #FFD700, #FFA500);
                            border: 3px solid #FF8C00;
                            border-radius: 15px;
                            padding: 15px 30px;
                            font-size: 1.3rem;
                            font-weight: 700;
                            color: #2C1810;
                            cursor: pointer;
                            box-shadow: 0 4px 15px rgba(255, 165, 0, 0.4);
                            min-height: 44px;
                            min-width: 200px;
                            touch-action: manipulation;
                        ">
                            🚀 Tap to Start! 🚀
                        </button>
                    </div>
                    <div id="voiceStatusMessage" style="margin-top: 1rem; font-size: 0.9rem; color: #666;"></div>
                `;
            }
            
            // 🍎 iOS-specific handlers
            if (isIOS) {
                // iOS Voice Button Handler
                const iosVoiceBtn = document.getElementById('iosVoiceBtn');
                const iosVoiceStatus = document.getElementById('iosVoiceStatus');
                const skipVoiceBtn = document.getElementById('skipVoiceBtn');
                
                iosVoiceBtn.addEventListener('click', () => {
                    console.log('🍎 iOS user tapped to hear intro voice');
                    
                    // 🍎 CRITICAL: Unlock voice for iOS - this enables all subsequent voice announcements
                    this.voiceUnlocked = true;
                    console.log('✅ Voice unlocked for iOS!');
                    
                    iosVoiceBtn.disabled = true;
                    iosVoiceBtn.style.opacity = '0.6';
                    iosVoiceBtn.style.cursor = 'not-allowed';
                    iosVoiceStatus.textContent = '🎤 Buzzy is speaking...';
                    iosVoiceStatus.style.color = '#4CAF50';
                    iosVoiceStatus.style.fontWeight = '600';
                    
                    const greeting = this.studentName ? `Hello ${this.studentName}!` : "Hello!";
                    const introMessage = `${greeting} I'm Buzzy, your announcer bee! ` +
                                       "Listen carefully to each word, then spell what you hear. " +
                                       "Let's start spelling and fill that honey jar!";
                    
                    // 🍎 CRITICAL: Create and speak IMMEDIATELY (iOS autoplay requirement)
                    speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(introMessage);
                    utterance.rate = 0.95;
                    utterance.pitch = 1.1;
                    utterance.volume = 0.9;
                    
                    utterance.onend = () => {
                        console.log('✅ iOS intro voice completed successfully');
                        iosVoiceStatus.textContent = '✅ Great! Starting quiz...';
                        iosVoiceStatus.style.color = '#4CAF50';
                        
                        setTimeout(() => {
                            feedbackArea.style.display = 'none';
                            this.quizStarted = true;
                            this.loadNextWordWithIntro();
                        }, 800);
                    };
                    
                    utterance.onerror = (err) => {
                        console.error('❌ iOS voice failed:', err);
                        iosVoiceStatus.textContent = '⚠️ Voice unavailable - starting quiz anyway!';
                        iosVoiceStatus.style.color = '#ff9800';
                        
                        setTimeout(() => {
                            feedbackArea.style.display = 'none';
                            this.quizStarted = true;
                            this.loadNextWordWithIntro();
                        }, 1500);
                    };
                    
                    // 🍎 Speak immediately while in user gesture context
                    speechSynthesis.speak(utterance);
                    
                }, { once: true });
                
                // iOS Skip Button Handler
                skipVoiceBtn.addEventListener('click', () => {
                    console.log('🍎 iOS user skipped voice intro');
                    
                    // 🍎 CRITICAL: Still need to unlock voice even if skipped
                    this.voiceUnlocked = true;
                    console.log('✅ Voice unlocked for iOS (via skip)!');
                    
                    feedbackArea.style.display = 'none';
                    this.quizStarted = true;
                    this.loadNextWordWithIntro();
                }, { once: true });
                
            } else {
                // Android/other mobile - Add click handler for start button
                document.getElementById('startQuizBtn').addEventListener('click', () => {
                    console.log('📱 Android/mobile user tapped to start quiz');
                    const startBtn = document.getElementById('startQuizBtn');
                    const statusMsg = document.getElementById('voiceStatusMessage');
                    
                    // Disable button during voice playback
                    if (startBtn) {
                        startBtn.disabled = true;
                        startBtn.style.opacity = '0.6';
                        startBtn.style.cursor = 'not-allowed';
                    }
                    
                    // Android voice intro
                    if ('speechSynthesis' in window) {
                        const greeting = this.studentName ? `Hello ${this.studentName}!` : "Hello!";
                        const introMessage = `${greeting} I'm Buzzy, your announcer bee! Let's start spelling!`;
                        
                        statusMsg.textContent = '🎤 Playing intro...';
                        
                        // Start speech and handle completion
                        this.speakAnnouncement(introMessage)
                            .then(() => {
                                console.log('✅ Voice intro completed successfully on Android');
                                statusMsg.textContent = '✅ Ready!';
                                
                                // Start quiz after voice completes
                                setTimeout(() => {
                                    feedbackArea.style.display = 'none';
                                    this.quizStarted = true;
                                    this.loadNextWordWithIntro();
                                }, 300);
                            })
                            .catch((err) => {
                                console.error('❌ Voice intro failed on Android:', err);
                                statusMsg.textContent = '⚠️ Voice unavailable, but quiz will continue';
                                statusMsg.style.color = '#ff9800';
                                
                                // Continue anyway
                                setTimeout(() => {
                                    feedbackArea.style.display = 'none';
                                    this.quizStarted = true;
                                    this.loadNextWordWithIntro();
                                }, 1000);
                            });
                    } else {
                        // No speech synthesis support
                        console.warn('⚠️ Speech synthesis not supported on this Android device');
                        statusMsg.textContent = '⚠️ Voice not available on this device';
                        statusMsg.style.color = '#ff9800';
                        
                        // Start quiz anyway after brief delay
                        setTimeout(() => {
                            feedbackArea.style.display = 'none';
                            this.quizStarted = true;
                            this.loadNextWordWithIntro();
                        }, 1500);
                    }
                }, { once: true });
            }
            
        } else {
            // Desktop gets auto-advancing intro with voice
            feedbackArea.innerHTML = `
                <div style="font-size: 1.2rem; font-weight: 700;">
                    🐝 Welcome to BeeSmart Spelling! 🐝
                </div>
                <div style="margin-top: 0.8rem;">
                    🍯 I'm your announcer bee, Buzzy! 🍯
                </div>
                <div style="margin-top: 0.5rem;">
                    🌟 Listen carefully to each word, then spell it correctly! 🌟
                </div>
                <div style="margin-top: 0.8rem; font-size: 1.1rem;">
                    ✨ Get ready for your first word! ✨
                </div>
            `;
            
            // Desktop voice intro
            if ('speechSynthesis' in window) {
                const greeting = this.studentName ? `Hello ${this.studentName}!` : "Hello!";
                const introMessage = `${greeting} I'm Buzzy, your announcer bee! Welcome to BeeSmart Spelling! ` +
                                   "Listen carefully to each word, then type what you hear. " +
                                   "Spell correctly to fill your honey jar with sweet success!";
                
                const speakIntro = () => {
                    console.log('🎤 Buzzy is ready to speak! Available voices:', speechSynthesis.getVoices().length);
                    
                    // iOS fix: Force voice loading by creating a dummy utterance first
                    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
                    if (isIOS) {
                        console.log('🍎 iOS detected - preloading voices');
                        const dummyUtterance = new SpeechSynthesisUtterance('');
                        speechSynthesis.speak(dummyUtterance);
                        speechSynthesis.cancel();
                    }
                    
                    this.speakAnnouncement(introMessage).catch(err => {
                        console.warn('Voice intro failed:', err);
                    });
                };
                
                if (speechSynthesis.getVoices().length > 0) {
                    speakIntro();
                } else {
                    speechSynthesis.addEventListener('voiceschanged', speakIntro, { once: true });
                }
            }
            
            // Auto-advance after 7 seconds on desktop
            setTimeout(async () => {
                feedbackArea.style.display = 'none';
                this.quizStarted = true;
                console.log('🎤 Intro complete - loading first word...');
                try {
                    await this.loadNextWordWithIntro();
                } catch (err) {
                    console.error('Failed to load first word:', err);
                    BeeSmart.showError('Failed to start quiz. Please refresh.');
                }
            }, 7000);
        }
    }
    
    async loadNextWordWithIntro() {
        try {
            this.lastPronounceData = null;
            // Reset hint tracking for new word
            this.hintUsedThisWord = false;
            
            const response = await fetch('/api/next', { 
                method: 'POST',
                credentials: 'same-origin'
            });
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                console.error('API Error:', data);
                BeeSmart.showError(data.message || data.error || 'Failed to load the next word');
                return;
            }

            if (data.done) {
                this.showQuizComplete(data.summary);
                return;
            }

            const questionNumber = data.index ?? data.number ?? 1;
            this.totalWords = data.total ?? this.totalWords;
            document.getElementById('progressText').textContent = `Question ${questionNumber} of ${data.total ?? '?'}`;

            if (data.progress) {
                // Use Object.assign for better compatibility
                const progressUpdate = Object.assign({}, data.progress, { total: data.total });
                this.updateScoreDisplay(progressUpdate);
            }

            if (this.delight && typeof this.delight.setTotalQuestions === 'function') {
                this.delight.setTotalQuestions(data.total);
            }

            // Set the definition with fallback - prefer explicit sentence/hint fields
            const defBox = document.getElementById('definitionDisplay');
            
            // Safe logging
            try {
                console.log('DEBUG loadNextWordWithIntro: /api/next response:', {
                    sentence: data.sentence,
                    hint: data.hint,
                    definition: data.definition,
                    word: data.word,
                    fullData: data
                });
            } catch (e) {
                console.log('DEBUG loadNextWordWithIntro: response received');
            }
            
            let chosen = '';
            if (data.sentence) {
                console.log('✓ Using sentence:', data.sentence);
                chosen = data.sentence;
            } else if (data.hint) {
                console.log('✓ Using hint:', data.hint);
                chosen = `Hint: ${data.hint}`;
            } else if (data.definition) {
                console.log('✓ Using definition:', data.definition);
                chosen = data.definition;
            } else {
                console.log('⚠️ No definition found, attempting /api/pronounce fallback');
                // Last resort fallback: try /api/pronounce for sentence/hint
                const pronounce = await this.fetchPronounce(true);
                chosen =
                    (pronounce && (pronounce.sentence || pronounce.hint))
                        ? (pronounce.sentence || `Hint: ${pronounce.hint}`)
                        : 'Listen carefully and spell the word you hear.';
                console.log('Using fallback:', chosen);
            }
            
            // Apply safety blanker to hide target word if it appears in the definition
            const finalDefinition = hideTargetWord(chosen, data.word);
            defBox.textContent = finalDefinition;
            
            // Also update the voice visualizer definition
            const voiceDefBox = document.getElementById('voiceDefinition');
            if (voiceDefBox) {
                voiceDefBox.textContent = finalDefinition;
            }

            // Store the word data
            this.currentWordData = {
                word: data.word || '',
                sentence: data.sentence || '',
                definition: data.definition || ''
            };

            // ✅ Allow early typing — enable input immediately (no need to wait for timer)
            {
                const spellingInput = document.getElementById('spellingInput');
                if (spellingInput) {
                    spellingInput.disabled = false;
                    spellingInput.value = '';
                    spellingInput.placeholder = 'Type your answer...';
                }
            }

            // If this first question is also the last, announce that explicitly
            if (data.total && questionNumber === data.total) {
                const namePart = (this.studentName || '').trim();
                const preface = namePart ? namePart + ', this is your last word.' : 'This is your last word.';
                await this.speakAnnouncement(preface);
            }
            
            // 📣 Build rich word intro with variety
            let wordIntro;
            if (questionNumber === 1) {
                const firstWordPhrases = [
                    'Your first word is:',
                    'Let\\'s start! Your first word is:',
                    'Here we go! First word is:',
                    'Ready? Your first word is:',
                    'Beginning now! Your word is:'
                ];
                wordIntro = firstWordPhrases[Math.floor(Math.random() * firstWordPhrases.length)];
            } else if (data.total && questionNumber === data.total) {
                wordIntro = 'This is your final word:';
            } else {
                const nextWordPhrases = [
                    'Next word:',
                    'Here\\'s the next one:',
                    'Moving on! Your word is:',
                    'Next up:',
                    'Ready for another? Word is:',
                    'Let\\'s keep going! Next word:'
                ];
                wordIntro = nextWordPhrases[Math.floor(Math.random() * nextWordPhrases.length)];
            }
            
            // Add student name for personalization (randomly)
            if (this.studentName && Math.random() < 0.4) {
                wordIntro = this.studentName + ', ' + wordIntro.toLowerCase();
            }
            
            wordIntro += ' ' + data.word + '.';
            
            // 📣 Wait for word intro announcement to complete
            await this.speakAnnouncement(wordIntro);
            
            // Brief visual pause between phases
            {
                const visualizer = document.getElementById('voiceVisualizer');
                const status = document.getElementById('voiceStatus');
                if (visualizer && status) {
                    visualizer.classList.add('pausing');
                    status.textContent = '⏸️ Pause...';
                }
                await new Promise(r => setTimeout(r, 500));
                if (visualizer && status) {
                    visualizer.classList.remove('pausing');
                }
            }
            
            // Auto‑pronounce the word (so kids hear it clearly before timing)
            await this.pronounceWord({ refresh: true });
            
            // ⏱️ Give user mental processing time BEFORE timer announcement (800ms)
            if (this.timerEnabled && this.quizStarted) {
                console.log('⏸️ Pausing 800ms for mental processing before timer...');
                await new Promise(resolve => setTimeout(resolve, 800));
                await this.announceAndStartTimer();
            }
            
            // Show "Can't hear?" helper notification after first word loads
            if (this.announcerEnabled && questionNumber === 1) {
                this.showVoiceHelperNotification();
            }

        } catch (error) {
            console.error('Error loading word:', error);
            BeeSmart.showError('Error loading word. Please try again.');
        }
    }
    
    // ⏱️ Countdown Timer Methods
    async announceAndStartTimer() {
        // Get random timer start announcement
        const announcement = this.getRandomTimerStartAnnouncement();
        
        console.log('⏱️ Announcing timer start:', announcement);
        
        // Show visual preparation cue
        const visualizer = document.getElementById('voiceVisualizer');
        const status = document.getElementById('voiceStatus');
        if (visualizer && status) {
            visualizer.classList.add('preparing');
            status.textContent = '⏳ Get ready...';
        }
        
        // Announce the timer start
        await this.speakAnnouncement(announcement);
        
        // Clear preparation cue
        if (visualizer && status) {
            visualizer.classList.remove('preparing');
        }
        
        // 🎭 MorphController removed - using CSS transitions instead
        
        // Small pause for clarity (0.3 seconds)
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // NOW start the actual timer
        this.startCountdownTimer();
    }
    
    getRandomTimerStartAnnouncement() {
        const announcements = this.timerStartAnnouncements;
        const randomIndex = Math.floor(Math.random() * announcements.length);
        let announcement = announcements[randomIndex];
        
        // Replace "15 seconds" with actual duration dynamically
        const duration = this.getTimerDuration();
        announcement = announcement.replace(/15 seconds?/gi, `${duration} ${duration === 1 ? 'second' : 'seconds'}`);
        
        return announcement;
    }
    
    startCountdownTimer() {
        // Stop any existing timer (but don't hide it - we're restarting)
        if (this.countdownTimer) {
            this.countdownTimer.stop();
        }
        
        // Get timer duration based on mode
        const duration = this.getTimerDuration();
        
        console.log(`⏱️ Starting ${duration}s countdown timer (mode: ${this.timerMode})`);
        
        // Create new timer
        this.countdownTimer = new CountdownTimer(duration, {
            soundboard: this.soundboard, // Pass soundboard for consistent audio
            onComplete: () => this.handleTimerExpired(),
            onWarning: (remaining) => console.log(`⚠️ Warning: ${remaining}s left`),
            onCritical: (remaining) => console.log(`🚨 Critical: ${remaining}s left`),
            soundEnabled: true,
            warningThreshold: 5,
            criticalThreshold: 3
        });
        
        // Start the timer
        this.countdownTimer.start();
        
        // ENABLE input now that timer has started
        const spellingInput = document.getElementById('spellingInput');
        if (spellingInput) {
            spellingInput.disabled = false;
            spellingInput.placeholder = 'Type your answer...';
            
            // 🍎 iOS FIX: Delay focus slightly to ensure keyboard shows properly
            if (this.isIOS || this.isSafari) {
                setTimeout(() => {
                    spellingInput.focus();
                }, 150);
            } else {
                spellingInput.focus();
            }
        }
    }
    
    getTimerDuration() {
        // Dynamic mode: adjust time based on word length
        if (this.timerMode === 'dynamic' && this.currentWordData && this.currentWordData.word) {
            const wordLength = this.currentWordData.word.length;
            if (wordLength <= 5) return 10;
            if (wordLength <= 9) return 15;
            return 20;
        }
        
        // Preset modes (Updated for 60s system)
        const durations = {
            'easy': 90,      // 90 seconds for easy mode
            'normal': 60,    // 60 seconds for normal mode  
            'challenge': 30  // 30 seconds for challenge mode
        };
        
        return durations[this.timerMode] || 60; // Default to 60s
    }
    
    handleTimerExpired() {
        console.log('⏰ Timer expired! Auto-advancing to next word...');
        
        // Mark as incorrect/missed
        this.incorrectCount++;
        this.currentStreak = 0; // Reset streak
        
        // Show timeout message
        const feedbackArea = document.getElementById('feedbackArea');
        feedbackArea.className = 'feedback-area feedback-error';
        feedbackArea.style.display = 'block';
        feedbackArea.textContent = '⏰ Time\'s up! Moving to the next word... (Marked as missed)';
        
        // Speak the timeout message
        this.speakAnnouncement('Times up! Moving to the next word.');
        
        // Update stats display
        this.updateScoreDisplay({
            correct: this.correctCount,
            incorrect: this.incorrectCount,
            streak: this.currentStreak
        });
        
        // Wait 3 seconds, then auto-advance to next word
        setTimeout(() => {
            this.loadNextWord();
        }, 3000);
    }
    
    stopCountdownTimer() {
        if (this.countdownTimer) {
            this.countdownTimer.stop();
        }
    }
    
    pauseCountdownTimer() {
        if (this.countdownTimer) {
            this.countdownTimer.pause();
        }
    }
    
    resumeCountdownTimer() {
        if (this.countdownTimer) {
            this.countdownTimer.resume();
        }
    }
    
    // 🏆 Points Calculation System
    calculatePoints(word, timeRemaining, isFirstAttempt, hintsUsed) {
        if (!this.pointsEnabled) return 0;
        
        const basePoints = 100;
        
        // Time bonus: 0-100 points based on time remaining
        const timeBonus = Math.floor((timeRemaining / this.timerDuration) * 100);
        
        // Difficulty multiplier based on word length
        let difficultyMultiplier = 1.0;
        const wordLength = word.length;
        if (wordLength >= 13) {
            difficultyMultiplier = 2.5;  // Very long words
        } else if (wordLength >= 9) {
            difficultyMultiplier = 2.0;  // Long words
        } else if (wordLength >= 6) {
            difficultyMultiplier = 1.5;  // Medium words
        } else {
            difficultyMultiplier = 1.0;  // Short words
        }
        
        // Calculate subtotal with multiplier
        let points = (basePoints + timeBonus) * difficultyMultiplier;
        
        // Add bonuses
        if (isFirstAttempt) {
            points += 50;  // First attempt bonus
        }
        
        // Hint penalty: Reduce points by 30% if hint was used
        if (hintsUsed) {
            const hintPenalty = Math.floor(points * 0.3); // 30% penalty
            points -= hintPenalty;
            console.log(`💡 Hint penalty applied: -${hintPenalty} points (30% reduction)`);
        } else {
            points += 25;  // No hints bonus
        }
        
        // Streak bonus
        points += this.currentStreak * 10;
        
        return Math.floor(points);
    }
    
    // Display points earned
    displayPointsEarned(points, breakdown) {
        const feedbackArea = document.getElementById('feedbackArea');
        
        // Create detailed points breakdown
        let pointsHtml = '<div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 20px; border-radius: 15px; margin: 15px 0; color: #4A2C2A;">';
        pointsHtml += '<h3 style="margin: 0 0 15px 0; font-size: 1.3em;">🎯 Points Earned!</h3>';
        pointsHtml += '<div style="background: rgba(255,255,255,0.3); padding: 15px; border-radius: 10px; text-align: left;">';
        pointsHtml += `<div style="margin: 5px 0;">📊 Base: ${breakdown.base} points</div>`;
        pointsHtml += `<div style="margin: 5px 0;">⏱️ Time Bonus: ${breakdown.timeBonus} points</div>`;
        if (breakdown.difficulty > 1.0) {
            pointsHtml += `<div style="margin: 5px 0;">💪 Difficulty: ×${breakdown.difficulty}</div>`;
        }
        if (breakdown.firstAttempt) {
            pointsHtml += `<div style="margin: 5px 0;">🎯 First Attempt: +50 points</div>`;
        }
        if (breakdown.hintPenalty && breakdown.hintPenalty > 0) {
            pointsHtml += `<div style="margin: 5px 0; color: #FF6B00;">💡 Hint Used: -${breakdown.hintPenalty} points (30% penalty)</div>`;
        } else if (breakdown.noHints) {
            pointsHtml += `<div style="margin: 5px 0;">🧠 No Hints: +25 points</div>`;
        }
        if (breakdown.streakBonus > 0) {
            pointsHtml += `<div style="margin: 5px 0;">🔥 Streak Bonus: +${breakdown.streakBonus} points</div>`;
        }
        pointsHtml += '<hr style="margin: 10px 0; border: 1px solid rgba(74,44,42,0.3);">';
        pointsHtml += `<div style="font-size: 1.5em; font-weight: bold; margin-top: 10px;">💰 Total: ${points.toLocaleString()} points!</div>`;
        pointsHtml += '</div>';
        pointsHtml += `<div style="margin-top: 15px; font-size: 1.1em;">🏆 Session Total: ${this.sessionPoints.toLocaleString()} points</div>`;
        pointsHtml += '</div>';
        
        const currentFeedback = feedbackArea.innerHTML;
        feedbackArea.innerHTML = currentFeedback + pointsHtml;
    }
    
    // 🍯 Show animated points popup
    showPointsPopup(points, breakdown) {
        // Remove any existing popup
        const existingPopup = document.querySelector('.points-popup');
        if (existingPopup) {
            existingPopup.remove();
        }
        
        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'points-popup';
        
        // Check if this is a retry attempt (33% points)
        const isRetry = this.isRetryAttempt;
        
        // Build breakdown HTML
        let breakdownHTML = '';
        if (breakdown.base) {
            breakdownHTML += `<div class="points-breakdown-item"><span>Base</span><span>+${breakdown.base}</span></div>`;
        }
        if (breakdown.time_bonus) {
            breakdownHTML += `<div class="points-breakdown-item"><span>⏱️ Time Bonus</span><span>+${breakdown.time_bonus}</span></div>`;
        }
        if (breakdown.streak_bonus) {
            breakdownHTML += `<div class="points-breakdown-item"><span>🔥 Streak</span><span>+${breakdown.streak_bonus}</span></div>`;
        }
        if (breakdown.first_attempt) {
            breakdownHTML += `<div class="points-breakdown-item"><span>🎯 First Try</span><span>+${breakdown.first_attempt}</span></div>`;
        }
        if (breakdown.hint_penalty && breakdown.hint_penalty > 0) {
            breakdownHTML += `<div class="points-breakdown-item" style="color: #FF6B00;"><span>💡 Hint Used</span><span>-${breakdown.hint_penalty}</span></div>`;
        } else if (breakdown.no_hints) {
            breakdownHTML += `<div class="points-breakdown-item"><span>🧠 No Hints</span><span>+${breakdown.no_hints}</span></div>`;
        }
        
        // Add retry penalty indicator if this is a retry
        if (isRetry) {
            breakdownHTML += `<div class="points-breakdown-item" style="color: #FF9800; font-weight: 600;"><span>🔄 Retry Penalty</span><span>-67% points</span></div>`;
        }
        
        popup.innerHTML = `
            <div class="points-total">+${points.toLocaleString()}</div>
            ${breakdownHTML ? `<div class="points-breakdown">${breakdownHTML}</div>` : ''}
            ${isRetry ? '<div style="font-size: 0.75rem; color: #FF9800; margin-top: 0.5rem;">Points deducted due to retry attempt</div>' : ''}
        `;
        
        document.body.appendChild(popup);
        
        // Create sparkle particles
        this.createBuzzDustSparkles(points);
        
        // Auto-remove after animation completes (2.5s)
        setTimeout(() => {
            popup.remove();
        }, 2500);
        
        console.log(`🍯 Displayed points popup: +${points} points${isRetry ? ' (Retry)' : ''} with sparkles!`);
    }
    
    // ✨ Create sparkle particles for Buzz Dust celebration
    createBuzzDustSparkles(points) {
        // More sparkles for higher points
        const sparkleCount = Math.min(Math.floor(points / 10) + 15, 50);
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        
        for (let i = 0; i < sparkleCount; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'buzz-dust-sparkle';
            
            // Random position around center
            const angle = (Math.PI * 2 * i) / sparkleCount;
            const radius = 50 + Math.random() * 100;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            sparkle.style.left = x + 'px';
            sparkle.style.top = y + 'px';
            sparkle.style.animationDelay = (Math.random() * 0.3) + 's';
            
            document.body.appendChild(sparkle);
            
            // Remove after animation
            setTimeout(() => sparkle.remove(), 1500);
        }
        
        // Add star bursts
        for (let i = 0; i < 5; i++) {
            const star = document.createElement('div');
            star.className = 'star-burst';
            star.textContent = ['✨', '⭐', '💫', '🌟'][Math.floor(Math.random() * 4)];
            
            const angle = (Math.PI * 2 * i) / 5;
            const radius = 80;
            star.style.left = (centerX + Math.cos(angle) * radius) + 'px';
            star.style.top = (centerY + Math.sin(angle) * radius) + 'px';
            star.style.animationDelay = (i * 0.1) + 's';
            
            document.body.appendChild(star);
            
            setTimeout(() => star.remove(), 1200);
        }
    }
    
    // 🏆 Badge Achievement System
    createConfetti() {
        const colors = ['#FFD700', '#FFA500', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.top = '-10px';
            confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            document.body.appendChild(confetti);
            
            // Remove after animation completes
            setTimeout(() => confetti.remove(), 3000);
        }
    }
    
    async showBadgeUnlock(badge) {
        return new Promise((resolve) => {
            // Create confetti effect
            this.createConfetti();
            
            // Create sparkles
            this.createBuzzDustSparkles(badge.points || 500);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'badge-modal';
            
            modal.innerHTML = `
                <div class="badge-modal-content">
                    <div class="badge-icon">${badge.icon}</div>
                    <h2>Achievement Unlocked!</h2>
                    <h3>${badge.name}</h3>
                    <p>${badge.message}</p>
                    <p class="badge-points">+${badge.points} Bonus Points!</p>
                    <button class="badge-continue-btn" onclick="this.closest('.badge-modal').remove()">
                        Continue
                    </button>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Speak achievement
            this.speakAnnouncement(`Achievement unlocked! ${badge.name}! You earned ${badge.points} bonus points!`);
            
            // Auto-continue after 5 seconds (in case user doesn't click)
            setTimeout(() => {
                if (document.body.contains(modal)) {
                    modal.remove();
                    resolve();
                }
            }, 5000);
            
            // Manual continue button
            modal.querySelector('.badge-continue-btn').addEventListener('click', () => {
                modal.remove();
                resolve();
            });
            
            console.log(`🏆 Badge unlocked: ${badge.name} (+${badge.points} points)`);
        });
    }
    
    async showAllBadges(badges) {
        console.log(`🏆 Showing ${badges.length} badge(s)`);
        
        for (const badge of badges) {
            await this.showBadgeUnlock(badge);
            // Small delay between badges if multiple
            if (badges.indexOf(badge) < badges.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
    }
    
    // 🎯 Level Progression System
    async showLevelUp(levelUpData) {
        return new Promise((resolve) => {
            // Create massive confetti explosion!
            this.createConfetti();
            setTimeout(() => this.createConfetti(), 300);
            setTimeout(() => this.createConfetti(), 600);
            
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'level-up-modal';
            
            const newLevel = levelUpData.new_level;
            const oldLevel = levelUpData.old_level;
            
            modal.innerHTML = `
                <div class="level-up-content">
                    <div class="level-up-title">🎉 LEVEL UP! 🎉</div>
                    <div class="level-up-icon-large">${newLevel.icon}</div>
                    <div class="level-up-tier">${newLevel.tier}</div>
                    <div class="level-up-message">${levelUpData.message}</div>
                    <div class="level-progress-display">
                        <p><strong>${oldLevel.tier}</strong> ${oldLevel.icon} → <strong>${newLevel.tier}</strong> ${newLevel.icon}</p>
                        <p>Level ${oldLevel.level} → Level ${newLevel.level}</p>
                        <p>🏆 ${newLevel.points_current.toLocaleString()} Total Points</p>
                        ${newLevel.is_max_level ? 
                            '<p style="color: #D32F2F; font-weight: 800;">👑 MAX LEVEL REACHED! 👑</p>' : 
                            `<p>Next: ${newLevel.points_to_next.toLocaleString()} points to next level</p>`
                        }
                    </div>
                    <button class="level-continue-btn">
                        Awesome! Let's Continue!
                    </button>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Speak level up
            this.speakAnnouncement(`Amazing! You leveled up! You are now a ${newLevel.tier}!`);
            
            // Auto-continue after 8 seconds
            setTimeout(() => {
                if (document.body.contains(modal)) {
                    modal.remove();
                    resolve();
                }
            }, 8000);
            
            // Manual continue button
            modal.querySelector('.level-continue-btn').addEventListener('click', () => {
                modal.remove();
                resolve();
            });
            
            console.log(`🎯 Level up! ${oldLevel.tier} (Lv ${oldLevel.level}) → ${newLevel.tier} (Lv ${newLevel.level})`);
        });
    }
    
    getRandomFeedback(isCorrect) {
        const feedbackArray = isCorrect ? this.positiveFeedback : this.negativeFeedback;
        const randomIndex = Math.floor(Math.random() * feedbackArray.length);
        let feedback = feedbackArray[randomIndex];
        
        // Randomly add student name (15% chance - more sporadic) at the beginning, middle, or end
        if (this.studentName && Math.random() < 0.15) {
            const position = Math.floor(Math.random() * 3); // 0, 1, or 2
            const nameVariations = [
                this.studentName,
                `${this.studentName}!`,
                this.studentName
            ];
            const chosenName = nameVariations[Math.floor(Math.random() * nameVariations.length)];
            
            if (position === 0) {
                // Add at beginning: "Sarah, 🐝 BEE-utiful!..."
                feedback = `${chosenName}, ${feedback.charAt(0).toLowerCase()}${feedback.slice(1)}`;
            } else if (position === 1) {
                // Add in middle after first sentence
                const sentences = feedback.split('!');
                if (sentences.length > 1) {
                    feedback = `${sentences[0]}! ${chosenName}, ${sentences.slice(1).join('!').trim()}`;
                } else {
                    // Fallback to beginning if no second sentence
                    feedback = `${chosenName}, ${feedback}`;
                }
            } else {
                // Add at end: "...Perfect spelling, Sarah!"
                feedback = feedback.replace(/!$/, `, ${chosenName}!`);
            }
        }
        
        return feedback;
    }
    
    getRandomAudioAnnouncement(isCorrect) {
        const announcementArray = isCorrect ? this.correctAnnouncements : this.incorrectAnnouncements;
        const randomIndex = Math.floor(Math.random() * announcementArray.length);
        const base = announcementArray[randomIndex];

        // Occasionally personalize with name; mostly do it with a deliberate pause
        // between the phrase and the name so it sounds natural.
        if (this.studentName && Math.random() < 0.12) { // ~12% of the time
            // 70%: split into two utterances (phrase, then name after a short pause)
            if (Math.random() < 0.7) {
                return {
                    phrase: base,               // speak the core message first
                    name: this.studentName,     // then speak just the name
                    pauseMs: 380                // ~0.38s pause feels natural with our cadence
                };
            }
            // 30%: inline the name for variety (fallback to commas)
            if (Math.random() < 0.5) {
                return `${this.studentName}, ${base.charAt(0).toLowerCase()}${base.slice(1)}`;
            } else {
                return base.replace(/!$/, `, ${this.studentName}!`);
            }
        }

        return base;
    }

    initializeEventListeners() {
        const spellingInput = document.getElementById('spellingInput');
        const submitButton = document.getElementById('submitButton');
        const speakButton = document.getElementById('speakButton');
        const repeatButton = document.getElementById('repeatButton');
        const getHintButton = document.getElementById('getHintButton');
        const skipButton = document.getElementById('skipButton');
        const restartButton = document.getElementById('restartButton');

        // Add buzz sounds to all buttons
        const allButtons = [submitButton, speakButton, repeatButton, getHintButton, skipButton, restartButton];
        allButtons.forEach(button => {
            if (button) {
                // Hover sound
                button.addEventListener('mouseenter', () => {
                    this.soundboard?.play('buzz-hover');
                });
                
                // Click sound (support both mouse and touch)
                button.addEventListener('mousedown', () => {
                    this.soundboard?.play('buzz-click');
                });
                
                // 🍎 iOS FIX: Add touch event for better iOS button responsiveness
                button.addEventListener('touchstart', (e) => {
                    this.soundboard?.play('buzz-click');
                    // Prevent duplicate mouse event on iOS
                    if (this.isIOS || this.isSafari) {
                        e.preventDefault();
                    }
                }, { passive: false });
            }
        });

        submitButton.addEventListener('click', () => {
            try { window.BeeVoiceViz?.react('submit'); } catch (e) {}
            this.submitAnswer();
        });
        
        // 🍎 iOS FIX: Add touch event for submit button to prevent iOS double-tap delay
        submitButton.addEventListener('touchend', (e) => {
            if (this.isIOS || this.isSafari) {
                e.preventDefault();
                try { window.BeeVoiceViz?.react('submit'); } catch (err) {}
                this.submitAnswer();
            }
        }, { passive: false });
        spellingInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter' && !this.isAnswering) {
                try { window.BeeVoiceViz?.react('submit'); } catch (e) {}
                this.submitAnswer();
            }
        });

        if (speakButton) {
            speakButton.addEventListener('click', () => {
                console.log('🔊 Pronounce button clicked');
                try { window.BeeVoiceViz?.react('button'); } catch (e) {}
                this.pronounceWordSlow(); // Pronounce at slower speed for learning
            });
        }

        if (repeatButton) {
            repeatButton.addEventListener('click', () => {
                console.log('🔁 Repeat button clicked');
                try { window.BeeVoiceViz?.react('button'); } catch (e) {}
                this.repeatWord(); // Repeat at normal speed
            });
        }

        getHintButton.addEventListener('click', () => {
            try { window.BeeVoiceViz?.react('hint'); } catch (e) {}
            this.getDefinition({ refresh: true });
        });
        skipButton.addEventListener('click', () => {
            try { window.BeeVoiceViz?.react('skip'); } catch (e) {}
            this.skipWord();
        });
        
        // Definition and Sentence Helper Buttons
        const showDefinitionButton = document.getElementById('showDefinitionButton');
        const showSentenceButton = document.getElementById('showSentenceButton');
        
        if (showDefinitionButton) {
            showDefinitionButton.addEventListener('click', () => {
                try { window.BeeVoiceViz?.react('hint'); } catch (e) {}
                this.showDefinition();
            });
        }
        
        if (showSentenceButton) {
            showSentenceButton.addEventListener('click', () => {
                try { window.BeeVoiceViz?.react('hint'); } catch (e) {}
                this.showSentence();
            });
        }
        
        // Stat Toggle Controls
        const toggleButtons = document.querySelectorAll('.toggle-stat');
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                try { window.BeeVoiceViz?.react('button'); } catch (e) {}
                const stat = button.getAttribute('data-stat');
                this.toggleStat(stat, button);
            });
        });
        
        // Retry button
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.addEventListener('click', () => {
                try { window.BeeVoiceViz?.react('button'); } catch (e) {}
                this.handleRetry();
            });
        }
        
        restartButton.addEventListener('click', () => this.restartQuiz());

        // Voice toggle button
        const voiceToggleBtn = document.getElementById('voiceToggleBtn');
        if (voiceToggleBtn) {
            voiceToggleBtn.addEventListener('click', () => this.toggleAnnouncer());
        }

        // Music toggle button
        const musicToggleBtn = document.getElementById('musicToggleBtn');
        if (musicToggleBtn) {
            musicToggleBtn.addEventListener('click', () => this.toggleMusic());
        }

        spellingInput.focus();
    }

    // Show voice intro modal for iOS/Safari
    showVoiceIntroModal() {
        const modal = document.getElementById('voiceIntroModal');
        const enableVoiceBtn = document.getElementById('enableVoiceBtn');
        const skipVoiceBtn = document.getElementById('skipVoiceBtn');
        
        if (!modal) return;
        
        modal.style.display = 'flex';
        
        // Enable voice button - unlocks voice and starts quiz with intro
        enableVoiceBtn.addEventListener('click', () => {
            this.voiceUnlocked = true;
            this.announcerEnabled = true;
            localStorage.setItem('announcerEnabled', 'true');
            sessionStorage.setItem('voiceIntroShown', 'true');
            modal.style.display = 'none';
            this.updateVoiceToggleUI();
            this.showIntroAnnouncer();
        }, { once: true });
        
        // Skip voice button - disables announcer and starts quiz silently
        skipVoiceBtn.addEventListener('click', () => {
            this.voiceUnlocked = false;
            this.announcerEnabled = false;
            localStorage.setItem('announcerEnabled', 'false');
            sessionStorage.setItem('voiceIntroShown', 'true');
            modal.style.display = 'none';
            this.updateVoiceToggleUI();
            // Don't call showIntroAnnouncer - just start quiz silently
            this.loadNextWord();
        }, { once: true });
    }

    // Toggle announcer voice on/off
    toggleAnnouncer() {
        this.announcerEnabled = !this.announcerEnabled;
        localStorage.setItem('announcerEnabled', this.announcerEnabled ? 'true' : 'false');
        
        // If enabling on iOS and not unlocked, we need user interaction to unlock
        if (this.announcerEnabled && (this.isIOS || this.isSafari) && !this.voiceUnlocked) {
            // Unlock voice with a test utterance
            const testUtterance = new SpeechSynthesisUtterance('');
            window.speechSynthesis.speak(testUtterance);
            this.voiceUnlocked = true;
        }
        
        this.updateVoiceToggleUI();
        
        // Show feedback
        const message = this.announcerEnabled ? 
            "Buzzy voice is ON! Buzzy will announce your results!" : 
            "Buzzy voice is OFF. Quiz will be silent.";
        BeeSmart.showSuccess(message);
    }

    // Update voice toggle button UI
    updateVoiceToggleUI() {
        const icon = document.getElementById('voiceToggleIcon');
        const text = document.getElementById('voiceToggleText');
        
        if (icon && text) {
            if (this.announcerEnabled) {
                icon.textContent = 'ON';
                text.textContent = 'Mute Buzzy';
            } else {
                icon.textContent = 'OFF';
                text.textContent = 'Unmute Buzzy';
            }
        }
    }

    // Toggle background music on/off
    toggleMusic() {
        this.musicEnabled = !this.musicEnabled;
        localStorage.setItem('musicEnabled', this.musicEnabled ? 'true' : 'false');
        
        if (this.musicEnabled) {
            this.playBackgroundMusic();
        } else {
            this.stopBackgroundMusic();
        }
        
        this.updateMusicToggleUI();
        
        // Show feedback
        const message = this.musicEnabled ? 
            "Background music is ON!" : 
            "Background music is OFF.";
        BeeSmart.showSuccess(message);
    }

    // Update music toggle button UI
    updateMusicToggleUI() {
        const icon = document.getElementById('musicToggleIcon');
        const text = document.getElementById('musicToggleText');
        
        if (icon && text) {
            if (this.musicEnabled) {
                icon.textContent = 'ON';
                text.textContent = 'Music On';
            } else {
                icon.textContent = 'OFF';
                text.textContent = 'Music Off';
            }
        }
    }

    // Play background music
    playBackgroundMusic() {
        if (!this.backgroundMusic) {
            this.backgroundMusic = new Audio('/static/sounds/we-can-be-bees.mp3');
            this.backgroundMusic.loop = true;
            this.backgroundMusic.volume = 0.3; // Quiet background music
        }
        
        this.backgroundMusic.play().catch(err => {
            console.log('🎵 Background music play prevented:', err);
        });
    }

    // Stop background music
    stopBackgroundMusic() {
        if (this.backgroundMusic) {
            this.backgroundMusic.pause();
            this.backgroundMusic.currentTime = 0;
        }
    }

    // Show helper notification if user can't hear announcer
    showVoiceHelperNotification() {
        // Don't show if already dismissed this session
        if (sessionStorage.getItem('voiceHelperDismissed')) {
            return;
        }
        
        const notification = document.createElement('div');
        notification.id = 'voiceHelperNotification';
        notification.style.cssText = `
            position: fixed;
            top: 120px;
            right: 20px;
            background: linear-gradient(135deg, #FF6B00 0%, #FFD700 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(255, 107, 0, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.3);
            z-index: 1500;
            max-width: 320px;
            animation: slideInRight 0.5s ease-out;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="font-size: 2.5rem;">🔊</div>
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                        Can't hear Buzzy?
                    </div>
                    <div style="font-size: 0.95rem; margin-bottom: 1rem; line-height: 1.4;">
                        If you can't hear the announcer, tap the <strong>Mute/Unmute button</strong> below the quiz to enable voice!
                    </div>
                    <button id="dismissVoiceHelper" style="
                        background: white;
                        color: #FF6B00;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        cursor: pointer;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                        width: 100%;
                    ">
                        Got it! 👍
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Dismiss button handler
        document.getElementById('dismissVoiceHelper').addEventListener('click', () => {
            sessionStorage.setItem('voiceHelperDismissed', 'true');
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto-dismiss after 12 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                sessionStorage.setItem('voiceHelperDismissed', 'true');
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 12000);
    }

    async loadNextWord() {
        console.log('🔄 loadNextWord() called - starting to load next word...');
        try {
            // 🎭 MorphController removed - using CSS transitions instead
            
            this.lastPronounceData = null;
            // Reset hint tracking for new word
            this.hintUsedThisWord = false;
            
            // 🔄 Reset retry system for new word
            this.retryAvailable = false;
            this.hasRetried = false;
            this.isRetryAttempt = false;
            this.clearRetryCountdown();
            this.hideRetryButton();
            // Hide next word button
            const nextWordBtn = document.getElementById('nextWordButton');
            if (nextWordBtn) nextWordBtn.style.display = 'none';
            
            console.log('🔄 Fetching /api/next...');
            const response = await fetch('/api/next', { 
                method: 'POST',
                credentials: 'same-origin'
            });
            console.log('🔄 /api/next response received, status:', response.status);
            const data = await response.json();
            console.log('🔄 /api/next data:', data);

            if (response.status !== 200 || data.error) {
                console.error('❌ API Error from /api/next:', data);
                BeeSmart.showError(data.message || data.error || 'Failed to load the next word');
                return;
            }

            if (data.done) {
                console.log('🏁 Quiz complete - showing summary');
                // Announce quiz ending before showing report card
                await this.announceQuizEnding();
                this.showQuizComplete(data.summary);
                return;
            }
            
            console.log('✅ Got next word data, processing...');

            const questionNumber = data.index ?? data.number ?? 1;
            this.totalWords = data.total ?? this.totalWords;
            
            // Update progress displays (both text and percentage)
            this.updateProgressDisplays(questionNumber, data.total ?? this.totalWords);

            if (data.progress) {
                this.updateScoreDisplay({ ...data.progress, total: data.total });
            }

            this.delight?.setTotalQuestions(data.total);

            // Set the definition directly from the /api/next response - prefer explicit fields
            const defBox = document.getElementById('definitionDisplay');
            console.log('DEBUG loadNextWord: /api/next response:', {
                sentence: data.sentence,
                hint: data.hint,
                definition: data.definition,
                word: data.word,
                fullData: data
            });
            
            let chosen = '';
            if (data.sentence) {
                console.log('✓ Using sentence:', data.sentence);
                chosen = data.sentence;
            } else if (data.hint) {
                console.log('✓ Using hint:', data.hint);
                chosen = `Hint: ${data.hint}`;
            } else if (data.definition) {
                console.log('✓ Using definition:', data.definition);
                chosen = data.definition;
            } else {
                console.log('⚠️ No definition found, attempting /api/pronounce fallback');
                // Last resort fallback: try /api/pronounce for sentence/hint
                const pronounce = await this.fetchPronounce(true);
                chosen =
                    (pronounce && (pronounce.sentence || pronounce.hint))
                        ? (pronounce.sentence || `Hint: ${pronounce.hint}`)
                        : 'Listen carefully and spell the word you hear.';
                console.log('Using fallback:', chosen);
            }
            
            // Apply safety blanker to hide target word if it appears in the definition
            const finalDefinition = hideTargetWord(chosen, data.word);
            defBox.textContent = finalDefinition;
            
            // Also update the voice visualizer definition
            const voiceDefBox = document.getElementById('voiceDefinition');
            if (voiceDefBox) {
                voiceDefBox.textContent = finalDefinition;
            }

            // Store the word data for pronunciation
            this.currentWordData = {
                word: data.word || '',
                definition: data.definition || ''
            };
            
            // Don't animate mascot on every question - keep it calm during gameplay
            // Mascot will only animate when answers are submitted

            // Announce the word like a real spelling bee, then pronounce it
            if (questionNumber === 1) {
                // First word already announced in intro
                await this.pronounceWord({ refresh: true });
            } else {
                // If this is the last word, announce it before giving the word
                if (this.totalWords && questionNumber === this.totalWords) {
                    const namePart = (this.studentName || '').trim();
                    const preface = namePart ? `${namePart}, this is your last word.` : `This is your last word.`;
                    await this.speakAnnouncement(preface);
                }
                // Subsequent words: consistent phrasing for clarity
                const phrase = `Your next word is: ${data.word}`;
                await this.speakAnnouncement(phrase);
                
                // Brief visual pause between phases, then auto‑pronounce
                {
                    const visualizer = document.getElementById('voiceVisualizer');
                    const status = document.getElementById('voiceStatus');
                    if (visualizer && status) {
                        visualizer.classList.add('pausing');
                        status.textContent = '⏸️ Pause...';
                    }
                    await new Promise(r => setTimeout(r, 500));
                    if (visualizer && status) {
                        visualizer.classList.remove('pausing');
                    }
                }
                
                await this.pronounceWord();
            }

            // ✅ Allow early typing — enable input immediately (no need to wait for timer)
            const spellingInput = document.getElementById('spellingInput');
            spellingInput.disabled = false;
            spellingInput.value = '';
            spellingInput.placeholder = 'Type your answer...';
            this.isAnswering = false; // Reset flag for new word
            console.log('✅ Input enabled and ready for answer');
            // Do not force focus here to avoid interrupting TTS; users can start typing anytime

            // Hide feedback area
            const feedbackArea2 = document.getElementById('feedbackArea');
            if (feedbackArea2) feedbackArea2.style.display = 'none';
            this.hideLetterHint();  // Hide letter hint for new word
            this.delight?.clearFeedbackState();
            
            // ⏱️ Give user mental processing time BEFORE timer announcement (800ms)
            if (this.timerEnabled && this.quizStarted) {
                console.log('⏸️ Pausing 800ms for mental processing before timer...');
                await new Promise(resolve => setTimeout(resolve, 800));
                await this.announceAndStartTimer();
            } else {
                // If timer is disabled, enable input immediately
                spellingInput.disabled = false;
                spellingInput.placeholder = 'Type your answer...';
                spellingInput.focus();
            }
        } catch (error) {
            console.error('Error loading next word:', error);
            BeeSmart.showError('Failed to load the next word. Please refresh the page.');
        }
    }

    async fetchPronounce(force = false) {
        if (!force && this.lastPronounceData) {
            return this.lastPronounceData;
        }

        try {
            const response = await fetch('/api/pronounce', { 
                method: 'POST',
                credentials: 'same-origin'
            });
            if (!response.ok) {
                console.warn('Pronounce API failed:', response.status);
                return null;
            }
            const data = await response.json();
            if (data.error) {
                console.warn('Pronounce API error:', data.error);
                return null;
            }
            this.lastPronounceData = data;
            return data;
        } catch (error) {
            console.warn('Pronounce API exception:', error);
            return null;
        }
    }

    async getQuizState() {
        try {
            const response = await fetch('/api/next', { 
                method: 'POST',
                credentials: 'same-origin'
            });
            if (!response.ok) {
                console.warn('Quiz state API failed:', response.status);
                return null;
            }
            const data = await response.json();
            if (data.error) {
                console.warn('Quiz state API error:', data.error);
                return null;
            }
            return data;
        } catch (error) {
            console.warn('Quiz state API exception:', error);
            return null;
        }
    }

    async getDefinition(options = {}) {
        try {
            if (options.refresh) {
                this.lastPronounceData = null;
                // Mark that hint was used for this word
                this.hintUsedThisWord = true;
                console.log('💡 Hint used - points will be reduced');
            }
            const data = await this.fetchPronounce(options.refresh);
            if (!data) {
                // Set a default message if API fails
                document.getElementById('definitionDisplay').textContent = 'Please spell the word you hear.';
                return;
            }

            const definitionElement = document.getElementById('definitionDisplay');
            
            // Format the definition in dictionary style
            const fullText = data.definition || 'Please spell the word you hear.';
            const pronunciation = data.phonetic || '';
            
            // Check if the definition contains "Fill in the blank:"
            if (fullText.includes('Fill in the blank:')) {
                const parts = fullText.split('Fill in the blank:');
                let definition = parts[0].trim();
                const sentence = parts[1] ? parts[1].trim() : '';
                
                // Remove emoji prefixes if present
                definition = definition.replace(/^[📖🔤📚]\s*/, '');
                
                // Extract word type if present (verb, noun, etc.)
                let wordType = '';
                const typeMatch = definition.match(/^\((verb|noun|adjective|adverb|pronoun|preposition|conjunction|interjection)\)/i);
                if (typeMatch) {
                    wordType = typeMatch[1];
                    definition = definition.replace(typeMatch[0], '').trim();
                }
                
                // Format with HTML for dictionary-style display
                definitionElement.innerHTML = `
                    ${pronunciation ? `<div class="pronunciation">🔊 [${pronunciation}]</div>` : ''}
                    ${wordType ? `<div class="word-type">${wordType}</div>` : ''}
                    <div class="word-definition"><span class="definition-number">1.</span>${definition}</div>
                    ${sentence ? `
                        <div class="sentence-example">
                            <span class="example-label">Example:</span>
                            <span class="example-text">${sentence}</span>
                        </div>
                    ` : ''}
                `;
            } else {
                // Clean format for simple definitions
                let cleanDef = fullText.replace(/^[📖🔤📚]\s*/, '');
                
                // Check for word type
                let wordType = '';
                const typeMatch = cleanDef.match(/^\((verb|noun|adjective|adverb|pronoun|preposition|conjunction|interjection)\)/i);
                if (typeMatch) {
                    wordType = typeMatch[1];
                    cleanDef = cleanDef.replace(typeMatch[0], '').trim();
                }
                
                definitionElement.innerHTML = `
                    ${pronunciation ? `<div class="pronunciation">🔊 [${pronunciation}]</div>` : ''}
                    ${wordType ? `<div class="word-type">${wordType}</div>` : ''}
                    <div class="word-definition"><span class="definition-number">1.</span>${cleanDef}</div>
                `;
            }
            
            // Show letter hint when user clicks "Honey Hint" button
            if (options.refresh) {
                this.showLetterHint();
                playThemedSound('hint-reveal');
                
                // Add bounce animation to definition
                definitionElement.classList.remove('hint-bounce');
                // Trigger reflow to restart animation
                void definitionElement.offsetWidth;
                definitionElement.classList.add('hint-bounce');
                
                // Remove animation class after it completes
                setTimeout(() => {
                    definitionElement.classList.remove('hint-bounce');
                }, 800);
            }
            
            if (!options.silent) {
                this.delight?.handleDefinition(data);
            } else {
                this.delight?.handleDefinition();
            }
        } catch (error) {
            console.error('Error getting definition:', error);
            // Set fallback message instead of breaking the quiz
            document.getElementById('definitionDisplay').textContent = 'Please spell the word you hear.';
        }
    }

    generateLetterHintPattern(word) {
        if (!word || word.length === 0) {
            return '';
        }
        
        const len = word.length;
        const letters = word.split('');
        let pattern = [];
        
        if (len === 1) {
            // Single letter - show the letter
            pattern = [letters[0]];
        } else if (len === 2) {
            // Two letters - show first and last
            pattern = [letters[0], letters[1]];
        } else if (len === 3) {
            // Three letters - show first and last, hide middle (e.g., d_g)
            pattern = [letters[0], '_', letters[2]];
        } else {
            // Four or more letters - show 1st, 3rd, and last
            for (let i = 0; i < len; i++) {
                if (i === 0 || i === 2 || i === len - 1) {
                    // Show 1st, 3rd, and last letter
                    pattern.push(letters[i]);
                } else {
                    // Hide other letters
                    pattern.push('_');
                }
            }
        }
        
        return pattern.join(' ');
    }

    showLetterHint() {
        const letterHintElement = document.getElementById('letterHint');
        const hintLettersElement = document.getElementById('hintLetters');
        
        if (!this.currentWordData || !this.currentWordData.word) {
            console.warn('No current word data available for letter hint');
            return;
        }
        
        const word = this.currentWordData.word;
        const hintPattern = this.generateLetterHintPattern(word);
        
        console.log(`💡 Showing letter hint for word (length ${word.length}): ${hintPattern}`);
        
        hintLettersElement.textContent = hintPattern;
        letterHintElement.classList.remove('hidden');
    }

    hideLetterHint() {
        const letterHintElement = document.getElementById('letterHint');
        letterHintElement.classList.add('hidden');
    }

    async pronounceWord({ refresh = false, rate = 1.0 } = {}) {
        try {
            // Play gentle tone before pronunciation
            playThemedSound('pronounce-word');
            
            // Animate voice visualizer during actual speech
            const visualizer = document.getElementById('voiceVisualizer');
            const status = document.getElementById('voiceStatus');
            
            // Use stored word data instead of API call
            if (this.currentWordData && this.currentWordData.word) {
                const data = {
                    word: this.currentWordData.word,
                    definition: this.currentWordData.definition,
                    rate: rate // Pass speech rate to handlers
                };
                
                // Start visualizer animation BEFORE speaking
                if (visualizer && status) {
                    console.log('🎤 Starting voice visualizer animation');
                    visualizer.classList.add('speaking');
                    status.textContent = rate < 1.0 ? '🐌 Speaking slowly...' : '🗣️ Speaking...';
                }
                
                // Return a promise that resolves when speech ends to allow precise sequencing
                return await new Promise((resolve) => {
                    const onDone = () => {
                        console.log('🎤 Stopping voice visualizer animation');
                        if (visualizer && status) {
                            visualizer.classList.remove('speaking');
                            status.textContent = '🐝 Ready';
                        }
                        resolve();
                    };
                    // Prefer delight handler when available, otherwise speak directly
                    // Just say the word once - it was already introduced in the announcement
                    if (this.delight && typeof this.delight.handlePronounce === 'function') {
                        try {
                            this.delight.handlePronounce(data, onDone);
                        } catch (e) {
                            console.warn('handlePronounce failed, falling back to direct TTS:', e);
                            const phrase = data.word; // Just the word, no repetition
                            this.soundboard && this.soundboard.speakWord ? this.soundboard.speakWord(phrase, onDone, rate) : this.speakDirectly(phrase, onDone, rate);
                        }
                    } else if (this.soundboard && typeof this.soundboard.speakWord === 'function') {
                        const phrase = data.word; // Just the word, no repetition
                        this.soundboard.speakWord(phrase, onDone, rate);
                    } else {
                        // Direct speech synthesis fallback
                        const phrase = data.word; // Just the word, no repetition
                        this.speakDirectly(phrase, onDone, rate);
                    }
                });
            } else {
                console.warn('No word data available for pronunciation');
            }
        } catch (error) {
            console.error('Unable to pronounce word:', error);
            BeeSmart.showError('Could not pronounce the word right now. Please try again.');
            // Ensure visualizer stops on error
            const visualizer = document.getElementById('voiceVisualizer');
            const status = document.getElementById('voiceStatus');
            if (visualizer && status) {
                visualizer.classList.remove('speaking');
                status.textContent = '🐝 Ready';
            }
        }
    }

    // Direct speech synthesis fallback
    speakDirectly(text, onDone, rate = 1.0) {
        if ('speechSynthesis' in window) {
            try {
                speechSynthesis.cancel(); // Cancel any ongoing speech
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = rate;
                utterance.pitch = 1.0;
                utterance.volume = 0.9;
                
                // Use the same female voice selection as other speech methods
                if (this.cachedVoice) {
                    utterance.voice = this.cachedVoice;
                    console.log(`Using cached female voice: ${this.cachedVoice.name}`);
                } else {
                    // Try to select best female voice if not cached yet
                    const femaleVoice = this.selectBestFemaleVoice();
                    if (femaleVoice) {
                        utterance.voice = femaleVoice;
                        this.cachedVoice = femaleVoice;
                        console.log(`Selected female voice: ${femaleVoice.name}`);
                    }
                }
                
                utterance.onend = () => {
                    console.log('Direct speech synthesis completed');
                    if (onDone) onDone();
                };
                
                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event);
                    if (onDone) onDone();
                };
                
                speechSynthesis.speak(utterance);
                console.log(`Direct speech synthesis started: "${text}" at rate ${rate}`);
            } catch (error) {
                console.error('Speech synthesis failed:', error);
                if (onDone) onDone();
            }
        } else {
            console.warn('Speech synthesis not supported');
            if (onDone) onDone();
        }
    }

    // Pronounce word at slower speed for learning
    async pronounceWordSlow() {
        return await this.pronounceWord({ rate: 0.7 });
    }

    // Repeat word at normal speed
    async repeatWord() {
        return await this.pronounceWord({ rate: 1.0 });
    }

    async submitAnswer() {
        if (this.isAnswering) {
            return;
        }

        const spellingInput = document.getElementById('spellingInput');
        // 🍎 iOS FIX: Normalize text for iOS compatibility (remove zero-width chars, normalize unicode)
        let userInput = spellingInput.value.trim();
        
        // Remove zero-width characters that iOS keyboard might insert
        userInput = userInput.replace(/[\u200B-\u200D\uFEFF]/g, '');
        
        // Normalize unicode (iOS may use different unicode representations)
        if (userInput.normalize) {
            userInput = userInput.normalize('NFC');
        }

        if (!userInput) {
            BeeSmart.showError('Please enter your spelling first!');
            spellingInput.focus();
            return;
        }

        this.isAnswering = true;
        // Keep submit button enabled - only disable input field
        document.getElementById('spellingInput').disabled = true;
        
        // ⏱️ Stop countdown timer when answer submitted
        this.stopCountdownTimer();

        try {
            const response = await fetch('/api/answer', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_input: userInput,
                    method: 'keyboard',
                    elapsed_ms: 0
                })
            });

            if (!response.ok) {
                let errorMsg = 'Failed to submit answer';
                try {
                    const error = await response.json();
                    errorMsg = error.error || errorMsg;
                } catch (e) {
                    console.warn('Failed to parse error response as JSON:', e);
                }
                BeeSmart.showError(errorMsg);
                this.enableInput();
                return;
            }

            const result = await response.json();
            
            // 🍯 Update points from backend response
            if (result.points) {
                this.sessionPoints = result.points.session_total || this.sessionPoints;
                this.maxStreak = result.points.max_streak || this.maxStreak;
            }
            
            // Show feedback and wait for announcement to complete
            await this.showFeedback(result);
            
            this.updateScoreDisplay(result.progress);
            
            // 🔄 CRITICAL FIX: If answer was INCORRECT, STOP HERE and wait for user choice
            if (!result.correct) {
                console.log('❌ INCORRECT - Halting auto-advance. Waiting for user to click Retry or Show Answer...');
                // DON'T load next word - wait for user to make a choice via retry buttons
                this.isAnswering = false;
                // Note: Next Word button will be shown by showRetryUI if retry window closes
                return;  // ⬅️ STOP HERE - DON'T CONTINUE
            }
            
            // 🏆 Check if quiz is complete and show badges/level-up
            if (result.quiz_complete) {
                console.log(`🏆 Quiz complete!`);
                
                // Small delay, then show all achievements and completion
                setTimeout(async () => {
                    // Show badges first (if any)
                    if (result.badges && result.badges.length > 0) {
                        console.log(`🏆 ${result.badges.length} badge(s) earned!`);
                        await this.showAllBadges(result.badges);
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                    
                    // 🎯 Show level up modal (if leveled up)
                    if (result.level_up && result.level_up.leveled_up) {
                        console.log(`🎯 Level up detected!`);
                        playThemedSound('level-up');
                        await this.showLevelUp(result.level_up);
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                    
                    // 🏁 Now get the final quiz summary and show completion
                    console.log('🏁 Fetching final quiz summary for report card...');
                    try {
                        const summaryResponse = await fetch('/api/next', { 
                            method: 'POST',
                            credentials: 'same-origin'
                        });
                        const summaryData = await summaryResponse.json();
                        
                        if (summaryData.done && summaryData.summary) {
                            this.showQuizComplete(summaryData.summary);
                        } else {
                            console.error('Expected quiz summary but got:', summaryData);
                            BeeSmart.showError('Could not load quiz results. Please try refreshing.');
                        }
                    } catch (error) {
                        console.error('Failed to fetch quiz summary:', error);
                        BeeSmart.showError('Could not load quiz results. Please try refreshing.');
                    }
                }, 1500);
            } else {
                // Normal flow (CORRECT answer): Show definition and celebrations
                if (!result.quiz_complete) {
                    // Show word definition popup for educational value
                    if (result.word_definition) {
                        showWordDefinitionPopup(result.correct_spelling, result.word_definition);
                    }
                    
                    // Show streak milestone celebration
                    if (result.streak_milestone) {
                        this.showStreakCelebration(result.streak_milestone);
                    }
                    
                    // Play success sound
                    if (this.soundboard && typeof this.soundboard.play === 'function') {
                        this.soundboard.play('correct');
                    }
                    
                    // CRITICAL: Reset isAnswering BEFORE setTimeout to allow new submissions
                    this.isAnswering = false;
                    
                    // Auto-advance to next word after brief delay (1200ms for tighter response)
                    console.log('✅ Correct answer - auto-advancing to next word in 1200ms');
                    console.log('DEBUG: quizStarted =', this.quizStarted, ', timerEnabled =', this.timerEnabled);
                    setTimeout(async () => {
                        console.log('🔄 Loading next word now...');
                        console.log('DEBUG: About to call loadNextWord(), quizStarted =', this.quizStarted);
                        try {
                            await this.loadNextWord();
                            console.log('✅ Next word loaded successfully');
                        } catch (err) {
                            console.error('❌ ERROR in loadNextWord():', err);
                            BeeSmart.showError('Failed to load next word. Please refresh the page.');
                            // Show Next Word button as fallback
                            this.showNextWordButton();
                        }
                    }, 1200);
                } else {
                    console.log('🏆 Quiz complete - skipping loadNextWord in normal flow');
                }
            }
            
        } catch (error) {
            console.error('❌ submitAnswer error:', error);
            console.error('Error details:', error.message, error.stack);
            BeeSmart.showError('Network error. Please try again.');
            this.enableInput();
            this.isAnswering = false;
        }
    }

    async showFeedback(result) {
        // 🎭 MorphController removed - using CSS transitions instead
        
        try { window.BeeVoiceViz?.react(result?.correct ? 'feedback-correct' : 'feedback-incorrect'); } catch (e) {}
        const feedbackArea = document.getElementById('feedbackArea');
        feedbackArea.style.display = 'block';
        
        // Use randomized feedback instead of server message
        const randomMessage = this.getRandomFeedback(result.correct);
        
    // Get audio announcement (may be a string or an object {phrase, name, pauseMs})
    const audioAnnouncement = this.getRandomAudioAnnouncement(result.correct);

        if (result.correct) {
            // 🏆 Use points from backend response
            const pointsData = result.points || {};
            let earnedPoints = pointsData.earned || 0;
            const breakdown = pointsData.breakdown || {};
            
            // 🔄 RETRY PENALTY: If this is a retry attempt, only award 33% of points
            if (this.isRetryAttempt) {
                const originalPoints = earnedPoints;
                earnedPoints = Math.floor(earnedPoints * 0.33);
                console.log(`🔄 Retry penalty applied: ${originalPoints} → ${earnedPoints} (33%)`);
            }
            
            // Update streak
            this.currentStreak = result.progress?.streak || this.currentStreak;
            if (this.currentStreak > this.maxStreak) {
                this.maxStreak = this.currentStreak;
            }
            
            feedbackArea.className = 'feedback-area feedback-success';
            feedbackArea.innerHTML = `
                <div style="font-size: 1.15rem; font-weight: 700;">${randomMessage}</div>
                ${this.isRetryAttempt ? '<div style="color: #FF9800; font-weight: 600; margin-top: 0.3rem;">🔄 Retry: 33% points awarded</div>' : ''}
                <div style="margin-top: 0.5rem;">Moving to the next word...</div>
            `;
            
            // Mascot celebrates!
            if (this.smartyBee) {
                this.smartyBee.onCorrectAnswer();
            }
            
            // Enhanced correct answer celebration
            playThemedSound('correct');
            
            // Audio announcement - may include a separate name utterance after a short pause
            if (typeof audioAnnouncement === 'string') {
                await this.speakAnnouncement(audioAnnouncement);
            } else if (audioAnnouncement && audioAnnouncement.phrase) {
                await this.speakAnnouncement(audioAnnouncement.phrase);
                await new Promise(r => setTimeout(r, Math.max(200, Math.min(1000, audioAnnouncement.pauseMs || 350))));
                await this.speakAnnouncement(audioAnnouncement.name);
            }
            
            // 🍯 Display animated points popup if points earned
            if (earnedPoints > 0) {
                this.showPointsPopup(earnedPoints, breakdown);
            }
            
            // 📚 Show educational word definition after a short delay
            if (result.definition) {
                setTimeout(() => {
                    showWordDefinitionPopup(result.word || this.currentWordData?.word || '', result.definition);
                }, 2000);
            }
            
            // 🎉 Check for streak milestones and celebrate
            if (result.streak_milestone) {
                setTimeout(() => {
                    showStreakCelebration(result.streak_milestone);
                }, 2500);
            }
            
            // Visual explosion effect!
            this.createExplosion();
        } else {
            // Reset streak on incorrect answer
            this.currentStreak = 0;
            
            // Get the correct spelling from the current word data
            const correctWord = this.currentWordData?.word || result.word || '';
            
            // 🔄 RETRY LOGIC: Show choice buttons if this is first failure and retry not used
            if (!this.isRetryAttempt && !this.hasRetried) {
                // This is first failure - offer choice
                // 🔴 CRITICAL: Show ABSOLUTELY NOTHING except buttons!
                // NO feedback message, NO phonetic, NO hints - JUST the choice buttons
                this.retryAvailable = true;
                this.showRetryButton();
                
                // 🍎 iOS FIX: Re-enable input immediately so user can interact
                this.enableInput();
                
                console.log('🔄 PURE RETRY CHOICE MODE: Showing ONLY buttons (no message, no phonetic, nothing else)');
                
                feedbackArea.className = 'feedback-area feedback-error';
                feedbackArea.innerHTML = `
                    <div style="text-align: center; margin-bottom: 0.5rem; font-size: 0.85rem; color: #999;">
                        Would you like to retry?
                    </div>
                    <div class="retry-choice-container">
                        <button class="retry-choice-btn retry" id="retryChoiceYes">✅ Retry</button>
                        <button class="retry-choice-btn show-answer" id="retryChoiceNo">📚 Answer</button>
                    </div>
                    <div class="retry-choice-timer" id="retryChoiceTimer"><span id="retryChoiceSeconds">10</span>s</div>
                `;
                
                // Mascot encourages retry
                if (this.smartyBee) {
                    this.smartyBee.onIncorrectAnswer();
                }
                
                // Enhanced incorrect answer feedback
                playThemedSound('incorrect');
                
                // 🔊 ONLY speak the choice question, nothing else
                console.log('🔊 Speaking: Would you like to retry?');
                await this.speakAnnouncement('Would you like to retry this word? You have 10 seconds to choose.');
                
                // 📚 Show encouraging definition to help with retry
                if (result.definition) {
                    setTimeout(() => {
                        showWordDefinitionPopup(correctWord, result.definition + " 💡 Don't worry - learning is all about trying!");
                    }, 1500);
                }
                
                // Start 10-second choice countdown
                console.log('⏱️ Starting 10-second choice countdown...');
                this.startRetryChoiceCountdown(correctWord);
                
            } else {
                // This is either a retry failure OR user already used retry - no more chances
                this.retryAvailable = false;
                this.hideRetryButton();
                
                feedbackArea.className = 'feedback-area feedback-error';
                feedbackArea.innerHTML = `
                    <div style="font-size: 1.15rem; font-weight: 700; color: #999; margin-bottom: 1rem;">
                        The correct spelling is:
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #FFA500; letter-spacing: 0.1em;">
                        ${correctWord}
                    </div>
                    <div style="font-size: 1rem; color: #666; margin-top: 1rem;">
                        Let's move to the next word!
                    </div>
                `;
                
                console.log('🔴 Second attempt failed - showing correct spelling and moving to next word');
                
                // Mascot encourages!
                if (this.smartyBee) {
                    this.smartyBee.onIncorrectAnswer();
                }
                
                // Show Next Word button so user can advance
                this.showNextWordButton();
            }
        }

        this.delight?.handleFeedback(result);
    }

    hideFeedback() {
        const feedbackArea = document.getElementById('feedbackArea');
        feedbackArea.style.display = 'none';
    }

    updateScoreDisplay(progress = {}) {
        const total = progress.total ?? this.totalWords ?? 0;
        if (Number.isFinite(total) && total > 0) {
            this.totalWords = total;
        }

        const correct = Number(progress.correct) || 0;
        const incorrect = Number(progress.incorrect) || 0;
        const streak = Number(progress.streak ?? this.currentStreak) || 0;
        
        // Ensure we never display NaN
        document.getElementById('correctCount').textContent = correct;
        document.getElementById('incorrectCount').textContent = incorrect;
        document.getElementById('streakCount').textContent = streak;
        
        // 🏆 Update session points display (if element exists)
        const sessionPointsElement = document.getElementById('sessionPoints');
        if (sessionPointsElement) {
            const points = Number(this.sessionPoints) || 0;
            sessionPointsElement.textContent = points.toLocaleString();
        }
        
        // 🎯 Update floating session stats bar
        const floatingWordCount = document.getElementById('floatingWordCount');
        const floatingPoints = document.getElementById('floatingPoints');
        const floatingStreak = document.getElementById('floatingStreak');
        const sessionStatsBar = document.getElementById('sessionStatsBar');
        
        if (floatingWordCount) {
            floatingWordCount.textContent = `${correct}/${total}`;
        }
        if (floatingPoints) {
            const points = Number(this.sessionPoints) || 0;
            floatingPoints.textContent = points.toLocaleString();
        }
        if (floatingStreak) {
            floatingStreak.textContent = streak;
        }
        
        // Show the floating stats bar once quiz starts
        if (sessionStatsBar && total > 0) {
            sessionStatsBar.style.display = 'flex';
        }

        // Update honey jar fill level based on QUIZ PROGRESSION (not correctness ratio)
        // This ensures consistency with progress percentage display
        const honeyLevel = document.getElementById('honeyLevel');
        if (honeyLevel && this.totalWords > 0) {
            // Get current question number from progress text or calculate from correct+incorrect
            const currentQuestion = (correct + incorrect);
            const percentage = Math.min(100, Math.max(0, (currentQuestion / this.totalWords) * 100));
            if (Number.isFinite(percentage)) {
                honeyLevel.style.height = percentage + '%';
                console.log(`🍯 Honey jar filled to ${percentage.toFixed(1)}% (${currentQuestion}/${this.totalWords} questions answered)`);
            }
        }

        this.delight?.updateProgress({ ...progress, total: this.totalWords });
    }

    /**
     * Update both progress text and percentage displays
     * @param {number} current - Current word index (1-based)
     * @param {number} total - Total number of words
     */
    updateProgressDisplays(current, total) {
        // Update traditional question counter
        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = `Question ${current} of ${total}`;
        }
        
        // Update percentage display to match honey jar logic (answered vs total)
        // This ensures consistency between progress percentage and honey jar fill
        const progressPercentage = document.getElementById('progressPercentage');
        if (progressPercentage && total > 0) {
            // Use same calculation as honey jar: answered questions / total
            const answered = current - 1; // Current is 1-based, so current-1 = answered
            const percentage = Math.round((answered / total) * 100);
            progressPercentage.textContent = `Progress: ${percentage}% (${answered} of ${total} words completed)`;
        }
    }
    
    resetHoneyJar() {
        // Reset honey jar to 0% (empty) at start of quiz
        const honeyLevel = document.getElementById('honeyLevel');
        if (honeyLevel) {
            honeyLevel.style.height = '0%';
            console.log('🍯 Honey jar reset to 0% for new quiz');
        }
    }

    disableInput() {
        document.getElementById('spellingInput').disabled = true;
        // Submit button remains enabled for user to submit anytime
        // document.getElementById('submitButton').disabled = true;
    }

    enableInput() {
        const spellingInput = document.getElementById('spellingInput');
        spellingInput.disabled = false;
        
        // 🍎 iOS FIX: Delay focus to allow keyboard to properly show after interaction
        if (this.isIOS || this.isSafari) {
            setTimeout(() => {
                spellingInput.focus();
            }, 100);
        } else {
            spellingInput.focus();
        }
        // Submit button remains enabled for user to submit anytime
        // document.getElementById('submitButton').disabled = false;
    }

    // 🔄 RETRY SYSTEM METHODS
    showRetryButton() {
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.disabled = false;
            console.log('🔄 Retry button enabled');
        }
    }
    
    hideRetryButton() {
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.disabled = true;
            console.log('🔄 Retry button disabled');
        }
    }
    
    startRetryCountdown(correctWord) {
        let secondsLeft = 20;
        const spellingInput = document.getElementById('spellingInput');
        const feedbackArea = document.getElementById('feedbackArea');
        
        // Clear any existing timeout
        if (this.retryTimeoutId) {
            clearTimeout(this.retryTimeoutId);
        }
        
        // 🔒 CLEAR THE ENTIRE FEEDBACK AREA - show ONLY the countdown
        feedbackArea.className = 'feedback-area';
        feedbackArea.innerHTML = '<div id="retryCountdown"></div>';
        const countdownElement = document.getElementById('retryCountdown');
        
        // Enable input for retry attempt
        if (spellingInput) {
            spellingInput.value = '';
            spellingInput.disabled = false;
            spellingInput.placeholder = 'Retry your spelling...';
            
            // 🍎 iOS FIX: Delay focus to ensure keyboard shows properly after retry
            if (this.isIOS || this.isSafari) {
                setTimeout(() => {
                    spellingInput.focus();
                }, 150);
            } else {
                spellingInput.focus();
            }
        }
        
        // Update countdown display with animated styling
        const updateCountdown = () => {
            if (countdownElement) {
                countdownElement.className = 'retry-countdown-timer';
                if (secondsLeft <= 3) {
                    countdownElement.classList.add('countdown-critical');
                }
                countdownElement.innerHTML = `
                    <div class="countdown-label">⏱️ Time to Retry:</div>
                    <div class="countdown-number">${secondsLeft}</div>
                    <div class="countdown-text">Type your answer and click Submit, or wait for next word</div>
                `;
            }
            secondsLeft--;
            
            if (secondsLeft >= 0) {
                this.retryTimeoutId = setTimeout(updateCountdown, 1000);
            } else {
                // Time's up - show "Next Word" button and the correct answer
                this.retryAvailable = false;
                this.hideRetryButton();
                
                // NOW show the correct spelling after 8 seconds are over
                if (correctWord) {
                    feedbackArea.innerHTML = `
                        <div style="font-size: 1.15rem; font-weight: 700;">Time's up! ⏰</div>
                        <div style="margin-top: 0.5rem;">The correct spelling is: <strong>${correctWord}</strong></div>
                        <div style="margin-top: 0.3rem; font-size: 0.9rem; color: #999;">Click "Next Word" to continue</div>
                    `;
                }
                
                // Disable input
                if (spellingInput) {
                    spellingInput.disabled = true;
                }
                
                // Show Next Word button
                this.showNextWordButton();
            }
        };
        
        updateCountdown();
    }
    
    clearRetryCountdown() {
        if (this.retryTimeoutId) {
            clearTimeout(this.retryTimeoutId);
            this.retryTimeoutId = null;
        }
        const countdownElement = document.getElementById('retryCountdown');
        if (countdownElement) {
            countdownElement.textContent = '';
        }
    }

    startRetryChoiceCountdown(correctWord) {
        let secondsLeft = 10;
        const yesButton = document.getElementById('retryChoiceYes');
        const noButton = document.getElementById('retryChoiceNo');
        const timerDisplay = document.getElementById('retryChoiceSeconds');
        const timerContainer = document.getElementById('retryChoiceTimer');
        
        // Clear any existing timeout
        if (this.retryChoiceTimeoutId) {
            clearTimeout(this.retryChoiceTimeoutId);
        }
        
        // ✨ Remove old listeners to prevent duplicates
        if (yesButton) {
            const newYesButton = yesButton.cloneNode(true);
            yesButton.parentNode.replaceChild(newYesButton, yesButton);
        }
        if (noButton) {
            const newNoButton = noButton.cloneNode(true);
            noButton.parentNode.replaceChild(newNoButton, noButton);
        }
        
        // Get the fresh button references
        const yesButtonFresh = document.getElementById('retryChoiceYes');
        const noButtonFresh = document.getElementById('retryChoiceNo');
        
        // Update timer display
        const updateTimer = () => {
            if (timerDisplay) {
                timerDisplay.textContent = secondsLeft;
            }
            if (timerContainer && secondsLeft <= 3) {
                timerContainer.classList.add('critical');
            }
            secondsLeft--;
            
            if (secondsLeft >= 0) {
                this.retryChoiceTimeoutId = setTimeout(updateTimer, 1000);
            } else {
                // Time's up - auto-select "Show Answer"
                console.log('⏱️ Choice timeout - auto-selecting Show Answer');
                this.handleRetryChoiceNo(correctWord);
            }
        };
        
        // ✨ Set up button listeners with fresh buttons
        if (yesButtonFresh) {
            yesButtonFresh.addEventListener('click', () => {
                console.log('🟢 Retry button clicked');
                clearTimeout(this.retryChoiceTimeoutId);
                this.handleRetryChoiceYes();
            });
        } else {
            console.warn('❌ retryChoiceYes button not found');
        }
        
        if (noButtonFresh) {
            noButtonFresh.addEventListener('click', () => {
                console.log('🔴 Show Answer button clicked');
                clearTimeout(this.retryChoiceTimeoutId);
                this.handleRetryChoiceNo(correctWord);
            });
        } else {
            console.warn('❌ retryChoiceNo button not found');
        }
        
        console.log('⏱️ Starting 10-second choice countdown...');
        updateTimer();
    }

    handleRetryChoiceYes() {
        console.log('✅ User chose to RETRY');
        console.log(`   - isRetryAttempt before: ${this.isRetryAttempt}`);
        console.log(`   - currentWordData: ${JSON.stringify(this.currentWordData)}`);
        
        // Mark this as a retry attempt - prevents another retry offer if they get it wrong again
        this.isRetryAttempt = true;
        console.log(`   - isRetryAttempt after: ${this.isRetryAttempt}`);
        
        // Clear choice UI and all feedback
        const feedbackArea = document.getElementById('feedbackArea');
        console.log(`   - feedbackArea found: ${!!feedbackArea}`);
        feedbackArea.innerHTML = '';
        feedbackArea.style.display = 'none';  // Hide feedback area during retry input
        
        // Enable input for retry
        const spellingInput = document.getElementById('spellingInput');
        console.log(`   - spellingInput found: ${!!spellingInput}`);
        if (spellingInput) {
            spellingInput.value = '';
            spellingInput.disabled = false;
            spellingInput.placeholder = 'Retry your spelling...';
            spellingInput.focus();
            console.log('   - Input field enabled and focused');
        }
        
        // ✅ CRITICAL: Re-enable submit button for retry
        const submitButton = document.getElementById('submitButton');
        if (submitButton) {
            submitButton.disabled = false;
            console.log('   - Submit button re-enabled for retry');
        }
        
        // Hide retry button during retry input
        this.hideRetryButton();
        
        // Hide next word button during retry
        const nextWordBtn2 = document.getElementById('nextWordButton');
        if (nextWordBtn2) nextWordBtn2.style.display = 'none';
        
        // Show countdown timer in a clean state
        feedbackArea.style.display = 'block';
        feedbackArea.innerHTML = `
            <div style="text-align: center; font-size: 0.95rem; color: #666;">
                ⏱️ <span id="retryTimerDisplay">20</span> seconds remaining
            </div>
        `;  // Start fresh with timer display
        
        // Announce the 20-second retry window
        console.log('   - Speaking announcement...');
        this.speakAnnouncement('You have 20 seconds to type your retry. Good luck!');
        
        // Start 20-second retry window
        console.log('   - Starting retry input window...');
        this.startRetryInputWindow();
        console.log('   ✅ Retry choice YES complete');
    }

    handleRetryChoiceNo(correctWord) {
        console.log('❌ User chose to see ANSWER');
        console.log(`   - correctWord: ${correctWord}`);
        
        if (this.retryChoiceTimeoutId) {
            clearTimeout(this.retryChoiceTimeoutId);
        }
        
        // Show the correct spelling since user chose to see answer
        const feedbackArea = document.getElementById('feedbackArea');
        feedbackArea.innerHTML = `
            <div style="font-size: 1.15rem; font-weight: 700; color: #999; margin-bottom: 1rem;">
                The correct spelling is:
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #FFA500; letter-spacing: 0.1em;">
                ${correctWord}
            </div>
            <div style="font-size: 1rem; color: #666; margin-top: 1rem;">
                You can try the next word!
            </div>
        `;
        console.log('   - Correct spelling shown, ready for next word');
        
        // Disable input
        const spellingInput = document.getElementById('spellingInput');
        if (spellingInput) {
            spellingInput.disabled = true;
            console.log('   - Input field disabled');
        }
        
        // Show Next Word button
        this.showNextWordButton();
        console.log('   - Next Word button shown');
    }

    startRetryInputWindow() {
        let secondsLeft = 20;
        const feedbackArea = document.getElementById('feedbackArea');
        
        // Clear countdown timer
        if (this.retryInputTimeoutId) {
            clearTimeout(this.retryInputTimeoutId);
        }
        
        // Show countdown in feedback area
        feedbackArea.innerHTML = `
            <div class="retry-countdown-timer">
                <div class="countdown-label">⏱️ Time to Retry:</div>
                <div class="countdown-number" id="retryInputTimer">${secondsLeft}</div>
                <div class="countdown-text">Type and submit your retry answer</div>
            </div>
        `;
        
        // Update timer
        const updateTimer = () => {
            const timerEl = document.getElementById('retryInputTimer');
            if (timerEl) {
                timerEl.textContent = secondsLeft;
            }
            const timerContainer = feedbackArea.querySelector('.retry-countdown-timer');
            if (timerContainer && secondsLeft <= 3) {
                timerContainer.classList.add('countdown-critical');
            }
            secondsLeft--;
            
            if (secondsLeft >= 0) {
                this.retryInputTimeoutId = setTimeout(updateTimer, 1000);
            } else {
                // Time's up - show answer and Next Word button
                this.showRetryInputExpired();
            }
        };
        
        updateTimer();
    }

    showRetryInputExpired() {
        const correctWord = this.currentWordData?.word || '';
        const feedbackArea = document.getElementById('feedbackArea');
        
        feedbackArea.innerHTML = `
            <div style="font-size: 1.15rem; font-weight: 700;">Time's up! ⏰</div>
            <div style="margin-top: 0.5rem;">The correct spelling is: <strong>${correctWord}</strong></div>
            <div style="margin-top: 0.3rem; font-size: 0.9rem; color: #999;">Click "Next Word" to continue</div>
        `;
        
        // Disable input
        const spellingInput = document.getElementById('spellingInput');
        if (spellingInput) {
            spellingInput.disabled = true;
        }
        
        // Show Next Word button
        this.showNextWordButton();
    }

    showNextWordButton() {
        const nextWordButton = document.getElementById('nextWordButton');
        if (nextWordButton) {
            nextWordButton.style.display = 'block';
            console.log('✅ Next Word button shown');
        }
    }

    hideNextWordButton() {
        const nextWordButton = document.getElementById('nextWordButton');
        if (nextWordButton) {
            nextWordButton.style.display = 'none';
            console.log('✅ Next Word button hidden');
        }
    }
    
    handleRetry() {
        console.log('🔄 Retry button clicked!');
        
        // Clear countdown and hide retry button
        this.clearRetryCountdown();
        this.hideRetryButton();
        // Hide next word button
        const nextWordBtn3 = document.getElementById('nextWordButton');
        if (nextWordBtn3) nextWordBtn3.style.display = 'none';
        this.retryAvailable = false;
        this.hasRetried = true;
        this.isRetryAttempt = true;  // Mark this as a retry attempt
        
        // Clear the input and enable it
        const spellingInput = document.getElementById('spellingInput');
        if (spellingInput) {
            spellingInput.value = '';
            spellingInput.disabled = false;
            spellingInput.placeholder = 'Retry spelling... (33% points)';
            spellingInput.focus();
        }
        
        // Hide feedback area
        const feedbackArea3 = document.getElementById('feedbackArea');
        if (feedbackArea3) feedbackArea3.style.display = 'none';
        
        // Re-enable submit button
        const submitButton = document.getElementById('submitButton');
        if (submitButton) {
            submitButton.disabled = false;
        }
        
        // Restart timer for retry attempt
        this.startCountdownTimer();
        
        console.log('🔄 Retry initialized - user can try again for 33% points');
    }

    async skipWord() {
        // ⏱️ Stop countdown timer when skipping
        this.stopCountdownTimer();
        
        try {
            await fetch('/api/answer', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_input: '',
                    method: 'skip',
                    elapsed_ms: 0
                })
            });
            this.delight?.handleSkip();
            this.loadNextWord();
        } catch (error) {
            console.error('Error skipping word:', error);
        }
    }
    
    showDefinition() {
        console.log('📖 Show Definition button clicked');
        console.log('Current word:', this.currentWord);
        
        if (!this.currentWord) {
            this.showFeedback('📖 No word loaded yet.', 'error');
            console.warn('No currentWord available');
            return;
        }
        
        // Check both definition and hint fields
        const definition = this.currentWord.definition || this.currentWord.hint;
        if (!definition) {
            this.showFeedback('📖 No definition available for this word.', 'error');
            console.warn('No definition found for word:', this.currentWord.word);
            return;
        }
        
        const defDisplay = document.getElementById('definitionDisplay');
        if (defDisplay) {
            // Hide the target word from the definition to avoid giving away the answer
            const safeDefinition = hideTargetWord(definition, this.currentWord.word);
            
            defDisplay.innerHTML = `
                <div class="definition-content">
                    <h4 style="color: #5A2C15; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📖 Definition</h4>
                    <p style="margin: 0; color: #3E2723; line-height: 1.4;">${safeDefinition}</p>
                </div>
            `;
            defDisplay.style.display = 'block';
            
            // Optional: Add slight animation
            defDisplay.style.opacity = '0';
            defDisplay.style.transform = 'translateY(10px)';
            defDisplay.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                defDisplay.style.opacity = '1';
                defDisplay.style.transform = 'translateY(0)';
            }, 10);
            
            this.soundboard?.play('button-click');
            console.log('✅ Definition displayed successfully');
        } else {
            console.error('definitionDisplay element not found');
        }
    }
    
    showSentence() {
        console.log('📝 Show Sentence button clicked');
        console.log('Current word:', this.currentWord);
        
        if (!this.currentWord) {
            this.showFeedback('📝 No word loaded yet.', 'error');
            console.warn('No currentWord available');
            return;
        }
        
        if (!this.currentWord.sentence) {
            this.showFeedback('📝 No sentence available for this word.', 'error');
            console.warn('No sentence found for word:', this.currentWord.word);
            return;
        }
        
        const defDisplay = document.getElementById('definitionDisplay');
        if (defDisplay) {
            // Hide the target word from the sentence to avoid giving away the answer
            const safeSentence = hideTargetWord(this.currentWord.sentence, this.currentWord.word);
            
            defDisplay.innerHTML = `
                <div class="sentence-content">
                    <h4 style="color: #5A2C15; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📝 Example Sentence</h4>
                    <p style="margin: 0; color: #3E2723; line-height: 1.4; font-style: italic;">${safeSentence}</p>
                </div>
            `;
            defDisplay.style.display = 'block';
            
            // Optional: Add slight animation
            defDisplay.style.opacity = '0';
            defDisplay.style.transform = 'translateY(10px)';
            defDisplay.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                defDisplay.style.opacity = '1';
                defDisplay.style.transform = 'translateY(0)';
            }, 10);
            
            this.soundboard?.play('button-click');
            console.log('✅ Sentence displayed successfully');
        } else {
            console.error('definitionDisplay element not found');
        }
    }
    
    toggleStat(statType, buttonElement) {
        // Special case: 'all' hides the entire score display
        if (statType === 'all') {
            const scoreDisplay = document.querySelector('.score-display');
            const toggleText = buttonElement.querySelector('.toggle-text');
            
            if (scoreDisplay && toggleText) {
                const isHidden = scoreDisplay.style.display === 'none';
                
                if (isHidden) {
                    // Show the entire stats section
                    scoreDisplay.style.display = '';
                    toggleText.textContent = 'Hide All Stats';
                    buttonElement.classList.remove('stat-hidden');
                } else {
                    // Hide the entire stats section
                    scoreDisplay.style.display = 'none';
                    toggleText.textContent = 'Show All Stats';
                    buttonElement.classList.add('stat-hidden');
                }
                
                this.soundboard?.play('button-click');
            }
            return;
        }
        
        // Individual stat toggles
        const statElements = {
            'correct': document.querySelector('.score-item .score-number.correct')?.parentElement,
            'incorrect': document.querySelector('.score-item .score-number.incorrect')?.parentElement,
            'streak': document.querySelector('.score-item .score-number.streak')?.parentElement,
            'points': document.querySelector('.score-item .score-number.points')?.parentElement
        };
        
        const statElement = statElements[statType];
        const toggleText = buttonElement.querySelector('.toggle-text');
        
        if (statElement && toggleText) {
            const isHidden = statElement.style.display === 'none';
            
            if (isHidden) {
                // Show the stat
                statElement.style.display = '';
                toggleText.textContent = `Hide ${statType.charAt(0).toUpperCase() + statType.slice(1)}`;
                buttonElement.classList.remove('stat-hidden');
            } else {
                // Hide the stat
                statElement.style.display = 'none';
                toggleText.textContent = `Show ${statType.charAt(0).toUpperCase() + statType.slice(1)}`;
                buttonElement.classList.add('stat-hidden');
            }
            
            this.soundboard?.play('button-click');
        }
    }

    async announceQuizEnding() {
        // Announce that the quiz has ended and report card is coming
        const announcement = "That's the end of the quiz. Please wait for your quiz results.";
        
        try {
            await this.speakAnnouncement(announcement);
            // Add a brief pause after the announcement
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            console.error('Error announcing quiz ending:', error);
        }
    }

    async showQuizComplete(summary) {
        document.getElementById('quizCard').style.display = 'none';
        const completeDiv = document.getElementById('quizComplete');
        completeDiv.style.display = 'block';
        
        // Play completion sound
        playThemedSound('word-complete');
        
        // Play completion sound
        playThemedSound('word-complete');

        // Ensure no NaN values in summary
        const total = Number(summary.total) || 1; // Avoid division by zero
        const correct = Number(summary.correct) || 0;
        const incorrect = Number(summary.incorrect) || 0;
        
        const percentage = Math.round((correct / total) * 100);
        const safePercentage = Number.isFinite(percentage) ? percentage : 0;
        
        // Calculate letter grade
        let letterGrade = '';
        let gradeColor = '';
        let gradeEmoji = '';
        let gradeMessage = '';
        
        if (safePercentage >= 90) {
            letterGrade = 'A';
            gradeColor = '#2ecc71'; // Green
            gradeEmoji = '🌟';
            gradeMessage = 'Outstanding! You\'re a spelling superstar!';
            // Extra celebration for perfect score
            if (safePercentage === 100) {
                setTimeout(() => playThemedSound('perfect-score'), 300);
            }
        } else if (safePercentage >= 80) {
            letterGrade = 'B';
            gradeColor = '#3498db'; // Blue
            gradeEmoji = '🎯';
            gradeMessage = 'Great job! You\'re doing really well!';
        } else if (safePercentage >= 70) {
            letterGrade = 'C';
            gradeColor = '#f39c12'; // Orange
            gradeEmoji = '👍';
            gradeMessage = 'Good work! Keep practicing!';
        } else if (safePercentage >= 60) {
            letterGrade = 'D';
            gradeColor = '#e67e22'; // Dark Orange
            gradeEmoji = '💪';
            gradeMessage = 'Nice try! Practice makes perfect!';
        } else {
            letterGrade = 'F';
            gradeColor = '#e74c3c'; // Red
            gradeEmoji = '🐝';
            gradeMessage = 'Keep buzzing! Every bee starts somewhere!';
        }
        
        // Get badges from session state
        const state = await this.getQuizState();
        const badgesEarned = state?.badges_earned || [];
        
        // Get user's current level
        let levelHTML = '';
        try {
            const levelResponse = await fetch('/api/user/level', {
                method: 'GET',
                credentials: 'same-origin'
            });
            if (levelResponse.ok) {
                const levelData = await levelResponse.json();
                if (levelData.success && levelData.level) {
                    const level = levelData.level;
                    const progressPercent = level.progress_percent || 0;
                    
                    levelHTML = `
                        <div style="
                            background: linear-gradient(135deg, #9b59b6 15%, #8e44ad 85%);
                            border-radius: 20px;
                            padding: 1.5rem;
                            margin-bottom: 1.5rem;
                            box-shadow: 0 10px 30px rgba(142, 68, 173, 0.4);
                            animation: slideInDown 0.6s ease 0.3s backwards;
                            text-align: center;
                        ">
                            <div style="font-size: 4rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">
                                ${level.icon}
                            </div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: white; margin-bottom: 0.3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                                ${level.tier}
                            </div>
                            <div style="font-size: 1rem; color: rgba(255,255,255,0.9); margin-bottom: 1rem;">
                                Level ${level.level}
                            </div>
                            ${!level.is_max_level ? `
                                <div style="
                                    background: rgba(255, 255, 255, 0.3);
                                    border-radius: 10px;
                                    height: 12px;
                                    overflow: hidden;
                                    margin-bottom: 0.5rem;
                                ">
                                    <div style="
                                        width: ${progressPercent}%;
                                        height: 100%;
                                        background: linear-gradient(90deg, #FFD700, #FFA500);
                                        border-radius: 10px;
                                        transition: width 1s ease;
                                        box-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                                    "></div>
                                </div>
                                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.95);">
                                    ${level.points_to_next.toLocaleString()} points to next level
                                </div>
                            ` : `
                                <div style="font-size: 1rem; color: rgba(255,255,255,0.95); margin-top: 0.5rem;">
                                    👑 Maximum Level Achieved! 👑
                                </div>
                            `}
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.warn('Failed to load level data:', error);
        }
        
        // Build badges HTML
        let badgesHTML = '';
        if (badgesEarned.length > 0) {
            badgesHTML = `
                <div style="
                    background: linear-gradient(135deg, #FFD700 15%, #FFA500 85%);
                    border-radius: 20px;
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    box-shadow: 0 10px 30px rgba(255, 152, 0, 0.4);
                    animation: slideInUp 0.6s ease 0.6s backwards;
                ">
                    <div style="font-size: 1.5rem; font-weight: 800; color: white; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        🏆 Badges Earned This Session!
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;">
                        ${badgesEarned.map(badge => `
                            <div style="
                                background: rgba(255, 255, 255, 0.95);
                                border-radius: 15px;
                                padding: 1rem;
                                min-width: 140px;
                                text-align: center;
                                box-shadow: 0 6px 15px rgba(0,0,0,0.2);
                                border: 2px solid rgba(255, 215, 0, 0.6);
                            ">
                                <div style="font-size: 3rem; margin-bottom: 0.5rem;">${badge.icon}</div>
                                <div style="font-size: 0.95rem; font-weight: 700; color: #5A2C15; margin-bottom: 0.3rem;">
                                    ${badge.name}
                                </div>
                                <div style="font-size: 1.2rem; font-weight: 800; color: #FFB300;">
                                    +${badge.points} pts
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        document.getElementById('completionStats').innerHTML = `
            <div class="report-card">
                <div class="report-header">
                    <h2>📚 ${(() => {
                        const n = (this.studentName || '').trim();
                        if (!n) return 'Your Report Card!';
                        return n + ' Report Card!';
                    })()}</h2>
                    <p class="sub">Great job practicing your spelling!</p>
                </div>

                <div class="grade-block">
                    <div class="grade-bubble" style="background: linear-gradient(135deg, ${gradeColor} 0%, ${gradeColor}dd 100%);">
                        ${letterGrade}
                    </div>
                    <div class="grade-emoji">${gradeEmoji}</div>
                    <div class="grade-message">${gradeMessage}</div>
                </div>

                <div class="tall-stats">
                    <div class="tall-stat-card">
                        <div class="stat-icon">📚</div>
                        <div class="stat-number">${total}</div>
                        <div class="stat-label">Total Words</div>
                    </div>
                    <div class="tall-stat-card success">
                        <div class="stat-icon">✅</div>
                        <div class="stat-number">${correct}</div>
                        <div class="stat-label">Correct</div>
                    </div>
                </div>

                <div class="grid-stats">
                    <div class="fancy-stat-card danger">
                        <div class="stat-icon">❌</div>
                        <h3>${incorrect}</h3>
                        <p>Incorrect</p>
                    </div>
                    <div class="fancy-stat-card warning">
                        <div class="stat-icon">🎯</div>
                        <h3>${safePercentage}%</h3>
                        <p>Accuracy</p>
                    </div>
                    <div class="fancy-stat-card gold">
                        <div class="stat-icon">🏆</div>
                        <h3>${(Number(summary.session_points) || 0).toLocaleString()}</h3>
                        <p>Total Points</p>
                    </div>
                    <div class="fancy-stat-card purple">
                        <div class="stat-icon">🔥</div>
                        <h3>${Number(summary.max_streak) || 0}</h3>
                        <p>Best Streak</p>
                    </div>
                </div>

                <!-- Buzz Dust Badge Progress -->
                <div class="buzz-dust-container" id="reportBuzzDustContainer">
                    <div class="buzz-dust-title">✨ Buzz Dust Earned This Session</div>
                    <div class="buzz-dust-badge-display">
                        <img id="reportBadgeImage" src="/static/assets/badges/Novice.png" alt="Current Rank" class="report-badge-image">
                    </div>
                    <div class="buzz-dust-points-display">
                        <div class="buzz-dust-points-label">Total Buzz Dust</div>
                        <div class="buzz-dust-points-value" id="reportBuzzDustPoints">0</div>
                    </div>
                    <div class="buzz-dust-rank-label" id="reportBuzzDustRank">Novice Bee</div>
                    <div class="buzz-dust-sub">Keep spelling to level up! ✨</div>
                </div>

                <!-- Achievements moved below for breathing room -->
                ${badgesHTML}
                ${levelHTML}
                
                <!-- Missed Words Section (Study Review) -->
                ${(() => {
                    const incorrectWords = summary.incorrect_words || [];
                    if (incorrectWords.length === 0) return '';
                    
                    return `
                        <div style="margin-top: 1.5rem; padding: 1.5rem; background: linear-gradient(135deg, #FFF9E6 0%, #FFE8B8 100%); border-radius: 16px; border: 2px solid #FFA726; animation: slideInUp 0.6s ease 0.8s backwards;">
                            <h3 style="color: #E65100; margin-bottom: 1rem; font-size: 1.3rem; font-weight: 800; text-align: center;">
                                📝 Words to Practice
                            </h3>
                            <div style="display: grid; gap: 0.75rem; text-align: left;">
                                ${incorrectWords.map(item => `
                                    <div style="background: white; padding: 1rem; border-radius: 12px; border: 2px solid #FFB74D; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                                        <div style="flex: 1; min-width: 150px;">
                                            <div style="font-size: 1.1rem; font-weight: 700; color: #E65100;">
                                                ${item.word}
                                            </div>
                                            <div style="font-size: 0.85rem; color: #757575; margin-top: 0.25rem;">
                                                ${item.user_answer ? `Your answer: <span style="color: #D32F2F; font-weight: 600;">${item.user_answer}</span>` : '(Skipped or no answer)'}
                                            </div>
                                        </div>
                        <button onclick="pronounceWordFromReport(&quot;${item.word.replace(/"/g, '&quot;')}&quot;)" style="background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); color: white; border: none; padding: 0.5rem 1rem; border-radius: 999px; cursor: pointer; font-weight: 700; font-size: 0.9rem; box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3); transition: all 0.2s;">
                                            Hear It
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                })()}
            </div>
            
            <style>
                .report-card {
                    max-width: 560px;
                    margin: 0 auto;
                    padding: 1.25rem 1rem 2rem;
                    background: linear-gradient(180deg, #FFF9E9, #FFF5DD);
                    border-radius: 24px;
                    border: 4px solid rgba(255, 182, 193, 0.45);
                    box-shadow: 0 20px 60px rgba(0,0,0,0.12);
                }
                .report-header { text-align: center; margin-bottom: 0.75rem; }
                .report-header h2 { margin: 0; font-size: 1.4rem; color: #5A2C15; }
                .report-header .sub { margin: 0.35rem 0 0; color: #7A4A2A; font-weight: 600; font-size: 0.95rem; opacity: 0.9; }

                .grade-block { text-align: center; margin: 0.75rem 0 1.25rem; }
                .grade-bubble {
                    display: inline-flex; align-items: center; justify-content: center;
                    color: #fff; font-size: 4.25rem; font-weight: 900; width: 132px; height: 132px;
                    border-radius: 50%; border: 6px solid rgba(255,255,255,0.9);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.25);
                    animation: gradePopIn 0.6s cubic-bezier(0.68,-0.55,0.265,1.55);
                    margin: 0 auto 0.5rem;
                }
                .grade-emoji { font-size: 2.1rem; margin-bottom: 0.25rem; }
                .grade-message { font-size: 1.05rem; color: #5A2C15; font-weight: 600; line-height: 1.45; }

                .tall-stats {
                    display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 0.5rem 0 0.5rem;
                }
                .tall-stat-card {
                    background: linear-gradient(135deg, #FFF5D7 0%, #FFE1F2 100%);
                    border-radius: 20px; padding: 1rem 0.5rem 1.2rem; text-align: center;
                    border: 3px solid rgba(255, 182, 193, 0.35);
                    box-shadow: 0 10px 28px rgba(255,193,7,0.2);
                    min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center;
                }
                .tall-stat-card.success { background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); color: #fff; border-color: rgba(255,255,255,0.35); }
                .tall-stat-card .stat-icon { font-size: 2rem; margin-bottom: 0.25rem; }
                .tall-stat-card .stat-number { font-size: 2.1rem; font-weight: 900; margin: 0.1rem 0; }
                .tall-stat-card .stat-label { font-weight: 700; opacity: 0.95; }

                .grid-stats {
                    display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 0.5rem 0 0.25rem;
                }
                .fancy-stat-card { background: linear-gradient(135deg, #FFF5D7 0%, #FFE1F2 100%); border-radius: 18px; padding: 1.1rem 0.8rem; border: 3px solid rgba(255,182,193,0.35); box-shadow: 0 10px 28px rgba(255,193,7,0.2); text-align: center; }
                .fancy-stat-card .stat-icon { font-size: 2.1rem; margin-bottom: 0.35rem; }
                .fancy-stat-card h3 { font-size: 2.1rem; font-weight: 900; margin: 0.2rem 0; }
                .fancy-stat-card p { font-size: 0.95rem; font-weight: 700; margin: 0; opacity: 0.95; }
                .fancy-stat-card.danger { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: #fff; border-color: rgba(255,255,255,0.35); }
                .fancy-stat-card.warning { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: #fff; border-color: rgba(255,255,255,0.35); }
                .fancy-stat-card.gold { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #fff; border-color: rgba(255,255,255,0.35); }
                .fancy-stat-card.purple { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: #fff; border-color: rgba(255,255,255,0.35); }

                @media (max-width: 460px) {
                    .tall-stats, .grid-stats { grid-template-columns: 1fr; }
                    .report-card { padding: 1rem 0.75rem 1.5rem; }
                }
            </style>
            
            <style>
                @keyframes gradePopIn {
                    from {
                        transform: scale(0) rotate(-180deg);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1) rotate(0deg);
                        opacity: 1;
                    }
                }

                @keyframes slideInLeft {
                    from {
                        transform: translateX(-50px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideInRight {
                    from {
                        transform: translateX(50px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                /* legacy fancy-stat-card base kept above, hover reduced to keep spacing calm */
            </style>
        `;

        this.delight?.setTotalQuestions(summary.total);
        this.delight?.updateProgress({ correct: summary.correct, total: summary.total });
        this.delight?.setMascotState('happy', 2200);
        
        // Mascot celebrates quiz completion!
        if (this.smartyBee) {
            this.smartyBee.onQuizComplete();
        }
        
        // Fetch and populate buzz dust badge info
        this.loadBuzzDustReportCard();

        BeeSmart.showSuccess(`Quiz complete! You got ${summary.correct} out of ${summary.total} words correct (${percentage}%). Grade: ${letterGrade}`);
    }

    async restartQuiz() {
        try {
            await fetch('/api/reset', { 
                method: 'POST',
                credentials: 'same-origin'
            });
            window.location.reload();
        } catch (error) {
            BeeSmart.showError('Failed to restart quiz. Please refresh the page.');
        }
    }
    
    async loadBuzzDustReportCard() {
        try {
            const response = await fetch('/api/buzz-dust/info', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                console.warn('Failed to load buzz dust info for report card');
                return;
            }
            
            const data = await response.json();
            
            if (data.success && data.current_class) {
                const badgeImage = document.getElementById('reportBadgeImage');
                const buzzDustPoints = document.getElementById('reportBuzzDustPoints');
                const buzzDustRank = document.getElementById('reportBuzzDustRank');
                
                // Update badge image - handle filename mapping (Elite -> Elete typo)
                const badgeFilename = data.current_class.badge_image
                    .replace('.glb', '.png')
                    .replace('Elite.png', 'Elete.png');
                badgeImage.src = `/static/assets/badges/${badgeFilename}`;
                badgeImage.alt = `${data.current_class.label} Badge`;
                
                // Update points display
                buzzDustPoints.textContent = (data.total_buzz_dust || 0).toLocaleString();
                
                // Update rank label with emoji
                buzzDustRank.textContent = `${data.current_class.emoji} ${data.current_class.label}`;
                
                console.log('✨ Buzz Dust report card loaded:', data);
            }
        } catch (error) {
            console.error('Error loading buzz dust report card:', error);
        }
    }
}

// 🔊 Pronounce word from report card (missed words review)
function pronounceWordFromReport(word) {
    if (!word) return;
    
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(word);
        const voices = speechSynthesis.getVoices();
        
        // Prefer US English voice
        const enUSVoice = voices.find(v => v.lang === 'en-US') || 
                         voices.find(v => v.lang?.startsWith('en')) || 
                         null;
        if (enUSVoice) utterance.voice = enUSVoice;
        
        utterance.rate = 0.85;  // Slow for clarity
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        speechSynthesis.speak(utterance);
    }
}

// ✅ Register QuizManager on window for global access
window.QuizManager = QuizManager;
console.log('✅ QuizManager registered on window');

// Toggle stats bar visibility
function toggleStatsBar() {
    const statsBar = document.getElementById('sessionStatsBar');
    const toggleBtn = document.getElementById('statsToggleBtn');
    
    if (statsBar && toggleBtn) {
        statsBar.classList.toggle('collapsed');
        
        // Update button title
        if (statsBar.classList.contains('collapsed')) {
            toggleBtn.title = 'Show stats bar';
        } else {
            toggleBtn.title = 'Hide stats bar';
        }
        
        // Play button click sound if available
        if (typeof playThemedSound === 'function') {
            playThemedSound('button-click');
        }
    }
}

// Kid-friendly confirmation for back to menu
function confirmBackToMenu(event) {
    event.preventDefault();
    
    // 🛑 FULL CLEANUP: Stop all quiz activities immediately
    console.log('🛑 Starting full quiz cleanup for back navigation...');
    
    // 1. Stop any ongoing announcer speech immediately
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        console.log('🔇 Stopped announcer speech');
    }
    
    // 2. Clear any active countdown timers
    if (window.spellingQuiz && window.spellingQuiz.countdownTimer) {
        clearInterval(window.spellingQuiz.countdownTimer);
        window.spellingQuiz.countdownTimer = null;
        console.log('⏱️ Cleared countdown timer');
    }
    
    // 3. Stop any audio context or sound effects
    if (window.AudioContext || window.webkitAudioContext) {
        try {
            const contexts = window.audioContexts || [];
            contexts.forEach(ctx => {
                if (ctx.state !== 'closed') {
                    ctx.close();
                }
            });
            console.log('🔊 Closed audio contexts');
        } catch (e) {
            console.log('Audio context cleanup attempted:', e);
        }
    }
    
    // 4. Clear any pending timeouts/intervals
    if (window.spellingQuiz && window.spellingQuiz.currentWordTimeout) {
        clearTimeout(window.spellingQuiz.currentWordTimeout);
        console.log('⏰ Cleared pending timeouts');
    }
    
    console.log('✅ Quiz cleanup complete');
    
    // Create kid-friendly modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #FFF5D7 0%, #FFE1F2 100%);
            padding: 2rem;
            border-radius: 24px;
            max-width: 420px;
            margin: 1rem;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
            border: 4px solid rgba(255, 182, 193, 0.6);
            animation: modalSlideIn 0.3s ease;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🐝</div>
            <h2 style="color: #D2691E; margin-bottom: 1rem; font-size: 1.5rem;">
                Are you sure you want to go back?
            </h2>
            <p style="color: #5A2C15; line-height: 1.6; margin-bottom: 1.5rem; font-size: 1.1rem;">
                🍯 Going back to the menu will end your current quiz and reset your progress!
                <br><br>
                <strong>Your scores will be lost.</strong>
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <button id="confirmBack" style="
                    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
                    color: white;
                    border: none;
                    padding: 0.9rem 1.8rem;
                    border-radius: 16px;
                    font-weight: 700;
                    font-size: 1rem;
                    cursor: pointer;
                    box-shadow: 0 8px 20px rgba(255, 107, 107, 0.4);
                    transition: all 0.2s;
                    border: 3px solid rgba(255, 255, 255, 0.4);
                ">
                    Yes, Go Back
                </button>
                <button id="cancelBack" style="
                    background: linear-gradient(135deg, #A8E6CF 0%, #6BCF7F 100%);
                    color: #1a5c3a;
                    border: none;
                    padding: 0.9rem 1.8rem;
                    border-radius: 16px;
                    font-weight: 700;
                    font-size: 1rem;
                    cursor: pointer;
                    box-shadow: 0 8px 20px rgba(168, 230, 207, 0.4);
                    transition: all 0.2s;
                    border: 3px solid rgba(255, 255, 255, 0.4);
                ">
                    Stay Here
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const confirmBtn = document.getElementById('confirmBack');
    const cancelBtn = document.getElementById('cancelBack');
    
    // Button hover effects
    confirmBtn.addEventListener('mouseenter', () => {
        confirmBtn.style.transform = 'scale(1.05) translateY(-2px)';
        confirmBtn.style.boxShadow = '0 12px 28px rgba(255, 107, 107, 0.6)';
    });
    confirmBtn.addEventListener('mouseleave', () => {
        confirmBtn.style.transform = 'scale(1)';
        confirmBtn.style.boxShadow = '0 8px 20px rgba(255, 107, 107, 0.4)';
    });
    
    cancelBtn.addEventListener('mouseenter', () => {
        cancelBtn.style.transform = 'scale(1.05) translateY(-2px)';
        cancelBtn.style.boxShadow = '0 12px 28px rgba(168, 230, 207, 0.6)';
    });
    cancelBtn.addEventListener('mouseleave', () => {
        cancelBtn.style.transform = 'scale(1)';
        cancelBtn.style.boxShadow = '0 8px 20px rgba(168, 230, 207, 0.4)';
    });
    
    // Click handlers
    confirmBtn.addEventListener('click', () => {
        modal.remove();
        
        // Final cleanup before navigation
        if ('speechSynthesis' in window) {
            speechSynthesis.cancel();
        }
        
        // Navigate to home
        window.location.href = '/';
    });
    
    cancelBtn.addEventListener('click', () => {
        modal.remove();
        // Resume quiz if user cancels
        console.log('↩️ User cancelled back navigation, resuming quiz');
    });
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 🍎 iOS Audio Unlock - MUST run before any speech synthesis
function unlockiOSAudio() {
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (!isIOS) return;
    
    console.log('🍎 iOS detected - setting up audio unlock');
    
    // Silent utterance to wake up speech synthesis on first user interaction
    const unlock = () => {
        console.log('🔓 Unlocking iOS audio...');
        
        // Method 1: Silent speech utterance
        const utterance = new SpeechSynthesisUtterance(' ');
        utterance.volume = 0.01; // Almost silent
        speechSynthesis.speak(utterance);
        setTimeout(() => speechSynthesis.cancel(), 100);
        
        // Method 2: Resume AudioContext if exists
        if (window.AudioContext || window.webkitAudioContext) {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            if (audioContext.state === 'suspended') {
                audioContext.resume().then(() => {
                    console.log('✅ AudioContext resumed');
                });
            }
        }
        
        console.log('✅ iOS audio unlocked');
        
        // Remove listeners after first unlock
        document.removeEventListener('touchstart', unlock);
        document.removeEventListener('click', unlock);
    };
    
    // Listen for first user interaction
    document.addEventListener('touchstart', unlock, { once: true });
    document.addEventListener('click', unlock, { once: true });
}

// 🛡️ Safe JSON parsing helper
function safeParseJSON(txt, label = 'payload') {
    try { 
        return JSON.parse(txt); 
    } catch (e) {
        console.error(`JSON parse failed for ${label}:`, txt.slice(0, 300), e);
        throw new Error(`Invalid JSON in ${label}: ${e.message}`);
    }
}

// 🛡️ Global error handler for syntax errors
window.addEventListener('error', (event) => {
    if (event.error && event.error.message && event.error.message.includes('Unexpected token')) {
        console.error('🚨 JavaScript syntax error detected:', {
            message: event.error.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            stack: event.error.stack
        });
        // Show user-friendly error message
        if (typeof BeeSmart !== 'undefined' && BeeSmart.showError) {
            BeeSmart.showError('Page loading error detected. Refreshing...');
        } else {
            alert('Page loading error. Refreshing...');
        }
        setTimeout(() => window.location.reload(), 2000);
        return true; // Prevent default error handling
    }
});

// Call immediately on page load
unlockiOSAudio();

// ✅ Verify critical classes are defined
console.log('📚 Class definitions check:', {
    CountdownTimer: typeof CountdownTimer !== 'undefined' ? 'OK' : 'MISSING',
    QuizManager: typeof QuizManager !== 'undefined' ? 'OK' : 'MISSING'
});

// Real-time live status polling (ensures header stays in sync even on tab focus changes)
</script>
