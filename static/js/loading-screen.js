// Loading Screen Manager
(function(){
  const OVERLAY_ID = 'loadingOverlay';
  const CHECKS_CONTAINER_ID = 'loadingChecks';
  const START_BTN_ID = 'loadingStartBtn';

  function el(id){ return document.getElementById(id); }

  const checks = [
    { id:'env', label:'Environment ready', status:'pending' },
    { id:'auth', label:'Auth system initialized', status:'pending' },
    { id:'dictionary', label:'Dictionary cache warmed', status:'pending' },
    { id:'avatars', label:'Avatars prepared', status:'pending' },
    { id:'quiz', label:'Quiz engine primed', status:'pending' }
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
  function iconFor(st){
    if(st === 'success') return '✅';
    if(st === 'error') return '❌';
    return '⏳';
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
  }
  function simulateProgress(){
    // Stagger updates for visual feedback
    const order = ['env','auth','dictionary','avatars','quiz'];
    order.forEach((id,idx)=>{
      setTimeout(()=> updateCheck(id,'success'), 450 + idx*450);
    });
  }
  function hideOverlay(){
    const ov = el(OVERLAY_ID); if(!ov) return;
    ov.classList.add('hidden');
  }
  function init(){
    const ov = el(OVERLAY_ID);
    if(!ov) return; // no overlay on this page
    renderChecks();
    simulateProgress();
    const btn = el(START_BTN_ID);
    if(btn){
      btn.addEventListener('click', function(){
        if(btn.disabled) return;
        hideOverlay();
        // Accessibility: move focus to first focusable element in main
        try {
          const focusable = document.querySelector('main.container')?.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
          if(focusable && focusable.length > 0) focusable[0].focus();
        } catch(_){}
      });
    }
    // Provide global API for future hook-ins
    window.LoadingScreenManager = {
      mark: updateCheck,
      hide: hideOverlay,
      show: () => { ov.classList.remove('hidden'); },
      isComplete: () => checks.every(c=>c.status==='success')
    };
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
