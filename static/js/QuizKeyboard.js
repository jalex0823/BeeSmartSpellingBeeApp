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

    function playKeyClick(volume) {
        try {
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

    function pressKey(el) {
        if (!el || !el.classList) return;
        el.classList.add('is-pressed');
        setTimeout(() => {
            try { el.classList.remove('is-pressed'); } catch (_) {}
        }, 80);
    }

    function playSubmitSound() {
        try {
            if (window.quizManager && window.quizManager.soundboard && typeof window.quizManager.soundboard.play === 'function') {
                window.quizManager.soundboard.play('correct');
            } else if (typeof window.BeeSmartButtonSfx !== 'undefined' && window.BeeSmartButtonSfx.playRandom) {
                window.BeeSmartButtonSfx.playRandom({ volume: 0.5 });
            }
        } catch (_) {}
    }

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
            pressKey(button);
            keyPopAnimation(button);
            playKeyClick(0.3);
            opts.onLetter(letter);
        };
        button.addEventListener('click', onLetter);
        button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            button.click();
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
            if (!isSubmit) {
                pressKey(button);
                keyPopAnimation(button);
            }
            if (isSubmit) {
                playSubmitSound();
                button.classList.add('quiz-keyboard-submit-pressed');
                setTimeout(() => button.classList.remove('quiz-keyboard-submit-pressed'), 420);
            } else {
                playKeyClick(0.32);
            }
            onClick();
        };
        button.addEventListener('click', wrapped);
        button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            button.click();
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

        function syncToInput() {
            inputEl.value = currentAnswer;
            try {
                inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            } catch (_) {}
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
            if (typeof onSubmit === 'function') onSubmit();
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
        const spacer = document.createElement('div');
        spacer.className = 'quiz-keyboard-key-spacer';
        spacer.setAttribute('aria-hidden', 'true');
        row4.appendChild(spacer);
        if (allowSpaces) {
            const spaceBtn = createSpecialKey('Space', 'quiz-keyboard-key-space', 'Space', handleSpace, false, useHexKeys);
            row4.appendChild(spaceBtn);
        }
        const backspaceBtn = createSpecialKey('⌫', 'quiz-keyboard-key-backspace', 'Backspace', handleBackspace, false, useHexKeys);
        row4.appendChild(backspaceBtn);
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

        inputEl.setAttribute('readonly', 'readonly');
        inputEl.setAttribute('inputmode', 'none');
        inputEl.setAttribute('autocomplete', 'off');
        inputEl.setAttribute('autocapitalize', 'off');
        inputEl.setAttribute('autocorrect', 'off');
        inputEl.setAttribute('spellcheck', 'false');
        inputEl.setAttribute('data-quiz-keyboard', 'true');

        inputEl.addEventListener('focus', (e) => {
            e.preventDefault();
            inputEl.blur();
        });

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
