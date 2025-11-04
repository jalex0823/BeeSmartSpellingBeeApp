// Reusable Avatar Unlock Modal
// Usage: window.showAvatarUnlockModal([{ name, thumbnail, message, id }])
(function(){
    function createConfetti(container, count = 40) {
        for (let i = 0; i < count; i++) {
            const piece = document.createElement('div');
            piece.className = 'unlock-confetti';
            piece.style.left = Math.random() * 100 + '%';
            piece.style.background = ['#FFD700','#FFA500','#FF8C00','#FFF176'][i % 4];
            piece.style.animationDelay = (Math.random() * 1.5) + 's';
            piece.style.transform = `translateY(-${Math.random()*200+50}px)`;
            container.appendChild(piece);
        }
    }

    function modalContent(av) {
        const thumb = av.thumbnail || (av.urls && av.urls.thumbnail) || '';
        const safeName = av.name || 'New Bee';
        const msg = av.message || `You unlocked ${safeName}!`;
        return `
            <div class="unlock-modal-content" role="dialog" aria-live="assertive">
                <button class="locked-modal-close" aria-label="Close" onclick="this.parentElement.parentElement.remove()">×</button>
                <div class="unlock-modal-icon">🐝</div>
                <div class="unlock-modal-title">New Avatar Unlocked!</div>
                <div class="unlock-modal-subtitle">${safeName}</div>
                <div class="unlock-modal-avatar-preview">${thumb ? `<img src="${thumb}" alt="${safeName} thumbnail">` : '🐝'}</div>
                <div class="unlock-modal-description">${msg}</div>
                <div class="unlock-modal-buttons">
                    <a class="unlock-modal-btn" href="/honeycomb-avatar-picker" style="text-decoration:none;">Choose This Bee</a>
                    <button class="unlock-modal-btn secondary" onclick="this.closest('.avatar-unlock-modal').remove()">Keep Going</button>
                </div>
            </div>`;
    }

    function showModalFor(avOrList){
        const list = Array.isArray(avOrList) ? avOrList : [avOrList];
        if (!list.length) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'avatar-unlock-modal';
        wrapper.innerHTML = modalContent(list[0]);
        document.body.appendChild(wrapper);
        createConfetti(wrapper, 50);

        // If there are more, cycle on Keep Going to next one instead of closing
        if (list.length > 1) {
            const nextBtn = wrapper.querySelector('.unlock-modal-btn.secondary');
            if (nextBtn) {
                let idx = 0;
                nextBtn.addEventListener('click', function(ev){
                    ev.preventDefault();
                    idx++;
                    if (idx < list.length) {
                        const content = wrapper.querySelector('.unlock-modal-content');
                        if (content) content.outerHTML = modalContent(list[idx]);
                    } else {
                        wrapper.remove();
                    }
                });
            }
        }

        wrapper.addEventListener('click', (e)=>{ if (e.target === wrapper) wrapper.remove(); });
    }

    window.showAvatarUnlockModal = showModalFor;
})();
