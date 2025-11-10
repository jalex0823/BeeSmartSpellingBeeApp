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
    { name:'Core',        weight:10, detail:'Preparing interface…',              expected:300,  fn: corePrep },
    { name:'Health',      weight:20, detail:'Checking system health…',          expected:600,  fn: () => fetchJson('/health') },
    { name:'Wordbank',    weight:35, detail:'Loading word lists…',              expected:1400, fn: () => fetchJson('/api/wordbank') },
    { name:'Avatars',     weight:15, detail:'Caching avatars…',                 expected:700,  fn: () => delay(600) },
    { name:'Definitions', weight:20, detail:'Priming dictionary cache…',        expected:800,  fn: () => delay(500) }
  ];
  const totalWeight = tasks.reduce((a,t)=>a+t.weight,0) || 100;

  // State
  const MIN_DISPLAY_MS = 800; // ensure loader visible briefly
  const SAFETY_TIMEOUT_MS = 10000; // hard cap
  let finished = false;
  let finishRequested = false;
  let currentIndex = 0;
  let accumulated = 0; // percent already allocated
  const startTs = performance.now();
  const timings = []; // {name,duration}

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
    if(diagEl){
      const nowEl = diagEl.querySelector('#honeyLoaderDiagNow');
      if(nowEl) nowEl.textContent = `Now: ${pct.toFixed(0)}%`;
    }
  }
  function setDetail(txt){ if(detailEl) detailEl.textContent = txt || ''; }
  function showSkip(){ if(skipBtn && skipBtn.hidden){ skipBtn.hidden = false; } }

  function finish(){
    if(finished) return;
      if(finished || finishRequested) return;
      finishRequested = true;
      const elapsed = performance.now() - startTs;
      const wait = Math.max(0, MIN_DISPLAY_MS - elapsed);
      setTimeout(()=>{
        if(finished) return;
        finished = true;
        setProgress(100,'Ready');
        setDetail('');
        try { document.dispatchEvent(new Event('honeyLoaderFinished')); } catch {}
        overlay.classList.add('loader-complete');
        overlay.style.opacity='0';
        setTimeout(()=>{ overlay.style.display='none'; },500);
        if(diagEnabled){ flushDiagnostics(); }
      }, wait);
  }

  // Perception nudge & safety
  setTimeout(()=>{ if(!finished && currentIndex === 0){ setDetail('Still working…'); showSkip(); } },2500);
  setTimeout(()=>{ if(!finished) finish(); },9000);
  setTimeout(()=>{ if(!finished) finish(); }, SAFETY_TIMEOUT_MS);

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

  let _raf=0,_interpStart=0,_interpBase=0,_interpCap=0,_interpExpected=800,_interpLabel='';
  function stopInterpolation(){ if(_raf){ cancelAnimationFrame(_raf); _raf=0;} _interpStart=0; }
  function startInterpolation(base,cap,expected,label){
    stopInterpolation();
    _interpBase=base; _interpCap=cap; _interpExpected=Math.max(200,expected|0); _interpLabel=label||'';
    function step(ts){
      if(!_interpStart) _interpStart=ts;
      const elapsed=ts-_interpStart;
      const t=Math.min(0.99, elapsed/_interpExpected);
      const eased=1-Math.pow(1-t,2); // easeOutQuad
      const pct=_interpBase+(_interpCap-_interpBase)*eased;
      setProgress(pct,_interpLabel);
      if(pct < _interpCap - 0.05){ _raf=requestAnimationFrame(step);} else { _raf=0; }
    }
    _raf=requestAnimationFrame(step);
  }
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
    const cap = Math.min(99, accumulated + Math.max(0, weightPct - 0.5));
    startInterpolation(accumulated, cap, t.expected || 800, t.name);
    Promise.resolve(p).finally(()=>{
      stopInterpolation();
      const duration = performance.now() - taskStart;
      timings.push({name:t.name,duration});
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
