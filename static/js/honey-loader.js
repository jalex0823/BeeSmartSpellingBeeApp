// Minimal Honey Loader Stub
(function(){
  const overlay = document.getElementById('appHoneyLoader');
  if(!overlay) return;
  const percentEl = document.getElementById('loaderPercentText');
  const taskEl = document.getElementById('loaderProcessName');
  const detailEl = document.getElementById('loaderStatusDetail');
  const ariaEl = document.getElementById('loaderAriaStatus');
  function set(p,label,detail){
    if(percentEl) percentEl.textContent = p + '%';
    if(taskEl) taskEl.textContent = label||'';
    if(detailEl) detailEl.textContent = detail||'';
    if(ariaEl) ariaEl.textContent = 'Loading: '+(label||'')+' ('+p+'%)';
  }
  function finish(){
    set(100,'Ready','');
    try{ document.dispatchEvent(new Event('honeyLoaderFinished')); }catch{}
    if(overlay){ overlay.style.opacity='0'; overlay.style.pointerEvents='none'; setTimeout(()=>{ overlay.style.display='none'; },200); }
    document.body.style.pointerEvents='auto';
    document.body.style.overflow='auto';
    document.body.style.userSelect='auto';
  }
  set(10,'Init','Starting…');
  setTimeout(()=>set(40,'Prep','Loading…'),120);
  setTimeout(()=>set(75,'Finalizing','Unlocking…'),250);
  setTimeout(()=>finish(),420);
  setTimeout(()=>{ if(overlay && overlay.style.display!=='none') finish(); },3000);
})();