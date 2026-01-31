/**
 * BeeSmart Custom Quiz Keyboard
 * On-screen A–Z + Space + Backspace for quiz flows only.
 * Prevents system keyboard; consistent UI across iOS/Android/Web.
 */
(function (global) {
    'use strict';

    const ROW1 = 'QWERTYUIOP'.split('');
    const ROW2 = 'ASDFGHJKL'.split('');
    const ROW3 = 'ZXCVBNM'.split('');

    let instance = null;

    function createKey(letter, opts) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'quiz-keyboard-key quiz-keyboard-key-letter';
        button.setAttribute('aria-label', 'Letter ' + letter);
        button.textContent = opts.autoCaps !== false ? letter : letter.toLowerCase();
        button.dataset.letter = letter;
        button.addEventListener('click', () => opts.onLetter(letter));
        button.addEventListener('touchstart', (e) => { e.preventDefault(); button.click(); }, { passive: false });
        return button;
    }

    function createSpecialKey(label, className, ariaLabel, onClick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'quiz-keyboard-key ' + className;
        button.setAttribute('aria-label', ariaLabel);
        button.innerHTML = label;
        button.addEventListener('click', onClick);
        button.addEventListener('touchstart', (e) => { e.preventDefault(); button.click(); }, { passive: false });
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
            practiceMode = false
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
            if (maxLength != null && currentAnswer.length >= maxLength) return;
            if (currentAnswer.length === 0) return;
            currentAnswer += ' ';
            syncToInput();
            if (typeof onSpace === 'function') onSpace();
        }

        function handleSubmit() {
            if (!enabled) return;
            if (typeof onSubmit === 'function') onSubmit();
        }

        const container = document.createElement('div');
        container.className = 'quiz-keyboard';
        container.setAttribute('role', 'group');
        container.setAttribute('aria-label', 'Quiz spelling keyboard');

        const row1 = document.createElement('div');
        row1.className = 'quiz-keyboard-row';
        ROW1.forEach(l => row1.appendChild(createKey(l, { autoCaps, onLetter: handleLetter })));
        container.appendChild(row1);

        const row2 = document.createElement('div');
        row2.className = 'quiz-keyboard-row';
        ROW2.forEach(l => row2.appendChild(createKey(l, { autoCaps, onLetter: handleLetter })));
        container.appendChild(row2);

        const row3 = document.createElement('div');
        row3.className = 'quiz-keyboard-row';
        ROW3.forEach(l => row3.appendChild(createKey(l, { autoCaps, onLetter: handleLetter })));
        container.appendChild(row3);

        const row4 = document.createElement('div');
        row4.className = 'quiz-keyboard-row quiz-keyboard-row-bottom';
        if (allowSpaces) {
            const spaceBtn = createSpecialKey('Space', 'quiz-keyboard-key-space', 'Space', handleSpace);
            row4.appendChild(spaceBtn);
        }
        const backspaceBtn = createSpecialKey('⌫', 'quiz-keyboard-key-backspace', 'Backspace', handleBackspace);
        row4.appendChild(backspaceBtn);
        container.appendChild(row4);

        targetEl.innerHTML = '';
        targetEl.appendChild(container);

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
            setOptions(opts) {
                if (opts.maxLength !== undefined) state.maxLength = opts.maxLength;
            },
            destroy() {
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

    function destroy() {
        if (instance && typeof instance.destroy === 'function') {
            instance.destroy();
        }
        instance = null;
    }

    global.initQuizKeyboard = initQuizKeyboard;
    global.setQuizKeyboardEnabled = setEnabled;
    global.destroyQuizKeyboard = destroy;
})(typeof window !== 'undefined' ? window : this);
