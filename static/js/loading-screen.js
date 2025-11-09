// Loading Screen Manager (crest system checks)
(function(){
  const overlay = document.getElementById('loadingOverlay') || document.getElementById('honeyLoader');
  const CHECKS_CONTAINER_ID = document.getElementById('loadingChecks') ? 'loadingChecks' : (document.getElementById('checksList') ? 'checksList' : 'loadingChecks');
  const START_BTN_ID = 'loadingStartBtn';
  const SKIP_KEY = 'bs_skip_overlay';
  const MIN_READY_DELAY_MS = 600;       // brief pause
  const FAILSAFE_ENABLE_MS = 6000;      // if something stalls, still enable
  const FAILSAFE_AUTOHIDE_MS = 30000;   // plenty of time to tap

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
    // Dictionary is bundled in-app; this is a non-blocking informational check
    { id:'dictionary', label:'Dictionary (built-in)', status:'pending' },
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

  let gateOpened = false;
  function openGate(){
    if (gateOpened) return true;
    gateOpened = true;
    const btn = el(START_BTN_ID);
    if (btn) { btn.disabled = false; btn.classList.add('pulse-btn'); }
    return true;
  }
  function allChecksPassed(){ return checks.every(c=>c.status === 'success'); }
  function verifyReady(){
    if (allChecksPassed()) return openGate();
    return gateOpened;
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
    // Dictionary is bundled into the app; mark as success without network calls
    updateCheck('dictionary','success');
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
      // Guest mode acceptable; if session cookie exists, mark success, else treat as non-blocking success
      const hasSession = (document.cookie || '').includes('session=');
      updateCheck('auth', hasSession ? 'success' : 'success');
    } catch(e){ updateCheck('auth','success'); }
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
    if(!overlay) return;
    overlay.classList.add('hidden');
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';
    setTimeout(()=>{ overlay.style.display='none'; },350);
  }

  function init(){
    const ov = overlay;
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
    // Failsafe enable + optional auto-hide; but prefer user tap
    setTimeout(openGate, FAILSAFE_ENABLE_MS);
    setTimeout(hideOverlay, FAILSAFE_AUTOHIDE_MS);
    setTimeout(verifyReady, MIN_READY_DELAY_MS);
    // Kick off real checks
    runChecks().then(()=>{
      // If environment is fine, ensure the button is enabled now
      verifyReady();
    });

    const btn = el(START_BTN_ID);
    if (btn) {
      btn.addEventListener('click', () => {
        if (btn.disabled) return;
        try { localStorage.setItem(SKIP_KEY,'1'); } catch(_){ }
        hideOverlay();
        try {
          const focusable = document.querySelector('main.container')?.querySelectorAll('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])');
          if (focusable && focusable.length>0) focusable[0].focus();
        } catch(_){ }
      });
    }
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
