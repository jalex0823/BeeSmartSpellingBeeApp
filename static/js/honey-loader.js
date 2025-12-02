// Minimal Honey Loader Stub - ULTRA FAST EMERGENCY MODE
(function(){
  const overlay = document.getElementById('appHoneyLoader');
  if(!overlay) {
    console.warn('🍯 Loader overlay not found, forcing page unlock');
    document.body.style.pointerEvents='auto';
    document.body.style.overflow='auto';
    document.body.style.userSelect='auto';
    return;
  }
  
  console.log('🍯 EMERGENCY MODE: Ultra-fast loader starting');
  
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
    console.log('🍯 Loader finishing, unlocking page');
    
    // UNLOCK PAGE IMMEDIATELY
    document.body.style.pointerEvents='auto';
    document.body.style.overflow='auto';
    document.body.style.userSelect='auto';
    
    // Dispatch event
    try{ 
      document.dispatchEvent(new Event('honeyLoaderFinished')); 
      console.log('🍯 honeyLoaderFinished event dispatched');
    }catch(e){ 
      console.error('🍯 Error dispatching event:', e);
    }
    
    // Hide overlay
    if(overlay){ 
      overlay.style.opacity='0'; 
      overlay.style.pointerEvents='none'; 
      setTimeout(()=>{ 
        overlay.style.display='none';
        overlay.remove();
        console.log('🍯 Loader removed from DOM');
      },200); 
    }
  }
  
  // ULTRA FAST SEQUENCE - finish in 100ms
  set(10,'Init','Starting…');
  setTimeout(()=>set(50,'Ready','Almost there…'),50);
  setTimeout(()=>finish(),100);
  
  // Emergency failsafe - force finish after 1 second no matter what
  setTimeout(()=>{ 
    if(overlay && overlay.style.display!=='none') {
      console.error('🍯 EMERGENCY FAILSAFE: Force finishing loader');
      finish(); 
    }
  },1000);
  
  // Nuclear option - force unlock after 3 seconds
  setTimeout(()=>{
    if(document.body.style.pointerEvents !== 'auto'){
      console.error('🍯 NUCLEAR OPTION: Force unlocking page');
      document.body.style.pointerEvents='auto';
      document.body.style.overflow='auto';
      document.body.style.userSelect='auto';
      if(overlay) overlay.style.display='none';
    }
  },3000);
})();