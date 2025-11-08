// Loading Screen Manager
(function(){
  const OVERLAY_ID = 'loadingOverlay';
  const CHECKS_CONTAINER_ID = 'loadingChecks';
  const START_BTN_ID = 'loadingStartBtn';
  const SKIP_KEY = 'bs_skip_overlay';

  function el(id){ return document.getElementById(id); }
  function qs(sel, root=document){ return root.querySelector(sel); }
  function iconFor(st){
    if(st === 'success') return '✅';
    if(st === 'error') return '❌';
    return '⏳';
  }
  function getParam(name){
    try { return new URLSearchParams(window.location.search).get(name); } catch(_) { return null; }
  }
  function forceLoad(){ return getParam('forceLoad') === '1'; }
  function shouldSkip(){ try { return localStorage.getItem(SKIP_KEY) === '1' && !forceLoad(); } catch(_) { return false; } }

  const checks = [
    { id:'env', label:'Environment ready', status:'pending' },
    { id:'dictionary', label:'Dictionary cache warmed', status:'pending' },
    { id:'avatars', label:'Avatars prepared', status:'pending' },
    { id:'quiz', label:'Quiz engine primed', status:'pending' },
    { id:'auth', label:'Session ready', status:'pending' }
  ];

  function renderChecks(){
    const c = el(CHECKS_CONTAINER_ID); if(!c) return;
    c.innerHTML = '';
    checks.forEach(ch => {
      const row = document.createElement('div');
      row.className = 'check-item ' + ch.status;
      row.dataset.checkId = ch.id;
      row.innerHTML = `<span class="check-icon">${iconFor(ch.status)}</span><span>${ch.label}</span>`;
      c.appendChild(row);
    });
  }

  function updateCheck(id, status){
    const ch = checks.find(x=>x.id===id); if(!ch) return;
    ch.status = status;
    const row = el(CHECKS_CONTAINER_ID)?.querySelector('[data-check-id="'+id+'"]');
    if(row){
      row.className = 'check-item ' + status;
      const icon = row.querySelector('.check-icon');
      if(icon) icon.textContent = iconFor(status);
    }
    verifyReady();
  }

  function verifyReady(){
    const allOk = checks.every(c => c.status === 'success');
    const btn = el(START_BTN_ID);
    if(btn){ btn.disabled = !allOk; if(allOk) btn.classList.add('pulse-btn'); }
    return allOk;
  }

  async function fetchWithTimeout(url, opts={}, timeoutMs=3000){
    const ctrl = new AbortController();
    const t = setTimeout(()=>ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(url, { ...opts, signal: ctrl.signal, cache: 'no-store' });
      clearTimeout(t);
      return res;
    } catch(e){ clearTimeout(t); throw e; }
  }

  async function checkEnv(){
    try {
      const res = await fetchWithTimeout('/health');
      if(!res.ok) throw new Error('health not ok');
      const j = await res.json().catch(()=>({}));
      if(!j || typeof j !== 'object') throw new Error('health invalid');
      updateCheck('env','success');
    } catch(e){ updateCheck('env','error'); }
  }
  async function checkDictionary(){
    try {
      const res = await fetchWithTimeout('/api/wordbank');
      if(!res.ok) throw new Error('wordbank not ok');
      await res.json().catch(()=>({}));
      updateCheck('dictionary','success');
    } catch(e){ updateCheck('dictionary','error'); }
  }
  async function checkAvatars(){
    try {
      // Lightweight script probe to ensure avatar system assets reachable
      const res = await fetchWithTimeout('/static/js/user-avatar-loader.js');
      if(!res.ok) throw new Error('avatar script missing');
      updateCheck('avatars','success');
    } catch(e){ updateCheck('avatars','error'); }
  }
  async function checkQuiz(){
    try {
      // If celebrations module is present, consider quiz UI primed
      if (window.QuizCelebrations && typeof window.QuizCelebrations.getEnabled === 'function') {
        updateCheck('quiz','success');
        return;
      }
      // Fallback: verify the script is fetchable
      const res = await fetchWithTimeout('/static/js/quiz-celebrations.js');
      if(!res.ok) throw new Error('quiz script missing');
      updateCheck('quiz','success');
    } catch(e){ updateCheck('quiz','error'); }
  }
  async function checkAuth(){
    try {
      // Guest mode is acceptable; success if session cookie present or server reachable
      const hasSession = (document.cookie || '').includes('session=');
      if (hasSession) { updateCheck('auth','success'); return; }
      const res = await fetchWithTimeout('/api/wordbank');
      if(res.ok) { updateCheck('auth','success'); return; }
      updateCheck('auth','error');
    } catch(e){ updateCheck('auth','error'); }
  }

  async function runChecks(){
    // Run in parallel for speed; updates land individually
    await Promise.allSettled([
      checkEnv(),
      checkDictionary(),
      checkAvatars(),
      checkQuiz(),
      checkAuth()
    ]);
  }

  function hideOverlay(){
    const ov = el(OVERLAY_ID); if(!ov) return;
    ov.classList.add('hidden');
  }

  function init(){
    const ov = el(OVERLAY_ID);
    // Provide global API early
    window.LoadingScreenManager = {
      mark: updateCheck,
      hide: hideOverlay,
      show: () => { ov && ov.classList.remove('hidden'); },
      isComplete: () => checks.every(c=>c.status==='success')
    };

    if(!ov) return; // no overlay on this page

    if (shouldSkip()) {
      hideOverlay();
      return;
    }

    renderChecks();
    // Kick off real checks
    runChecks().then(()=>{
      // If everything is green and user hasn't clicked yet, allow auto-enable
      verifyReady();
    });

    const btn = el(START_BTN_ID);
    if(btn){
      btn.addEventListener('click', function(){
        if(btn.disabled) return;
        try { localStorage.setItem(SKIP_KEY, '1'); } catch(_){ }
        hideOverlay();
        // Accessibility: move focus to first focusable element in main
        try {
          const focusable = document.querySelector('main.container')?.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
          if(focusable && focusable.length > 0) focusable[0].focus();
        } catch(_){}
      });
    }
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
