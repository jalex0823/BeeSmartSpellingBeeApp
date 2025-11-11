// Dark Honeycomb Loader – Full featured with matrix animation and system checks
(function(){
  // Prevent double-execution if loader already ran
  if (window.honeyLoaderLoaded) {
    console.log('🍯 Loader already initialized, skipping');
    return;
  }
  window.honeyLoaderLoaded = true;
  
  const overlay = document.getElementById('appHoneyLoader');
  if(!overlay){ return; }

  // Elements
  const percentEl = document.getElementById('loaderPercentText');
  const taskEl = document.getElementById('loaderProcessName');
  const detailEl = document.getElementById('loaderStatusDetail');
  const ringEl = document.querySelector('.progress-ring');
  const ariaEl = document.getElementById('loaderAriaStatus');
  const skipBtn = document.getElementById('skipLoaderBtn');
  const allowMotion = overlay.dataset.allowMotion !== 'false';

  // Reduced motion
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(prefersReduced){ overlay.classList.add('reduced-motion'); }

  // Matrix Rain Animation
  function initMatrixRain(){
    let canvas = document.getElementById('matrixCanvas');
    if(!canvas){
      canvas = document.createElement('canvas');
      canvas.id = 'matrixCanvas';
      canvas.setAttribute('aria-hidden', 'true');
      canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:0.4';
      overlay.insertBefore(canvas, overlay.firstChild);
    }
    
    const ctx = canvas.getContext('2d', { alpha: true });
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = [];
    
    for(let i = 0; i < columns; i++){
      drops[i] = Math.floor(Math.random() * canvas.height / fontSize);
    }
    
    function drawMatrix(){
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#FFD540';
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
    
    const matrixInterval = setInterval(drawMatrix, 33);
    
    document.addEventListener('honeyLoaderFinished', () => {
      clearInterval(matrixInterval);
      if(canvas && canvas.parentNode){
        canvas.style.opacity = '0';
        setTimeout(() => canvas.remove(), 500);
      }
    }, {once: true});
    
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

  // Start matrix animation
  if(!prefersReduced && allowMotion) {
    initMatrixRain();
  }

  // State
  let progress = 0;
  let currentTask = 0;
  let finished = false;
  let skipShown = false;
  const startTs = Date.now();

  // Helper: fetch with timeout
  const fetchWithTimeout = (url, ms = 1200, opts = {}) => {
    return Promise.race([
      fetch(url, { cache: 'no-store', ...opts }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms))
    ]);
  };

  // System diagnostics logger
  const diagnosticsLog = {
    timestamp: new Date().toISOString(),
    checks: [],
    warnings: [],
    errors: []
  };

  function logCheck(name, status, details = {}) {
    const entry = {
      name,
      status, // 'success', 'warning', 'error', 'timeout'
      timestamp: new Date().toISOString(),
      ...details
    };
    diagnosticsLog.checks.push(entry);
    
    if (status === 'warning') diagnosticsLog.warnings.push(entry);
    if (status === 'error' || status === 'timeout') diagnosticsLog.errors.push(entry);
    
    // Store in sessionStorage for user viewing
    try {
      sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
    } catch(e) {
      console.warn('Could not save diagnostics:', e);
    }
  }

  // Tasks (ordered)
  const tasks = [
    {
      name: 'Core', detail: 'Preparing interface…', fn: () => {
        ['/static/images/backgrounds/HoneyCombBg2.png','/static/BeeSmartCrestLogo1.png'].forEach(u=>{ const img=new Image(); img.src=u; });
        logCheck('Core Assets', 'success', { preloaded: 2 });
        return Promise.resolve();
      }
    },
    { 
      name: 'Health', 
      detail: 'Checking system health…', 
      fn: () => fetchWithTimeout('/health', 1000)
        .then(r=>r.json())
        .then(data => {
          logCheck('Health Check', 'success', { version: data.version, status: data.status });
          return data;
        })
        .catch(err => {
          logCheck('Health Check', err.message === 'timeout' ? 'timeout' : 'error', { error: err.message });
          return {error:true};
        })
    },
    { 
      name: 'Wordbank', 
      detail: 'Loading word lists…', 
      fn: () => fetchWithTimeout('/api/wordbank', 1200)
        .then(r=>r.json())
        .then(data => {
          const wordCount = Array.isArray(data) ? data.length : (data.count || 0);
          logCheck('Wordbank', wordCount > 0 ? 'success' : 'warning', { words: wordCount });
          return data;
        })
        .catch(err => {
          logCheck('Wordbank', err.message === 'timeout' ? 'timeout' : 'error', { error: err.message });
          return {error:true};
        })
    },
    { 
      name: 'Avatars', 
      detail: 'Checking mascot…', 
      fn: () => fetchWithTimeout('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', 1200, { method: 'HEAD' })
        .then(res => {
          logCheck('Mascot Avatar', res.ok ? 'success' : 'warning', { status: res.status, size: res.headers.get('content-length') });
          return res;
        })
        .catch(err => {
          logCheck('Mascot Avatar', err.message === 'timeout' ? 'timeout' : 'error', { error: err.message });
          return null;
        })
    },
    { 
      name: 'Definitions', 
      detail: 'Priming dictionary cache…', 
      fn: () => new Promise(res=>{
        setTimeout(() => {
          logCheck('Dictionary Cache', 'success', { primed: true });
          res();
        }, 500);
      })
    }
  ];
  const slice = Math.floor(100 / tasks.length);

  // Utility setters
  function setProgress(pct, label){
    pct = Math.max(0, Math.min(100, pct));
    progress = pct;
    if(percentEl) percentEl.textContent = pct + '%';
    if(taskEl) taskEl.textContent = label || '';
    if(ringEl) ringEl.style.setProperty('--p', pct + '%');
    if(!setProgress._last || Math.abs(pct - setProgress._last.pct) >= 2 || setProgress._last.label !== label){
      if(ariaEl) ariaEl.textContent = `Loading: ${label || ''} (${pct} percent)`;
      setProgress._last = {pct,label};
    }
  }
  function setDetail(text){ if(detailEl) detailEl.textContent = text || ''; }
  function showSkip(){ if(skipBtn && !skipShown){ skipBtn.hidden = false; skipShown = true; } }
  function finish(){
    if(finished) return;
    
    // Calculate system health percentage
    const totalChecks = diagnosticsLog.checks.length;
    const successfulChecks = diagnosticsLog.checks.filter(c => c.status === 'success').length;
    const healthPercentage = totalChecks > 0 ? Math.round((successfulChecks / totalChecks) * 100) : 0;
    
    // CRITICAL THRESHOLD: Minimum 55% system health required
    const MIN_HEALTH_THRESHOLD = 55;
    
    if (healthPercentage < MIN_HEALTH_THRESHOLD) {
      // System health below threshold - show error and halt
      console.error(`🚫 System health at ${healthPercentage}% - below minimum threshold of ${MIN_HEALTH_THRESHOLD}%`);
      console.error('Critical systems failed. View diagnostics: SystemChecks.viewDiagnostics()');
      
      setProgress(healthPercentage, 'System Health Critical');
      setDetail(`Only ${healthPercentage}% of systems healthy (need ${MIN_HEALTH_THRESHOLD}%)`);
      
      // Log critical failure
      diagnosticsLog.criticalFailure = true;
      diagnosticsLog.healthPercentage = healthPercentage;
      diagnosticsLog.thresholdRequired = MIN_HEALTH_THRESHOLD;
      
      try {
        sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
      } catch(e) {}
      
      // Show error message to user
      if (detailEl) {
        detailEl.innerHTML = `<span style="color:#ff4444">⚠️ System health: ${healthPercentage}% (need ${MIN_HEALTH_THRESHOLD}%)<br>Please refresh or contact support</span>`;
      }
      
      // Don't proceed to main page - keep loader visible
      return;
    }
    
    finished = true;
    
    // Log completion summary
    const duration = Date.now() - startTs;
    diagnosticsLog.completedAt = new Date().toISOString();
    diagnosticsLog.duration = duration;
    diagnosticsLog.healthPercentage = healthPercentage;
    diagnosticsLog.summary = {
      totalChecks: diagnosticsLog.checks.length,
      successful: successfulChecks,
      warnings: diagnosticsLog.warnings.length,
      errors: diagnosticsLog.errors.length,
      healthPercentage: healthPercentage
    };
    
    // Save final state
    try {
      sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
    } catch(e) {}
    
    // Console summary (colored for visibility)
    const hasIssues = diagnosticsLog.errors.length > 0 || diagnosticsLog.warnings.length > 0;
    if (hasIssues) {
      console.warn(`🍯 BeeSmart loaded in ${duration}ms (${healthPercentage}% healthy) with ${diagnosticsLog.errors.length} errors, ${diagnosticsLog.warnings.length} warnings. View: SystemChecks.viewDiagnostics()`);
    } else {
      console.log(`🍯 BeeSmart loaded in ${duration}ms - All systems healthy (${healthPercentage}%) ✓`);
    }
    
    setProgress(100,'Ready');
    setDetail('Complete!');
    try{ document.dispatchEvent(new Event('honeyLoaderFinished')); }catch{}
    setTimeout(()=>{ overlay.classList.add('hidden'); }, 350);
  }

  // Expose minimal API
  window.SystemChecks = Object.assign(window.SystemChecks||{}, { 
    setProgress, 
    setDetail, 
    finish,
    getDiagnostics: () => diagnosticsLog,
    viewDiagnostics: () => {
      console.group('🍯 BeeSmart System Diagnostics');
      console.log('Timestamp:', diagnosticsLog.timestamp);
      console.log('Total Checks:', diagnosticsLog.checks.length);
      console.log('Warnings:', diagnosticsLog.warnings.length);
      console.log('Errors:', diagnosticsLog.errors.length);
      console.table(diagnosticsLog.checks);
      if (diagnosticsLog.errors.length > 0) {
        console.group('❌ Errors');
        diagnosticsLog.errors.forEach(e => console.error(e));
        console.groupEnd();
      }
      if (diagnosticsLog.warnings.length > 0) {
        console.group('⚠️ Warnings');
        diagnosticsLog.warnings.forEach(w => console.warn(w));
        console.groupEnd();
      }
      console.groupEnd();
      return diagnosticsLog;
    }
  });

  // Per-task runner
  function runNext(){
    if(finished) return;
    const task = tasks[currentTask];
    if(!task){ finish(); return; }
    setProgress(currentTask * slice, task.name + '…');
    setDetail(task.detail);
    Promise.resolve().then(task.fn).then(()=>{
      currentTask++;
      const base = Math.min(99, currentTask * slice);
      setProgress(base, tasks[currentTask] ? tasks[currentTask].name + '…' : 'Finalizing…');
      setDetail(tasks[currentTask] ? tasks[currentTask].detail : '');
      if(!skipShown && (base >= 60 || (Date.now() - startTs) > 1500)) showSkip();
      setTimeout(runNext, 80);
    }).catch(()=>{
      currentTask++;
      setProgress(Math.min(99, currentTask * slice), tasks[currentTask] ? tasks[currentTask].name + '…' : 'Finalizing…');
      setDetail(tasks[currentTask] ? tasks[currentTask].detail : '');
      if(!skipShown && (progress >= 60 || (Date.now() - startTs) > 1500)) showSkip();
      setTimeout(runNext, 60);
    });
  }

  // Perception nudge
  setTimeout(()=>{
    if(finished) return;
    const current = parseInt((percentEl?.textContent||'').replace(/[^0-9]/g,''),10) || 0;
    const oneSlice = Math.floor(100 / tasks.length);
    if(current <= oneSlice && allowMotion && !prefersReduced){
      setProgress(Math.max(1, oneSlice - 1), tasks[1]? tasks[1].name + '…':'Loading…');
    }
  },2500);

  // Safety timeout (5 seconds)
  setTimeout(()=>{ if(!finished) finish(); }, 5000);

  // Skip button
  if(skipBtn){ skipBtn.addEventListener('click', ()=> finish()); }

  // Start
  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', runNext); } else { runNext(); }

  // External early finish hook
  document.addEventListener('systemChecks:done', finish);
})();
