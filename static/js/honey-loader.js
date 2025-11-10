// Dark Honeycomb Loader – canonical implementation (weighted gated tasks + optional diagnostics + matrix stop)
(function(){
  const overlay = document.getElementById('appHoneyLoader');
  if(!overlay){ return; }

  // Elements
  const percentEl = document.getElementById('loaderPercentText');
  const taskEl = document.getElementById('loaderProcessName');
  const detailEl = document.getElementById('loaderStatusDetail');
  const ringEl = document.querySelector('.progress-ring');
  const ariaEl = document.getElementById('loaderAriaStatus');
  const skipBtn = document.getElementById('skipLoaderBtn');

  // Diagnostics enable switches (any truthy path turns it on)
  const diagEnabled = (
    overlay.dataset.diagnostics === '1' ||
    /[?&]loaderDiag=1/.test(location.search) ||
    localStorage.getItem('honeyLoaderDiagnostics') === '1'
  );

  // Reduced motion support
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(prefersReduced){ overlay.classList.add('reduced-motion'); }

  // Matrix Rain Animation Setup - optimized for instant start
  function initMatrixRain(){
    let canvas = document.getElementById('matrixCanvas');
    if(!canvas){
      canvas = document.createElement('canvas');
      canvas.id = 'matrixCanvas';
      canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:0.6';
      overlay.insertBefore(canvas, overlay.firstChild);
    }
    
    const ctx = canvas.getContext('2d', { alpha: true });
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = [];
    
    // Initialize drops with random starting positions for instant effect
    for(let i = 0; i < columns; i++){
      drops[i] = Math.floor(Math.random() * canvas.height / fontSize);
    }
    
    function drawMatrix(){
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFD540'; // BeeSmart yellow
      ctx.font = fontSize + 'px monospace';
      
      for(let i = 0; i < drops.length; i++){
        const char = chars[Math.floor(Math.random() * chars.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;
        
        ctx.fillText(char, x, y);
        
        if(y > canvas.height && Math.random() > 0.975){
          drops[i] = 0;
        }
        drops[i]++;
      }
    }
    
    // Start animation immediately
    const matrixInterval = setInterval(drawMatrix, 33);
    
    // Cleanup on loader finish
    document.addEventListener('honeyLoaderFinished', () => {
      clearInterval(matrixInterval);
      if(canvas && canvas.parentNode){
        canvas.style.opacity = '0';
        setTimeout(() => canvas.remove(), 500);
      }
    }, {once: true});
    
    // Handle resize efficiently
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        drops.length = Math.floor(canvas.width / fontSize);
        for(let i = 0; i < drops.length; i++){
          if(drops[i] === undefined) drops[i] = Math.floor(Math.random() * canvas.height / fontSize);
        }
      }, 100);
    });
  }
  
  // Start matrix animation immediately (before tasks)
  initMatrixRain();

    // System checks with realistic timing - minimum 65% before page loads
  const tasks = [
    // Quick startup (0-20%)
    { 
      name: 'System Health', 
      weight: 20, 
      detail: 'Checking server status…',
      expected: 800,
      fn: async () => {
        // Real health check with timeout
        try {
          const response = await Promise.race([
            fetch('/health', {cache: 'no-store'}),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000))
          ]);
          await new Promise(resolve => setTimeout(resolve, 600)); // Ensure visible time
          return response.ok ? {status: 'ok'} : {status: 'degraded'};
        } catch(e) {
          await new Promise(resolve => setTimeout(resolve, 600));
          return {status: 'degraded'}; // Continue anyway
        }
      }
    },
    // Word system (20-40%)
    { 
      name: 'Quiz Content', 
      weight: 20, 
      detail: 'Loading word system…',
      expected: 800,
      fn: async () => {
        // Check wordbank
        try {
          const response = await fetch('/api/wordbank', {cache: 'no-store'});
          await new Promise(resolve => setTimeout(resolve, 600));
          return response.ok ? {loaded: true} : {loaded: false};
        } catch(e) {
          await new Promise(resolve => setTimeout(resolve, 600));
          return {loaded: false};
        }
      }
    },
    // Avatar system (40-70%) - CRITICAL CHECKPOINT
    { 
      name: 'Avatar System', 
      weight: 30, 
      detail: 'Preparing avatars…',
      expected: 1000,
      fn: async () => {
        // Preload guest carousel avatars (priority picks for non-registered users)
        const base = '/static/assets/avatars/glb_files/AvatarThumbnails';
        const carouselAvatars = [
          'SuperBee!.png',
          'QueenBee!.png', 
          'JRockBee!.png',
          'BeeKnight!.png'
        ];
        
        console.log('🍯 Preloading carousel avatars for home page');
        const carouselPromises = carouselAvatars.map(file => {
          return new Promise(resolve => {
            const img = new Image();
            img.onload = () => {
              console.log(`✅ Loaded carousel: ${file}`);
              resolve(true);
            };
            img.onerror = () => {
              console.warn(`⚠️ Failed carousel: ${file}`);
              resolve(false);
            };
            img.src = `${base}/${file}`;
          });
        });
        
        // Load all carousel avatars in parallel
        await Promise.all(carouselPromises);
        
        // Also check mascot avatar for registered users
        try {
          const mascotCheck = await fetch('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', {
            method: 'HEAD',
            cache: 'no-store'
          });
          if (!mascotCheck.ok) {
            console.warn('Mascot avatar missing, using fallback');
          }
          return {ready: true, carouselLoaded: true};
        } catch(e) {
          console.warn('Mascot check failed:', e);
          return {ready: false, carouselLoaded: true};
        }
      }
    },
    // UI preparation (70-90%)
    { 
      name: 'Interface Ready', 
      weight: 20, 
      detail: 'Initializing interface…',
      expected: 600,
      fn: async () => {
        await new Promise(resolve => setTimeout(resolve, 500));
        return {ready: true};
      }
    },
    // Final touches (90-100%)
    { 
      name: 'System Ready', 
      weight: 10, 
      detail: 'Starting BeeSmart…',
      expected: 400,
      fn: async () => {
        await new Promise(resolve => setTimeout(resolve, 300));
        document.dispatchEvent(new CustomEvent('systemChecks:done'));
        return {ready: true};
      }
    }
  ];
  const totalWeight = tasks.reduce((a,t)=>a+t.weight,0) || 100;

  // State
  const MIN_DISPLAY_MS = 0; // No minimum - instant when ready
  const SAFETY_TIMEOUT_MS = 3000; // 3 second hard cap
  let finished = false;
  let finishRequested = false;
  let currentIndex = 0;
  let accumulated = 0;
  const startTs = performance.now();
  const timings = [];

  // Utility helpers - simplified
  function setProgress(pct,label){
    pct = Math.max(0, Math.min(100, pct));
    if(percentEl) percentEl.textContent = pct.toFixed(0) + '%';
    if(taskEl) taskEl.textContent = label || '';
    if(ringEl) ringEl.style.setProperty('--p', pct + '%');
    if(ariaEl && (!setProgress._last || Math.abs(pct - setProgress._last) >= 5)){
      ariaEl.textContent = `Loading: ${label || ''} (${pct.toFixed(0)}%)`;
      setProgress._last = pct;
    }
  }
  function setDetail(txt){ if(detailEl) detailEl.textContent = txt || ''; }

  function finish(){
    if(finished) return;
    finished = true;
    finishRequested = true;
    
    setProgress(100,'Ready');
    setDetail('Complete!');
    
    // UNLOCK PAGE IMMEDIATELY - Don't wait for anything
    console.log('🍯 UNLOCKING PAGE NOW');
    document.body.style.pointerEvents = 'auto';
    document.body.style.overflow = 'auto';
    document.body.style.userSelect = 'auto';
    
    // Remove overlay from DOM flow immediately
    if(overlay) {
      overlay.style.pointerEvents = 'none';
      overlay.style.zIndex = '-1';
      console.log('🍯 Overlay disabled for interactions');
    }
    
    // Dispatch event for page initialization (non-blocking)
    try { 
      document.dispatchEvent(new Event('honeyLoaderFinished')); 
      console.log('🍯 Honey loader finished, dispatched event');
    } catch(e) {
      console.error('Error dispatching honeyLoaderFinished:', e);
    }
    
    // Hide loader overlay visually
    if(overlay) {
      overlay.style.transition = 'opacity 0.3s ease';
      overlay.style.opacity = '0';
      setTimeout(() => { 
        overlay.style.display = 'none';
        overlay.remove(); // Completely remove from DOM
        console.log('🍯 Loader removed from DOM');
      }, 300);
    }
  }

  // Single safety timeout - force finish if loader hangs
  setTimeout(()=>{ 
    if(!finished) {
      console.warn('🍯 SAFETY TIMEOUT: Forcing loader to finish');
      finish(); 
    }
  }, SAFETY_TIMEOUT_MS);
  
  // Emergency page unlock after 10 seconds if EVERYTHING fails
  setTimeout(() => {
    if(overlay && overlay.style.display !== 'none') {
      console.error('🍯 EMERGENCY UNLOCK: Page frozen, forcing unlock');
      overlay.style.display = 'none';
      document.body.style.pointerEvents = 'auto';
      document.body.style.overflow = 'auto';
    }
  }, 10000);

  if(skipBtn){
    skipBtn.addEventListener('click', ()=>{ showSkip(); finish(); });
  }
  window.addEventListener('systemChecks:done', finish);

  // Diagnostics overlay construction
  let diagEl;
  function initDiagnostics(){
    if(!diagEnabled) return;
    diagEl = document.createElement('div');
    diagEl.id = 'honeyLoaderDiagnostics';
    diagEl.style.cssText = 'position:fixed;top:8px;right:8px;z-index:99999;font:12px/1.3 monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:280px;box-shadow:0 0 6px #000;';
    diagEl.innerHTML = '<strong>Loader Diagnostics</strong><div style="margin-top:4px" id="honeyLoaderDiagRows"></div><div id="honeyLoaderDiagNow" style="margin-top:2px;color:#ccc;font-size:11px">Now: 0%</div><div style="margin-top:6px" id="honeyLoaderDiagSparkline"></div><div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>';
    document.body.appendChild(diagEl);
  }
  function updateDiag(){
    if(!diagEnabled || !diagEl) return;
    const rowsEl = diagEl.querySelector('#honeyLoaderDiagRows');
    const footer = diagEl.querySelector('#honeyLoaderDiagFooter');
    const spark = diagEl.querySelector('#honeyLoaderDiagSparkline');
    rowsEl.innerHTML = timings.map(t => {
      const dur = (t.duration).toFixed(0);
      return `<div>${t.name}</div><div style="color:#aaa;margin-left:6px">${dur} ms</div>`;
    }).join('');
    if(spark){
      if(!timings.length){
        spark.innerHTML = '<div style="opacity:.6">(waiting for data…)</div>';
      } else {
        const max = Math.max(...timings.map(t=>t.duration),1);
        const w = 240, h = 34, pad = 5;
        const pts = timings.map((t,i)=>{
          const x = pad + (i/(timings.length-1||1))*(w-pad*2);
          const y = h - pad - (t.duration/max)*(h-pad*2);
          return `${x},${y}`;
        });
        const last = pts[pts.length-1].split(',');
        const svg = `<svg viewBox='0 0 ${w} ${h}' width='${w}' height='${h}' preserveAspectRatio='none'>`
          + `<polyline points='${pts.join(' ')}' fill='none' stroke='#f8d25c' stroke-width='2' stroke-linejoin='round' />`
          + `<circle cx='${last[0]}' cy='${last[1]}' r='3' fill='#f0c246' stroke='#332600' stroke-width='1' />`
          + `</svg>`;
        spark.innerHTML = svg;
      }
    }
    const total = (performance.now() - startTs).toFixed(0);
    footer.textContent = `Total: ${total} ms | ${(timings.reduce((a,t)=>a+t.duration,0)).toFixed(0)} ms task time`;
  }
  function flushDiagnostics(){ updateDiag(); }

  initDiagnostics();

  // START MATRIX ANIMATION IMMEDIATELY for instant visual feedback
  console.log('🍯 Starting Matrix rain animation FIRST');
  initMatrixRain();

  // Simplified execution - no interpolation, instant progress
  function runNext(){
    if(finished) return;
    if(currentIndex >= tasks.length){ 
      console.log('🍯 All tasks complete, calling finish()');
      finish(); 
      return; 
    }
    const t = tasks[currentIndex];
    const weightPct = (t.weight / totalWeight) * 100;
    setProgress(accumulated, t.name);
    setDetail(t.detail);
    console.log(`🍯 Running task ${currentIndex + 1}/${tasks.length}: ${t.name}`);
    
    let p;
    try { p = t.fn(); } catch(e){ 
      console.error(`Task ${t.name} error:`, e);
      p = Promise.resolve(); 
    }
    
    Promise.resolve(p)
      .catch(() => ({}))
      .finally(()=>{
        accumulated = Math.min(100, accumulated + weightPct);
        setProgress(accumulated, t.name);
        currentIndex++;
        runNext();
      });
  }

  // Give Matrix 100ms to start rendering, THEN begin system checks
  console.log('🍯 Delaying system checks to let Matrix animation start');
  setTimeout(() => {
    console.log('🍯 Beginning system checks now');
    runNext();
  }, 100);
  })();
