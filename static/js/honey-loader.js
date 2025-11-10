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

  // Weighted tasks (sum to 100) – adjust weights to perceived duration
  const tasks = [
    { name:'Core',        weight:10, detail:'Preparing interface…', fn: corePrep },
    { name:'Health',      weight:20, detail:'Checking system health…', fn: () => fetchJson('/health') },
    { name:'Wordbank',    weight:35, detail:'Loading word lists…', fn: () => fetchJson('/api/wordbank') },
    { name:'Avatars',     weight:15, detail:'Caching avatars…', fn: () => delay(600) },
    { name:'Definitions', weight:20, detail:'Priming dictionary cache…', fn: () => delay(500) }
  ];
  const totalWeight = tasks.reduce((a,t)=>a+t.weight,0) || 100;

  // State
  let finished = false;
  let currentIndex = 0;
  let accumulated = 0; // percent already allocated
  const startTs = performance.now();
  const timings = []; // {name,start,end,duration}

  // Utility helpers
  function corePrep(){
    ['/static/images/backgrounds/HoneyCombBg2.png','/static/BeeSmartCrestLogo1.png'].forEach(u=>{ const img=new Image(); img.src=u; });
    return Promise.resolve();
  }
  function fetchJson(url){ return fetch(url,{cache:'no-store'}).then(r=>r.json()).catch(()=>({error:true})); }
  function delay(ms){ return new Promise(res=>setTimeout(res,ms)); }

  function setProgress(pct,label){
    pct = Math.max(0, Math.min(100, pct));
    if(percentEl) percentEl.textContent = pct.toFixed(0) + '%';
    if(taskEl) taskEl.textContent = label || '';
    if(ringEl) ringEl.style.setProperty('--p', pct + '%');
    // ARIA throttling
    if(!setProgress._last || Math.abs(pct - setProgress._last.pct) >= 2 || setProgress._last.label !== label){
      if(ariaEl) ariaEl.textContent = `Loading: ${label || ''} (${pct.toFixed(0)} percent)`;
      setProgress._last = {pct,label};
    }
  }
  function setDetail(txt){ if(detailEl) detailEl.textContent = txt || ''; }
  function showSkip(){ if(skipBtn && skipBtn.hidden){ skipBtn.hidden = false; } }

  function finish(){
    if(finished) return;
    finished = true;
    setProgress(100,'Ready');
    setDetail('');
    try { document.dispatchEvent(new Event('honeyLoaderFinished')); } catch {}
    overlay.classList.add('loader-complete');
    setTimeout(()=>{ overlay.style.opacity='0'; },50);
    setTimeout(()=>{ overlay.style.display='none'; },600);
    if(diagEnabled){ flushDiagnostics(); }
  }

  // Perception nudge & safety
  setTimeout(()=>{ if(!finished && currentIndex === 0){ setDetail('Still working…'); showSkip(); } },2500);
  setTimeout(()=>{ if(!finished) finish(); },9000);

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
    diagEl.style.cssText = 'position:fixed;top:8px;right:8px;z-index:99999;font:12px/1.3 monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:260px;box-shadow:0 0 6px #000;';
    diagEl.innerHTML = '<strong>Loader Diagnostics</strong><div style="margin-top:4px" id="honeyLoaderDiagRows"></div><div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>';
    document.body.appendChild(diagEl);
  }
  function updateDiag(){
    if(!diagEnabled || !diagEl) return;
    const rowsEl = diagEl.querySelector('#honeyLoaderDiagRows');
    const footer = diagEl.querySelector('#honeyLoaderDiagFooter');
    rowsEl.innerHTML = timings.map(t => {
      const dur = (t.duration).toFixed(0);
      return `<div>${t.name}</div><div style="color:#aaa;margin-left:6px">${dur} ms</div>`;
    }).join('');
    const total = (performance.now() - startTs).toFixed(0);
    footer.textContent = `Total: ${total} ms | ${(timings.reduce((a,t)=>a+t.duration,0)).toFixed(0)} ms task time`;
  }
  function flushDiagnostics(){ updateDiag(); }

  initDiagnostics();

  function runNext(){
    if(finished) return;
    if(currentIndex >= tasks.length){ finish(); return; }
    const t = tasks[currentIndex];
    const weightPct = (t.weight / totalWeight) * 100;
    setProgress(accumulated, t.name);
    setDetail(t.detail);
    const taskStart = performance.now();
    let p;
    try { p = t.fn(); } catch(e){ p = Promise.resolve({error:true}); }
    Promise.resolve(p).finally(()=>{
      const end = performance.now();
      const duration = end - taskStart;
      timings.push({name:t.name,start:taskStart,end,duration});
      accumulated = Math.min(99, accumulated + weightPct);
      setProgress(accumulated, t.name);
      currentIndex++;
      if(currentIndex < tasks.length){
        const next = tasks[currentIndex];
        // Show upcoming task name early for user context
        if(taskEl) taskEl.textContent = next.name;
        setDetail(next.detail);
      }
      if(diagEnabled){ updateDiag(); }
      runNext();
    });
  }

  // Kick off sequence
  runNext();
})();
// Dark Honeycomb Loader — gated progress with matrix background
(function(){
  const overlay = document.getElementById('appHoneyLoader');
  if (!overlay) return;
  window.addEventListener('systemChecks:done', finish);
})();
  function finish(){
    if(done) return;
    done = true;
    setProgress(100, 'Ready');
    setDetail('');
    // Stop matrix animation
      })();
      pct = Math.max(0, Math.min(100, pct));
