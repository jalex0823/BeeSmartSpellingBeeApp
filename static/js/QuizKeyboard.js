/**
 * BeeSmart Custom Quiz Keyboard
 * On-screen A–Z + Space + Backspace for quiz flows only.
 * Prevents system keyboard; consistent UI across iOS/Android/Web.
 * Lifecycle: mount when countdown starts, disable on submit/timer end, unmount on game over.
 * Optional: hex key styling (USE_HEX_KEYS), practice-mode key flash.
 */
(function (global) {
    'use strict';

    const ROW1 = 'QWERTYUIOP'.split('');
    const ROW2 = 'ASDFGHJKL'.split('');
    const ROW3 = 'ZXCVBNM'.split('');

    /** Set true only after QA confirms tap targets remain accurate. */
    const USE_HEX_KEYS_DEFAULT = false;

    let instance = null;

    let lastTouchActivationTs = 0;

    function playKeyClick(volume) {
        try {
            if (window && window.__disableQuizKeyboardSfx) {
                return;
            }
            try {
                if (window && typeof window.__beesmartSfxEnabled === 'function' && !window.__beesmartSfxEnabled()) {
                    return;
                }
            } catch (_) {}

            if (window && window.__useSimpleQuizKeyboardSfx) {
                if (!window.__quizKeyboardClickAudio) {
                    window.__quizKeyboardClickAudio = new Audio('/static/sounds/button-click.mp3');
                }
                const a = window.__quizKeyboardClickAudio;
                a.volume = typeof volume === 'number' ? volume : 0.32;
                try { a.currentTime = 0; } catch (_) {}
                const p = a.play();
                if (p && typeof p.catch === 'function') p.catch(() => {});
                return;
            }
            if (typeof window.BeeSmartButtonSfx !== 'undefined' && window.BeeSmartButtonSfx.playRandom) {
                window.BeeSmartButtonSfx.playRandom({ volume: typeof volume === 'number' ? volume : 0.32 });
            }
        } catch (_) {}
    }

    function keyPopAnimation(buttonEl) {
        if (!buttonEl || !buttonEl.classList) return;
        buttonEl.classList.add('quiz-keyboard-key-pop', 'key-pop');
        const duration = 120;
        setTimeout(() => {
            try {
                buttonEl.classList.remove('quiz-keyboard-key-pop', 'key-pop');
            } catch (_) {}
        }, duration);
    }

    /* Only click sound + one visual (pop). No extra press state or submit sound on key. */
    function createKey(letter, opts) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'quiz-keyboard-key quiz-keyboard-key-letter';
        if (opts.useHexKeys) button.classList.add('quiz-keyboard-key-hex');
        button.setAttribute('aria-label', 'Letter ' + letter);
        button.setAttribute('data-no-button-sfx', '1');
        button.textContent = opts.autoCaps !== false ? letter : letter.toLowerCase();
        button.dataset.letter = letter;
        const onLetter = () => {
            if (Date.now() - lastTouchActivationTs < 450) return;
            keyPopAnimation(button);
            playKeyClick(0.3);
            opts.onLetter(letter);
        };
        button.addEventListener('click', onLetter);
        button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            lastTouchActivationTs = Date.now();
            keyPopAnimation(button);
            playKeyClick(0.3);
            opts.onLetter(letter);
        }, { passive: false });
        return button;
    }

    function createSpecialKey(label, className, ariaLabel, onClick, isSubmit, useHexKeys) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'quiz-keyboard-key ' + className;
        if (useHexKeys) button.classList.add('quiz-keyboard-key-hex');
        button.setAttribute('aria-label', ariaLabel);
        button.setAttribute('data-no-button-sfx', '1');
        button.innerHTML = label;
        const wrapped = () => {
            if (Date.now() - lastTouchActivationTs < 450) return;
            keyPopAnimation(button);
            playKeyClick(0.32);
            onClick();
        };
        let lastPressAt = 0;
        const trigger = (e) => {
            const now = Date.now();
            if (now - lastPressAt < 220) {
                if (e && e.cancelable) e.preventDefault();
                return;
            }
            lastPressAt = now;
            wrapped();
        };
        button.addEventListener('click', trigger);
        button.addEventListener('touchend', (e) => {
            if (e && e.cancelable) e.preventDefault();
            lastTouchActivationTs = Date.now();
            trigger(e);
        }, { passive: false });
        return button;
    }

    function initQuizKeyboard(options) {
        const {
            targetEl,
            inputEl,
            onKey,
            onBackspace,
            onSpace,
            onSubmit,
            allowSpaces = true,
            autoCaps = true,
            maxLength = null,
            disableInputWhenRoundEnds = true,
            practiceMode = false,
            showSubmitKey = false,
            useHexKeys = USE_HEX_KEYS_DEFAULT,
            // When true, prevents the OS/system keyboard and forces on-screen keys.
            // Default: lock only on coarse-pointer (phones/tablets). Desktop/laptops keep physical keyboard typing.
            lockSystemKeyboard = null,
            spacerTargetEl = null,
            onMounted = null,
            onUnmounted = null,
            onHide = null
        } = options || {};

        if (!targetEl || !inputEl) {
            console.warn('QuizKeyboard: targetEl and inputEl are required');
            return null;
        }

        if (instance) {
            instance.destroy();
        }

        let currentAnswer = '';
        let enabled = true;
        const state = { maxLength: maxLength ?? null };

        const shouldLockSystemKeyboard = (() => {
            if (lockSystemKeyboard === true || lockSystemKeyboard === false) return !!lockSystemKeyboard;
            try {
                if (typeof document !== 'undefined' && document.documentElement && document.documentElement.classList.contains('android')) return true;
                if (typeof navigator !== 'undefined' && /Android/i.test(navigator.userAgent)) return true;
                if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.getPlatform && window.Capacitor.getPlatform() === 'android') return true;
                if (typeof window !== 'undefined' && window.matchMedia) {
                    return window.matchMedia('(hover: none) and (pointer: coarse)').matches;
                }
            } catch (_) {}
            try {
                return (typeof navigator !== 'undefined') && (navigator.maxTouchPoints > 0);
            } catch (_) {}
            return true;
        })();

        function syncToInput() {
            inputEl.value = currentAnswer;
            try {
                inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            } catch (_) {}
        }

        function syncFromInput() {
            let v = String(inputEl.value == null ? '' : inputEl.value);
            if (state.maxLength != null && v.length > state.maxLength) {
                v = v.slice(0, state.maxLength);
                inputEl.value = v;
            }
            currentAnswer = v;
        }

        function handleLetter(letter) {
            if (!enabled) return;
            const char = autoCaps ? letter : letter.toLowerCase();
            if (state.maxLength != null && currentAnswer.length >= state.maxLength) return;
            currentAnswer += char;
            syncToInput();
            if (typeof onKey === 'function') onKey(char);
        }

        function handleBackspace() {
            if (!enabled) return;
            currentAnswer = currentAnswer.slice(0, -1);
            syncToInput();
            if (typeof onBackspace === 'function') onBackspace();
        }

        function handleSpace() {
            if (!enabled || !allowSpaces) return;
            if (state.maxLength != null && currentAnswer.length >= state.maxLength) return;
            if (currentAnswer.length === 0) return; // no space at start
            currentAnswer += ' ';
            syncToInput();
            if (typeof onSpace === 'function') onSpace();
        }

        function handleSubmit() {
            if (!enabled) return;
            try {
                if (typeof onSubmit === 'function') {
                    onSubmit();
                    return;
                }
            } catch (_) {}
            // Fallback path: trigger the main submit button if provided callback is missing/broken.
            try {
                const submitBtn = document.getElementById('submitButton');
                if (submitBtn && typeof submitBtn.click === 'function') submitBtn.click();
            } catch (_) {}
        }

        const container = document.createElement('div');
        container.className = 'quiz-keyboard custom-keyboard' + (useHexKeys ? ' quiz-keyboard--hex-keys' : '');
        container.setAttribute('role', 'group');
        container.setAttribute('aria-label', 'Quiz spelling keyboard');

        if (typeof onHide === 'function') {
            const hideRow = document.createElement('div');
            hideRow.className = 'quiz-keyboard-hide-row';
            const hideBtn = document.createElement('button');
            hideBtn.type = 'button';
            hideBtn.id = 'hideKeyboardBtn';
            hideBtn.className = 'quiz-keyboard-hide-btn';
            hideBtn.setAttribute('aria-label', 'Hide keyboard');
            hideBtn.innerHTML = '&#9660; Hide keyboard';
            hideBtn.addEventListener('click', function () {
                try { onHide(); } catch (_) {}
            }, { once: false });
            hideRow.appendChild(hideBtn);
            container.appendChild(hideRow);
        }

        const keyOpts = { autoCaps, onLetter: handleLetter, useHexKeys };

        const row1 = document.createElement('div');
        row1.className = 'quiz-keyboard-row';
        ROW1.forEach(l => row1.appendChild(createKey(l, keyOpts)));
        container.appendChild(row1);

        const row2 = document.createElement('div');
        row2.className = 'quiz-keyboard-row';
        ROW2.forEach(l => row2.appendChild(createKey(l, keyOpts)));
        container.appendChild(row2);

        const row3 = document.createElement('div');
        row3.className = 'quiz-keyboard-row';
        ROW3.forEach(l => row3.appendChild(createKey(l, keyOpts)));
        container.appendChild(row3);

        const row4 = document.createElement('div');
        row4.className = 'quiz-keyboard-row quiz-keyboard-row-bottom';
        row4.classList.toggle('has-submit', !!showSubmitKey);
        row4.classList.toggle('no-space', !allowSpaces);

        // Layout:
        // - If spaces allowed: [spacer][Space][Backspace][Submit?]
        // - If spaces NOT allowed: [Backspace][Submit?]
        if (allowSpaces) {
            const spacer = document.createElement('div');
            spacer.className = 'quiz-keyboard-key-spacer';
            spacer.setAttribute('aria-hidden', 'true');
            row4.appendChild(spacer);

            const spaceBtn = createSpecialKey('Space', 'quiz-keyboard-key-space', 'Space', handleSpace, false, useHexKeys);
            row4.appendChild(spaceBtn);
        }

        const backspaceBtn = createSpecialKey('⌫', 'quiz-keyboard-key-backspace', 'Backspace', handleBackspace, false, useHexKeys);
        row4.appendChild(backspaceBtn);

        // Submit key should sit right next to backspace
        if (showSubmitKey) {
            const submitBtn = createSpecialKey('Submit', 'quiz-keyboard-key-submit', 'Submit answer', handleSubmit, true, useHexKeys);
            row4.appendChild(submitBtn);
        }
        container.appendChild(row4);

        targetEl.innerHTML = '';
        targetEl.appendChild(container);
        container.classList.add('quiz-keyboard-enter');

        function applyKeyboardSpacer() {
            try {
                const h = container.getBoundingClientRect().height;
                if (typeof h === 'number' && h > 0) {
                    document.documentElement.style.setProperty('--quiz-kb-height', Math.ceil(h) + 'px');
                    if (spacerTargetEl) spacerTargetEl.style.paddingBottom = (h + 12) + 'px';
                }
            } catch (_) {}
        }
        applyKeyboardSpacer();
        requestAnimationFrame(function reapply() {
            applyKeyboardSpacer();
            setTimeout(applyKeyboardSpacer, 300);
        });
        if (spacerTargetEl && inputEl) {
            setTimeout(function scrollInputIntoView() {
                try {
                    inputEl.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
                } catch (_) {}
            }, 100);
        }
        if (typeof onMounted === 'function') {
            try { onMounted(container); } catch (_) {}
        }

        // Keep input and keyboard state in sync (supports physical keyboard typing on desktop).
        const inputSyncHandler = () => syncFromInput();
        inputEl.addEventListener('input', inputSyncHandler);

        // Physical keyboard support (desktop + external keyboards):
        // When the system keyboard is locked (mobile) OR the input isn't focused, capture keystrokes
        // and route them through the on-screen keyboard handlers.
        let docKeydownHandler = null;
        docKeydownHandler = (e) => {
            try {
                if (!enabled) return;
                if (!e || e.defaultPrevented) return;

                const key = e.key;
                if (!key) return;

                const tgt = e.target;
                const tag = (tgt && tgt.tagName) ? String(tgt.tagName).toLowerCase() : '';
                const isEditable = !!(tgt && (tgt.isContentEditable || tag === 'textarea' || (tag === 'input' && tgt !== inputEl)));
                // If the user is typing into another input/textarea/contenteditable, do not hijack.
                if (isEditable) return;

                const inputIsFocused = (document.activeElement === inputEl);
                const inputIsReadOnly = inputEl.hasAttribute('readonly');

                // Always allow Enter to submit (so desktop users can press Enter).
                if (key === 'Enter') {
                    e.preventDefault();
                    handleSubmit();
                    return;
                }

                // If the input is focused and writable, let the browser handle typing; we'll sync via input event.
                if (inputIsFocused && !inputIsReadOnly) {
                    return;
                }

                if (key === 'Backspace') {
                    e.preventDefault();
                    handleBackspace();
                    return;
                }

                if (key === ' ') {
                    e.preventDefault();
                    handleSpace();
                    return;
                }

                if (key.length === 1 && /[a-z]/i.test(key)) {
                    e.preventDefault();
                    handleLetter(key.toUpperCase());
                    return;
                }
            } catch (_) {}
        };
        document.addEventListener('keydown', docKeydownHandler, true);

        // Normalize input attributes (always)
        inputEl.setAttribute('autocomplete', 'off');
        inputEl.setAttribute('autocapitalize', 'off');
        inputEl.setAttribute('autocorrect', 'off');
        inputEl.setAttribute('spellcheck', 'false');
        inputEl.setAttribute('data-quiz-keyboard', 'true');

        // Optionally lock system keyboard (mobile) vs allow physical keyboard (desktop)
        let focusBlurHandler = null;
        if (shouldLockSystemKeyboard) {
            inputEl.setAttribute('readonly', 'readonly');
            inputEl.setAttribute('inputmode', 'none');
            focusBlurHandler = (e) => {
                try { e.preventDefault(); } catch (_) {}
                try { inputEl.blur(); } catch (_) {}
            };
            inputEl.addEventListener('focus', focusBlurHandler);
        } else {
            inputEl.removeAttribute('readonly');
            inputEl.setAttribute('inputmode', 'text');
        }

        let mode = practiceMode ? 'practice' : 'test';

        function flashKey(letter, className) {
            const keyEl = container.querySelector('.quiz-keyboard-key-letter[data-letter="' + letter + '"]');
            if (!keyEl) return;
            keyEl.classList.add(className);
            setTimeout(() => keyEl.classList.remove(className), 400);
        }

        instance = {
            setEnabled(bool) {
                enabled = !!bool;
                container.classList.toggle('quiz-keyboard-disabled', !enabled);
                container.querySelectorAll('.quiz-keyboard-key').forEach(k => {
                    k.disabled = !enabled;
                });
                if (disableInputWhenRoundEnds) {
                    inputEl.disabled = !enabled;
                }
            },
            setValue(value) {
                currentAnswer = String(value == null ? '' : value);
                syncToInput();
            },
            getValue() {
                return currentAnswer;
            },
            clear() {
                currentAnswer = '';
                syncToInput();
            },
            setMode(m) {
                mode = m === 'practice' || m === 'test' ? m : mode;
            },
            flashCorrectKey(letter) {
                if (mode !== 'practice') return;
                flashKey(String(letter).toUpperCase(), 'quiz-keyboard-key-flash-correct');
            },
            flashIncorrectKey(letter) {
                if (mode !== 'practice') return;
                flashKey(String(letter).toUpperCase(), 'quiz-keyboard-key-flash-incorrect');
            },
            setOptions(opts) {
                if (opts.maxLength !== undefined) state.maxLength = opts.maxLength;
            },
            destroy() {
                try {
                    document.documentElement.style.removeProperty('--quiz-kb-height');
                } catch (_) {}
                if (spacerTargetEl) {
                    try { spacerTargetEl.style.paddingBottom = ''; } catch (_) {}
                }
                if (typeof onUnmounted === 'function') {
                    try { onUnmounted(); } catch (_) {}
                }
                if (instance === this) instance = null;
                try { if (inputSyncHandler) inputEl.removeEventListener('input', inputSyncHandler); } catch (_) {}
                try { if (focusBlurHandler) inputEl.removeEventListener('focus', focusBlurHandler); } catch (_) {}
                try { if (docKeydownHandler) document.removeEventListener('keydown', docKeydownHandler, true); } catch (_) {}
                inputEl.removeAttribute('readonly');
                inputEl.removeAttribute('inputmode');
                inputEl.removeAttribute('data-quiz-keyboard');
                try { targetEl.removeChild(container); } catch (_) {}
            }
        };

        return instance;
    }

    function setEnabled(bool) {
        if (instance && typeof instance.setEnabled === 'function') {
            instance.setEnabled(bool);
        }
    }

    function clear() {
        if (instance && typeof instance.clear === 'function') {
            instance.clear();
        }
    }

    function setMode(mode) {
        if (instance && typeof instance.setMode === 'function') {
            instance.setMode(mode);
        }
    }

    function destroy() {
        if (instance && typeof instance.destroy === 'function') {
            instance.destroy();
        }
        instance = null;
    }

    /**
     * Spec-compliant mount: (containerEl, handlers, options).
     * handlers: { onKey, onSpace, onBackspace, onSubmit (optional) }
     * options: { inputEl, maxLength, allowSpaces, autoCaps, showSubmitKey, useHexKeys, practiceMode, ... }
     */
    function mount(containerEl, handlers, options) {
        const opts = Object.assign({}, options, {
            targetEl: containerEl,
            onKey: handlers && handlers.onKey,
            onBackspace: handlers && handlers.onBackspace,
            onSpace: handlers && handlers.onSpace,
            onSubmit: handlers && handlers.onSubmit
        });
        return initQuizKeyboard(opts);
    }

    global.initQuizKeyboard = initQuizKeyboard;
    global.setQuizKeyboardEnabled = setEnabled;
    global.destroyQuizKeyboard = destroy;
    global.QuizKeyboard = {
        mount,
        unmount: destroy,
        setEnabled,
        clear,
        setMode
    };
})(typeof window !== 'undefined' ? window : this);
