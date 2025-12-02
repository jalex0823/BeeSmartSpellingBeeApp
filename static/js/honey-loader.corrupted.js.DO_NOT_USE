// Honey Loader – cleaned canonical implementation (no duplicated blocks)// Dark Honeycomb Loader – canonical implementation (weighted gated tasks + optional diagnostics + matrix stop)

(function(){(function(){

  function initHoneyLoader(){  function initHoneyLoader() {

    const overlay = document.getElementById('appHoneyLoader');    const overlay = document.getElementById('appHoneyLoader');

    if(!overlay){ console.error('🍯 Honey loader overlay not found!'); return; }    if (!overlay) {

    console.log('🍯 Honey loader initializing...');      console.error('🍯 Honey loader overlay not found!');

      return;

    const percentEl = document.getElementById('loaderPercentText');    }

    const taskEl    = document.getElementById('loaderProcessName');

    const detailEl  = document.getElementById('loaderStatusDetail');    console.log('🍯 Honey loader initializing...');

    const ringEl    = document.querySelector('.progress-ring');

    const ariaEl    = document.getElementById('loaderAriaStatus');    // Elements

    const skipBtn   = document.getElementById('skipLoaderBtn');    const percentEl = document.getElementById('loaderPercentText');

    const taskEl = document.getElementById('loaderProcessName');

    const diagEnabled = (    const detailEl = document.getElementById('loaderStatusDetail');

      overlay.dataset.diagnostics === '1' ||    const ringEl = document.querySelector('.progress-ring');

      /[?&]loaderDiag=1/.test(location.search) ||    const ariaEl = document.getElementById('loaderAriaStatus');

      localStorage.getItem('honeyLoaderDiagnostics') === '1'    const skipBtn = document.getElementById('skipLoaderBtn');

    );

    // Diagnostics enable switches

    const emergencyBypass = false; // run real tasks    const diagEnabled = (

      overlay.dataset.diagnostics === '1' ||

    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;      /[?&]loaderDiag=1/.test(location.search) ||

    if(prefersReduced) overlay.classList.add('reduced-motion');      localStorage.getItem('honeyLoaderDiagnostics') === '1'

    );

    // ---------------- Matrix Rain ----------------

    function initMatrixRain(){    // IMPORTANT: run real tasks

      try {    const emergencyBypass = false; // was true

        let canvas = document.getElementById('matrixCanvas');

        if(!canvas){    // Reduced motion support

          canvas = document.createElement('canvas');    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

          canvas.id = 'matrixCanvas';    if (prefersReduced) overlay.classList.add('reduced-motion');

          canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:.6';

          overlay.insertBefore(canvas, overlay.firstChild);    // Matrix Rain Animation Setup - non-blocking and guarded

        }    function initMatrixRain(){

        const ctx = canvas.getContext('2d',{alpha:true});      try {

        const fontSize = 14;        let canvas = document.getElementById('matrixCanvas');

        function resize(){        if (!canvas) {

          canvas.width = window.innerWidth;          canvas = document.createElement('canvas');

          canvas.height = window.innerHeight;          canvas.id = 'matrixCanvas';

        }          canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:0.6';

        resize();          overlay.insertBefore(canvas, overlay.firstChild);

        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';        }

        let columns = Math.floor(canvas.width / fontSize);

        let drops = new Array(columns).fill(0).map(()=>Math.floor(Math.random()*canvas.height/fontSize));        const ctx = canvas.getContext('2d', { alpha: true });

        function draw(){        canvas.width = window.innerWidth;

          ctx.fillStyle = 'rgba(0,0,0,0.05)';        canvas.height = window.innerHeight;

          ctx.fillRect(0,0,canvas.width,canvas.height);

          ctx.fillStyle = '#FFD540';        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';

          ctx.font = fontSize+'px monospace';        const fontSize = 14;

          for(let i=0;i<drops.length;i++){        const columns = Math.floor(canvas.width / fontSize);

            const ch = chars[Math.floor(Math.random()*chars.length)];        const drops = [];

            ctx.fillText(ch, i*fontSize, drops[i]*fontSize);        for (let i = 0; i < columns; i++) {

            if(drops[i]*fontSize > canvas.height && Math.random()>0.975) drops[i]=0;          drops[i] = Math.floor(Math.random() * canvas.height / fontSize);

            drops[i]++;        }

          }

        }        function drawMatrix(){

        const interval = setInterval(draw,33);          ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';

        document.addEventListener('honeyLoaderFinished',()=>{          ctx.fillRect(0, 0, canvas.width, canvas.height);

          clearInterval(interval);          ctx.fillStyle = '#FFD540';

          canvas.style.opacity='0';          ctx.font = fontSize + 'px monospace';

          setTimeout(()=>{ if(canvas.parentNode) canvas.remove(); },500);          for (let i = 0; i < drops.length; i++) {

        },{once:true});            const char = chars[Math.floor(Math.random() * chars.length)];

        let rTO; window.addEventListener('resize',()=>{ clearTimeout(rTO); rTO=setTimeout(()=>{ resize(); columns=Math.floor(canvas.width/fontSize); drops=new Array(columns).fill(0).map(()=>Math.floor(Math.random()*canvas.height/fontSize)); },120); });            const x = i * fontSize;

      } catch(e){ console.error('🍯 Matrix animation failed:', e); }            const y = drops[i] * fontSize;

    }            ctx.fillText(char, x, y);

    setTimeout(initMatrixRain,0);            if (y > canvas.height && Math.random() > 0.975) drops[i] = 0;

            drops[i]++;

    // ---------------- Tasks ----------------          }

    const tasks = [        }

      { name:'System Health', weight:20, detail:'Checking server status…', fn:async()=>{

          try { const r = await Promise.race([ fetch('/health',{cache:'no-store'}), new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout')),1000)) ]); await new Promise(r=>setTimeout(r,600)); return {status:r.ok?'ok':'degraded'}; } catch { await new Promise(r=>setTimeout(r,600)); return {status:'degraded'}; }        const matrixInterval = setInterval(drawMatrix, 33);

        } },

      { name:'Quiz Content', weight:20, detail:'Loading word system…', fn:async()=>{        document.addEventListener('honeyLoaderFinished', () => {

          try { const r = await fetch('/api/wordbank',{cache:'no-store'}); await new Promise(r=>setTimeout(r,600)); return {loaded:r.ok}; } catch { await new Promise(r=>setTimeout(r,600)); return {loaded:false}; }          clearInterval(matrixInterval);

        } },          if (canvas && canvas.parentNode) {

      { name:'Avatar System', weight:30, detail:'Preparing avatars…', fn:async()=>{            canvas.style.opacity = '0';

          const base='/static/assets/avatars/glb_files/AvatarThumbnails';            setTimeout(() => canvas.remove(), 500);

          const list=['SuperBee!.png','QueenBee!.png','JRockBee!.png','BeeKnight!.png'];          }

          await Promise.all(list.map(f=>new Promise(res=>{ const img=new Image(); img.onload=()=>res(true); img.onerror=()=>res(false); img.src=`${base}/${f}`; })));         }, { once: true });

          try { const head = await fetch('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj',{method:'HEAD',cache:'no-store'}); if(!head.ok) console.warn('Mascot missing, fallback'); } catch(e){ console.warn('Mascot check failed:', e); }

          return {ready:true};        let resizeTimeout;

        } },        window.addEventListener('resize', () => {

      { name:'Interface Ready', weight:20, detail:'Initializing interface…', fn:async()=>{ await new Promise(r=>setTimeout(r,500)); return {ready:true}; } },          clearTimeout(resizeTimeout);

      { name:'System Ready', weight:10, detail:'Starting BeeSmart…', fn:async()=>{ await new Promise(r=>setTimeout(r,300)); document.dispatchEvent(new CustomEvent('systemChecks:done')); return {ready:true}; } }          resizeTimeout = setTimeout(() => {

    ];            canvas.width = window.innerWidth;

    const totalWeight = tasks.reduce((a,t)=>a+t.weight,0)||100;            canvas.height = window.innerHeight;

            const newLen = Math.floor(canvas.width / fontSize);

    // ---------------- State & UI helpers ----------------            if (newLen !== drops.length) {

    let finished=false, idx=0, progress=0; const timings=[]; const startTs=performance.now();              drops.length = newLen;

    function setProgress(p,label){ p=Math.max(0,Math.min(100,p)); if(percentEl) percentEl.textContent=p.toFixed(0)+'%'; if(taskEl) taskEl.textContent=label||''; if(ringEl) ringEl.style.setProperty('--p',p+'%'); if(ariaEl && (!setProgress._last || Math.abs(p-setProgress._last)>=5)){ ariaEl.textContent=`Loading: ${label||''} (${p.toFixed(0)}%)`; setProgress._last=p; } }              for (let i = 0; i < drops.length; i++) {

    function setDetail(d){ if(detailEl) detailEl.textContent=d||''; }                if (drops[i] === undefined) drops[i] = Math.floor(Math.random() * canvas.height / fontSize);

              }

    // ---------------- Finish ----------------            }

    function finish(){ if(finished) return; finished=true; setProgress(100,'Ready'); setDetail('Complete!'); console.log('🍯 UNLOCKING PAGE NOW'); document.body.style.pointerEvents='auto'; document.body.style.overflow='auto'; document.body.style.userSelect='auto'; try{ document.dispatchEvent(new Event('honeyLoaderFinished')); }catch(e){ console.error('Dispatch failed:', e);} if(overlay){ try{ overlay.style.transition='opacity .3s ease'; overlay.style.opacity='0'; overlay.style.pointerEvents='none'; setTimeout(()=>{ try{ overlay.style.display='none'; overlay.style.zIndex='-1'; if(overlay.remove) overlay.remove(); console.log('🍯 Loader removed'); }catch(rem){ console.error('Removal failed:', rem); overlay.style.display='none'; } },300); }catch(e){ console.error('Hide failed:', e); overlay.style.display='none'; } } }          }, 100);

        });

    setTimeout(()=>{ if(!finished){ console.warn('🍯 SAFETY TIMEOUT forcing finish'); finish(); } },3000);      } catch (e) {

    setTimeout(()=>{ if(!finished){ console.error('🍯 EMERGENCY UNLOCK forcing finish'); finish(); } },10000);        console.error('🍯 Matrix animation failed, continuing without it:', e);

    if(skipBtn) skipBtn.addEventListener('click',()=>finish());      }

    }

    // ---------------- Diagnostics ----------------

    let diagEl; function initDiagnostics(){ if(!diagEnabled) return; diagEl=document.createElement('div'); diagEl.id='honeyLoaderDiagnostics'; diagEl.style.cssText='position:fixed;top:8px;right:8px;z-index:99999;font:12px monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:280px;box-shadow:0 0 6px #000;'; diagEl.innerHTML='<strong>Loader Diagnostics</strong><div style="margin-top:4px" id="honeyLoaderDiagRows"></div><div id="honeyLoaderDiagNow" style="margin-top:2px;color:#ccc;font-size:11px">Now: 0%</div><div style="margin-top:6px" id="honeyLoaderDiagSparkline"></div><div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>'; document.body.appendChild(diagEl);}     // Start matrix animation immediately (before tasks) - non-blocking

    function updateDiag(){ if(!diagEnabled||!diagEl) return; const rowsEl=diagEl.querySelector('#honeyLoaderDiagRows'); const footer=diagEl.querySelector('#honeyLoaderDiagFooter'); const spark=diagEl.querySelector('#honeyLoaderDiagSparkline'); rowsEl.innerHTML=timings.map(t=>`<div>${t.name}</div><div style=\"color:#aaa;margin-left:6px\">${t.duration.toFixed(0)} ms</div>`).join(''); if(spark){ if(!timings.length){ spark.innerHTML='<div style="opacity:.6">(waiting for data…)</div>'; } else { const max=Math.max(...timings.map(t=>t.duration),1); const w=240,h=34,p=5; const pts=timings.map((t,i)=>{ const x=p+(i/((timings.length-1)||1))*(w-p*2); const y=h-p-(t.duration/max)*(h-p*2); return `${x},${y}`; }); const last=pts[pts.length-1].split(','); spark.innerHTML=`<svg viewBox='0 0 ${w} ${h}' width='${w}' height='${h}' preserveAspectRatio='none'><polyline points='${pts.join(' ')}' fill='none' stroke='#f8d25c' stroke-width='2' stroke-linejoin='round' /><circle cx='${last[0]}' cy='${last[1]}' r='3' fill='#f0c246' stroke='#332600' stroke-width='1' /></svg>`; } } footer.textContent=`Total: ${(performance.now()-startTs).toFixed(0)} ms | ${timings.reduce((a,t)=>a+t.duration,0).toFixed(0)} ms task time`; }    setTimeout(() => {

    initDiagnostics();      try { initMatrixRain(); } catch(e) { console.error('🍯 Matrix init failed:', e); }

    }, 0);

    // ---------------- Execution ----------------

    function runNext(){ if(finished) return; if(idx>=tasks.length){ console.log('🍯 All tasks complete'); finish(); return; } const t=tasks[idx]; const weightPct=(t.weight/totalWeight)*100; setProgress(progress,t.name); setDetail(t.detail); console.log(`🍯 Running task ${idx+1}/${tasks.length}: ${t.name}`); const start=performance.now(); let p; try{ p=t.fn(); }catch(e){ console.error('Task error:', e); p=Promise.resolve(); } Promise.resolve(p).catch(()=>({})).finally(()=>{ const dur=performance.now()-start; timings.push({name:t.name,duration:dur}); updateDiag(); progress=Math.min(100,progress+weightPct); setProgress(progress,t.name); idx++; runNext(); }); }    // System checks with realistic timing

    console.log('🍯 Starting system checks shortly');    const tasks = [

    setTimeout(()=>{ if(!emergencyBypass){ console.log('🍯 Beginning system checks now'); runNext(); } else { console.warn('🍯 Emergency bypass active – skipping tasks'); finish(); } },100);      {

  }        name: 'System Health',

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', initHoneyLoader); else initHoneyLoader();        weight: 20,

})();        detail: 'Checking server status…',

        expected: 800,
        fn: async () => {
          try {
            const response = await Promise.race([
              fetch('/health', { cache: 'no-store' }),
              new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000))
            ]);
            await new Promise(r => setTimeout(r, 600));
            return response.ok ? { status: 'ok' } : { status: 'degraded' };
          } catch {
            await new Promise(r => setTimeout(r, 600));
            return { status: 'degraded' };
          }
        }
      },
      {
        name: 'Quiz Content',
        weight: 20,
        detail: 'Loading word system…',
        expected: 800,
        fn: async () => {
          try {
            const response = await fetch('/api/wordbank', { cache: 'no-store' });
            await new Promise(r => setTimeout(r, 600));
            return response.ok ? { loaded: true } : { loaded: false };
          } catch {
            await new Promise(r => setTimeout(r, 600));
            return { loaded: false };
          }
        }
      },
      {
        name: 'Avatar System',
        weight: 30,
        detail: 'Preparing avatars…',
        expected: 1000,
        fn: async () => {
          const base = '/static/assets/avatars/glb_files/AvatarThumbnails';
          const carouselAvatars = ['SuperBee!.png','QueenBee!.png','JRockBee!.png','BeeKnight!.png'];
          console.log('🍯 Preloading carousel avatars for home page');
          const carouselPromises = carouselAvatars.map(file => new Promise(resolve => {
            const img = new Image();
            img.onload = () => { console.log(`✅ Loaded carousel: ${file}`); resolve(true); };
            img.onerror = () => { console.warn(`⚠️ Failed carousel: ${file}`); resolve(false); };
            img.src = `${base}/${file}`;
          }));
          await Promise.all(carouselPromises);
          try {
            const mascotCheck = await fetch('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', { method: 'HEAD', cache: 'no-store' });
            if (!mascotCheck.ok) console.warn('Mascot avatar missing, using fallback');
            return { ready: true, carouselLoaded: true };
          } catch (e) {
            console.warn('Mascot check failed:', e);
            return { ready: false, carouselLoaded: true };
          }
        }
      },
      {
        name: 'Interface Ready',
        weight: 20,
        detail: 'Initializing interface…',
        expected: 600,
        fn: async () => {
          await new Promise(r => setTimeout(r, 500));
          return { ready: true };
        }
      },
      {
        name: 'System Ready',
        weight: 10,
        detail: 'Starting BeeSmart…',
        expected: 400,
        fn: async () => {
          await new Promise(r => setTimeout(r, 300));
          document.dispatchEvent(new CustomEvent('systemChecks:done'));
          return { ready: true };
        }
      }
    ];
    const totalWeight = tasks.reduce((a, t) => a + t.weight, 0) || 100;

    // State
    const SAFETY_TIMEOUT_MS = 3000;
    let finished = false;
    let currentIndex = 0;
    let accumulated = 0;
    const startTs = performance.now();
    const timings = [];

    function setProgress(pct, label){
      pct = Math.max(0, Math.min(100, pct));
      if (percentEl) percentEl.textContent = pct.toFixed(0) + '%';
      if (taskEl) taskEl.textContent = label || '';
      if (ringEl) ringEl.style.setProperty('--p', pct + '%');
      if (ariaEl && (!setProgress._last || Math.abs(pct - setProgress._last) >= 5)) {
        ariaEl.textContent = `Loading: ${label || ''} (${pct.toFixed(0)}%)`;
        setProgress._last = pct;
      }
    }
    function setDetail(txt){ if (detailEl) detailEl.textContent = txt || ''; }

    function finish(){
      if (finished) return;
      finished = true;
      setProgress(100, 'Ready');
      setDetail('Complete!');

      console.log('🍯 UNLOCKING PAGE NOW');
      document.body.style.pointerEvents = 'auto';
      document.body.style.overflow = 'auto';
      document.body.style.userSelect = 'auto';

      try {
        document.dispatchEvent(new Event('honeyLoaderFinished'));
        console.log('🍯 Honey loader finished, dispatched event');
      } catch (e) {
        console.error('Error dispatching honeyLoaderFinished:', e);
      }

      if (overlay) {
        try {
          overlay.style.transition = 'opacity 0.3s ease';
          overlay.style.opacity = '0';
          overlay.style.pointerEvents = 'none';
          setTimeout(() => {
            try {
              overlay.style.display = 'none';
              overlay.style.zIndex = '-1';
              if (overlay.remove) overlay.remove();
              console.log('🍯 Loader removed from DOM');
            } catch (remErr) {
              console.error('🍯 Overlay removal failed:', remErr);
              overlay.style.display = 'none';
            }
          }, 300);
        } catch (e) {
          console.error('🍯 Overlay hide error, forcing unlock:', e);
          overlay.style.display = 'none';
        }
      }
    }

    // Safety timeout – force finish if loader hangs
    setTimeout(() => {
      if (!finished) {
        console.warn('🍯 SAFETY TIMEOUT: Forcing loader to finish');
        finish();
      }
    }, SAFETY_TIMEOUT_MS);

    // Emergency unlock after 10s no matter what
    setTimeout(() => {
      if (!finished) {
        console.error('🍯 EMERGENCY UNLOCK: Page frozen, forcing unlock');
        finish();
      }
    }, 10000);

    if (skipBtn) {
      skipBtn.addEventListener('click', () => finish());
    }

    // Diagnostics overlay construction
    let diagEl;
    function initDiagnostics(){
      if (!diagEnabled) return;
      diagEl = document.createElement('div');
      diagEl.id = 'honeyLoaderDiagnostics';
      diagEl.style.cssText = 'position:fixed;top:8px;right:8px;z-index:99999;font:12px/1.3 monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:280px;box-shadow:0 0 6px #000;';
      diagEl.innerHTML = '<strong>Loader Diagnostics</strong>'+
        '<div style="margin-top:4px" id="honeyLoaderDiagRows"></div>'+
        '<div id="honeyLoaderDiagNow" style="margin-top:2px;color:#ccc;font-size:11px">Now: 0%</div>'+
        '<div style="margin-top:6px" id="honeyLoaderDiagSparkline"></div>'+
        '<div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>';
      document.body.appendChild(diagEl);
    }

    function updateDiag(){
      if (!diagEnabled || !diagEl) return;
      const rowsEl = diagEl.querySelector('#honeyLoaderDiagRows');
      const footer = diagEl.querySelector('#honeyLoaderDiagFooter');
      const spark = diagEl.querySelector('#honeyLoaderDiagSparkline');
      rowsEl.innerHTML = timings.map(t => {
        const dur = (t.duration).toFixed(0);
        return `<div>${t.name}</div><div style="color:#aaa;margin-left:6px">${dur} ms</div>`;
      }).join('');
      if (spark){
        if (!timings.length){
          spark.innerHTML = '<div style="opacity:.6">(waiting for data…)</div>';
        } else {
          const max = Math.max(...timings.map(t=>t.duration),1);
          const w = 240, h = 34, pad = 5;
          const pts = timings.map((t,i)=>{
            const x = pad + (i/((timings.length-1)||1))*(w-pad*2);
            const y = h - pad - (t.duration/max)*(h-pad*2);
            return `${x},${y}`;
          });
          const last = pts[pts.length-1].split(',');
          const svg = `<svg viewBox='0 0 ${w} ${h}' width='${w}' height='${h}' preserveAspectRatio='none'>`+
            `<polyline points='${pts.join(' ')}' fill='none' stroke='#f8d25c' stroke-width='2' stroke-linejoin='round' />`+
            `<circle cx='${last[0]}' cy='${last[1]}' r='3' fill='#f0c246' stroke='#332600' stroke-width='1' />`+
            `</svg>`;
          spark.innerHTML = svg;
        }
      }
      const total = (performance.now() - startTs).toFixed(0);
      footer.textContent = `Total: ${total} ms | ${(timings.reduce((a,t)=>a+t.duration,0)).toFixed(0)} ms task time`;
    }

    initDiagnostics();

    // Simplified sequential execution
    function runNext(){
      if (finished) return;
      if (currentIndex >= tasks.length){
        console.log('🍯 All tasks complete, calling finish()');
        finish();
        return;
      }
      const t = tasks[currentIndex];
      const weightPct = (t.weight / totalWeight) * 100;
      setProgress(accumulated, t.name);
      setDetail(t.detail);
      console.log(`🍯 Running task ${currentIndex + 1}/${tasks.length}: ${t.name}`);

      const start = performance.now();
      let p;
      try { p = t.fn(); } catch(e){
        console.error(`Task ${t.name} error:`, e);
        p = Promise.resolve();
      }

      Promise.resolve(p)
        .catch(() => ({}))
        .finally(() => {
          const dur = performance.now() - start;
          timings.push({ name: t.name, duration: dur });
          updateDiag();
          accumulated = Math.min(100, accumulated + weightPct);
          setProgress(accumulated, t.name);
          currentIndex++;
          runNext();
        });
    }

    console.log('🍯 Delaying system checks to let Matrix animation start');
    setTimeout(() => {
      console.log('🍯 Beginning system checks now');
      runNext();
    }, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHoneyLoader);
  } else {
    initHoneyLoader();
  }
})();
// Dark Honeycomb Loader – canonical implementation (weighted gated tasks + optional diagnostics + matrix stop)// Dark Honeycomb Loader – canonical implementation (weighted gated tasks + optional diagnostics + matrix stop)

(function(){(function(){

  // Wait for DOM to be ready before initializing loader  // Wait for DOM to be ready before initializing loader

  function initHoneyLoader() {  function initHoneyLoader() {

    const overlay = document.getElementById('appHoneyLoader');    const overlay = document.getElementById('appHoneyLoader');

    if(!overlay){    if(!overlay){ 

      console.error('🍯 Honey loader overlay not found!');      console.error('🍯 Honey loader overlay not found!');

      return;      return; 

    }    }



    console.log('🍯 Honey loader initializing...');    console.log('🍯 Honey loader initializing...');



    // Elements  // Elements

    const percentEl = document.getElementById('loaderPercentText');  const percentEl = document.getElementById('loaderPercentText');

    const taskEl = document.getElementById('loaderProcessName');  const taskEl = document.getElementById('loaderProcessName');

    const detailEl = document.getElementById('loaderStatusDetail');  const detailEl = document.getElementById('loaderStatusDetail');

    const ringEl = document.querySelector('.progress-ring');  const ringEl = document.querySelector('.progress-ring');

    const ariaEl = document.getElementById('loaderAriaStatus');  const ariaEl = document.getElementById('loaderAriaStatus');

    const skipBtn = document.getElementById('skipLoaderBtn');  const skipBtn = document.getElementById('skipLoaderBtn');



    // Diagnostics enable switches  // Diagnostics enable switches (any truthy path turns it on)

    const diagEnabled = (  const diagEnabled = (

      overlay.dataset.diagnostics === '1' ||    overlay.dataset.diagnostics === '1' ||

      /[?&]loaderDiag=1/.test(location.search) ||    /[?&]loaderDiag=1/.test(location.search) ||

      localStorage.getItem('honeyLoaderDiagnostics') === '1'    localStorage.getItem('honeyLoaderDiagnostics') === '1'

    );  );

  

    // IMPORTANT: we're turning this OFF so the real tasks run  // EMERGENCY BYPASS: Skip all async tasks and finish immediately

    const emergencyBypass = false; // was true  const emergencyBypass = true; // Set to false once we identify the hanging task



    // Reduced motion support  // Reduced motion support

    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced) { overlay.classList.add('reduced-motion'); }  if(prefersReduced){ overlay.classList.add('reduced-motion'); }



    // Matrix Rain Animation Setup - optimized for instant start (wrapped in try-catch to prevent blocking)  // Matrix Rain Animation Setup - optimized for instant start (wrapped in try-catch to prevent blocking)

    function initMatrixRain(){  function initMatrixRain(){

      try {    try {

        let canvas = document.getElementById('matrixCanvas');    let canvas = document.getElementById('matrixCanvas');

        if(!canvas){    if(!canvas){

          canvas = document.createElement('canvas');      canvas = document.createElement('canvas');

          canvas.id = 'matrixCanvas';      canvas.id = 'matrixCanvas';

          canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:0.6';      canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:1;background:transparent;pointer-events:none;opacity:0.6';

          overlay.insertBefore(canvas, overlay.firstChild);      overlay.insertBefore(canvas, overlay.firstChild);

        }    }

    

        const ctx = canvas.getContext('2d', { alpha: true });    const ctx = canvas.getContext('2d', { alpha: true });

        canvas.width = window.innerWidth;    canvas.width = window.innerWidth;

        canvas.height = window.innerHeight;    canvas.height = window.innerHeight;

    

        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';

        const fontSize = 14;    const fontSize = 14;

        const columns = Math.floor(canvas.width / fontSize);    const columns = Math.floor(canvas.width / fontSize);

        const drops = [];    const drops = [];

    

        for (let i = 0; i < columns; i++) {    // Initialize drops with random starting positions for instant effect

          drops[i] = Math.floor(Math.random() * canvas.height / fontSize);    for(let i = 0; i < columns; i++){

        }      drops[i] = Math.floor(Math.random() * canvas.height / fontSize);

    }

        function drawMatrix(){    

          ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';    function drawMatrix(){

          ctx.fillRect(0, 0, canvas.width, canvas.height);      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';

      ctx.fillRect(0, 0, canvas.width, canvas.height);

          ctx.fillStyle = '#FFD540'; // BeeSmart yellow      

          ctx.font = fontSize + 'px monospace';      ctx.fillStyle = '#FFD540'; // BeeSmart yellow

      ctx.font = fontSize + 'px monospace';

          for (let i = 0; i < drops.length; i++) {      

            const char = chars[Math.floor(Math.random() * chars.length)];      for(let i = 0; i < drops.length; i++){

            const x = i * fontSize;        const char = chars[Math.floor(Math.random() * chars.length)];

            const y = drops[i] * fontSize;        const x = i * fontSize;

        const y = drops[i] * fontSize;

            ctx.fillText(char, x, y);        

        ctx.fillText(char, x, y);

            if (y > canvas.height && Math.random() > 0.975) {        

              drops[i] = 0;        if(y > canvas.height && Math.random() > 0.975){

            }          drops[i] = 0;

            drops[i]++;        }

          }        drops[i]++;

        }      }

    }

        const matrixInterval = setInterval(drawMatrix, 33);    

    // Start animation immediately

        document.addEventListener('honeyLoaderFinished', () => {    const matrixInterval = setInterval(drawMatrix, 33);

          clearInterval(matrixInterval);    

          if (canvas && canvas.parentNode) {    // Cleanup on loader finish

            canvas.style.opacity = '0';    document.addEventListener('honeyLoaderFinished', () => {

            setTimeout(() => canvas.remove(), 500);      clearInterval(matrixInterval);

          }      if(canvas && canvas.parentNode){

        }, { once: true });        canvas.style.opacity = '0';

        setTimeout(() => canvas.remove(), 500);

        let resizeTimeout;      }

        window.addEventListener('resize', () => {    }, {once: true});

          clearTimeout(resizeTimeout);    

          resizeTimeout = setTimeout(() => {    // Handle resize efficiently

            canvas.width = window.innerWidth;    let resizeTimeout;

            canvas.height = window.innerHeight;    window.addEventListener('resize', () => {

            drops.length = Math.floor(canvas.width / fontSize);      clearTimeout(resizeTimeout);

            for (let i = 0; i < drops.length; i++) {      resizeTimeout = setTimeout(() => {

              if (drops[i] === undefined) drops[i] = Math.floor(Math.random() * canvas.height / fontSize);        canvas.width = window.innerWidth;

            }        canvas.height = window.innerHeight;

          }, 100);        drops.length = Math.floor(canvas.width / fontSize);

        });        for(let i = 0; i < drops.length; i++){

      } catch(e) {          if(drops[i] === undefined) drops[i] = Math.floor(Math.random() * canvas.height / fontSize);

        console.error('🍯 Matrix animation failed, continuing without it:', e);        }

      }      }, 100);

    }    });

    } catch(e) {

    // Start matrix animation immediately (before tasks) - non-blocking      console.error('🍯 Matrix animation failed, continuing without it:', e);

    setTimeout(() => {    }

      try { initMatrixRain(); } catch(e) { console.error('🍯 Matrix init failed:', e); }  }

    }, 0);  

  // Start matrix animation immediately (before tasks) - non-blocking

    // System checks with realistic timing - minimum 65% before page loads  setTimeout(() => {

    const tasks = [    try {

      // Quick startup (0-20%)      initMatrixRain();

      {    } catch(e) {

        name: 'System Health',      console.error('🍯 Matrix init failed:', e);

        weight: 20,    }

        detail: 'Checking server status…',  }, 0);

        expected: 800,

        fn: async () => {    // System checks with realistic timing - minimum 65% before page loads

          try {  const tasks = [

            const response = await Promise.race([    // Quick startup (0-20%)

              fetch('/health', {cache: 'no-store'}),    { 

              new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000))      name: 'System Health', 

            ]);      weight: 20, 

            await new Promise(resolve => setTimeout(resolve, 600));      detail: 'Checking server status…',

            return response.ok ? {status: 'ok'} : {status: 'degraded'};      expected: 800,

          } catch(e) {      fn: async () => {

            await new Promise(resolve => setTimeout(resolve, 600));        // Real health check with timeout

            return {status: 'degraded'};        try {

          }          const response = await Promise.race([

        }            fetch('/health', {cache: 'no-store'}),

      },            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000))

      // Word system (20-40%)          ]);

      {          await new Promise(resolve => setTimeout(resolve, 600)); // Ensure visible time

        name: 'Quiz Content',          return response.ok ? {status: 'ok'} : {status: 'degraded'};

        weight: 20,        } catch(e) {

        detail: 'Loading word system…',          await new Promise(resolve => setTimeout(resolve, 600));

        expected: 800,          return {status: 'degraded'}; // Continue anyway

        fn: async () => {        }

          try {      }

            const response = await fetch('/api/wordbank', {cache: 'no-store'});    },

            await new Promise(resolve => setTimeout(resolve, 600));    // Word system (20-40%)

            return response.ok ? {loaded: true} : {loaded: false};    { 

          } catch(e) {      name: 'Quiz Content', 

            await new Promise(resolve => setTimeout(resolve, 600));      weight: 20, 

            return {loaded: false};      detail: 'Loading word system…',

          }      expected: 800,

        }      fn: async () => {

      },        // Check wordbank

      // Avatar system (40-70%) - CRITICAL CHECKPOINT        try {

      {          const response = await fetch('/api/wordbank', {cache: 'no-store'});

        name: 'Avatar System',          await new Promise(resolve => setTimeout(resolve, 600));

        weight: 30,          return response.ok ? {loaded: true} : {loaded: false};

        detail: 'Preparing avatars…',        } catch(e) {

        expected: 1000,          await new Promise(resolve => setTimeout(resolve, 600));

        fn: async () => {          return {loaded: false};

          const base = '/static/assets/avatars/glb_files/AvatarThumbnails';        }

          const carouselAvatars = [      }

            'SuperBee!.png',    },

            'QueenBee!.png',    // Avatar system (40-70%) - CRITICAL CHECKPOINT

            'JRockBee!.png',    { 

            'BeeKnight!.png'      name: 'Avatar System', 

          ];      weight: 30, 

      detail: 'Preparing avatars…',

          console.log('🍯 Preloading carousel avatars for home page');      expected: 1000,

          const carouselPromises = carouselAvatars.map(file => {      fn: async () => {

            return new Promise(resolve => {        // Preload guest carousel avatars (priority picks for non-registered users)

              const img = new Image();        const base = '/static/assets/avatars/glb_files/AvatarThumbnails';

              img.onload = () => {        const carouselAvatars = [

                console.log(`✅ Loaded carousel: ${file}`);          'SuperBee!.png',

                resolve(true);          'QueenBee!.png', 

              };          'JRockBee!.png',

              img.onerror = () => {          'BeeKnight!.png'

                console.warn(`⚠️ Failed carousel: ${file}`);        ];

                resolve(false);        

              };        console.log('🍯 Preloading carousel avatars for home page');

              img.src = `${base}/${file}`;        const carouselPromises = carouselAvatars.map(file => {

            });          return new Promise(resolve => {

          });            const img = new Image();

            img.onload = () => {

          await Promise.all(carouselPromises);              console.log(`✅ Loaded carousel: ${file}`);

              resolve(true);

          try {            };

            const mascotCheck = await fetch('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', {            img.onerror = () => {

              method: 'HEAD',              console.warn(`⚠️ Failed carousel: ${file}`);

              cache: 'no-store'              resolve(false);

            });            };

            if (!mascotCheck.ok) {            img.src = `${base}/${file}`;

              console.warn('Mascot avatar missing, using fallback');          });

            }        });

            return {ready: true, carouselLoaded: true};        

          } catch(e) {        // Load all carousel avatars in parallel

            console.warn('Mascot check failed:', e);        await Promise.all(carouselPromises);

            return {ready: false, carouselLoaded: true};        

          }        // Also check mascot avatar for registered users

        }        try {

      },          const mascotCheck = await fetch('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', {

      // UI preparation (70-90%)            method: 'HEAD',

      {            cache: 'no-store'

        name: 'Interface Ready',          });

        weight: 20,          if (!mascotCheck.ok) {

        detail: 'Initializing interface…',            console.warn('Mascot avatar missing, using fallback');

        expected: 600,          }

        fn: async () => {          return {ready: true, carouselLoaded: true};

          await new Promise(resolve => setTimeout(resolve, 500));        } catch(e) {

          return {ready: true};          console.warn('Mascot check failed:', e);

        }          return {ready: false, carouselLoaded: true};

      },        }

      // Final touches (90-100%)      }

      {    },

        name: 'System Ready',    // UI preparation (70-90%)

        weight: 10,    { 

        detail: 'Starting BeeSmart…',      name: 'Interface Ready', 

        expected: 400,      weight: 20, 

        fn: async () => {      detail: 'Initializing interface…',

          await new Promise(resolve => setTimeout(resolve, 300));      expected: 600,

          document.dispatchEvent(new CustomEvent('systemChecks:done'));      fn: async () => {

          return {ready: true};        await new Promise(resolve => setTimeout(resolve, 500));

        }        return {ready: true};

      }      }

    ];    },

    const totalWeight = tasks.reduce((a,t)=>a+t.weight,0) || 100;    // Final touches (90-100%)

    { 

    // State      name: 'System Ready', 

    const MIN_DISPLAY_MS = 0;      weight: 10, 

    const SAFETY_TIMEOUT_MS = 3000;      detail: 'Starting BeeSmart…',

    let finished = false;      expected: 400,

    let currentIndex = 0;      fn: async () => {

    let accumulated = 0;        await new Promise(resolve => setTimeout(resolve, 300));

    const startTs = performance.now();        document.dispatchEvent(new CustomEvent('systemChecks:done'));

    const timings = [];        return {ready: true};

      }

    function setProgress(pct,label){    }

      pct = Math.max(0, Math.min(100, pct));  ];

      if (percentEl) percentEl.textContent = pct.toFixed(0) + '%';  const totalWeight = tasks.reduce((a,t)=>a+t.weight,0) || 100;

      if (taskEl) taskEl.textContent = label || '';

      if (ringEl) ringEl.style.setProperty('--p', pct + '%');  // State

      if (ariaEl && (!setProgress._last || Math.abs(pct - setProgress._last) >= 5)) {  const MIN_DISPLAY_MS = 0; // No minimum - instant when ready

        ariaEl.textContent = `Loading: ${label || ''} (${pct.toFixed(0)}%)`;  const SAFETY_TIMEOUT_MS = 3000; // 3 second hard cap

        setProgress._last = pct;  let finished = false;

      }  let finishRequested = false;

    }  let currentIndex = 0;

    function setDetail(txt){ if (detailEl) detailEl.textContent = txt || ''; }  let accumulated = 0;

  const startTs = performance.now();

    function finish(){  const timings = [];

      if (finished) return;

      finished = true;  // Utility helpers - simplified

  function setProgress(pct,label){

      setProgress(100,'Ready');    pct = Math.max(0, Math.min(100, pct));

      setDetail('Complete!');    if(percentEl) percentEl.textContent = pct.toFixed(0) + '%';

    if(taskEl) taskEl.textContent = label || '';

      console.log('🍯 UNLOCKING PAGE NOW');    if(ringEl) ringEl.style.setProperty('--p', pct + '%');

      document.body.style.pointerEvents = 'auto';    if(ariaEl && (!setProgress._last || Math.abs(pct - setProgress._last) >= 5)){

      document.body.style.overflow = 'auto';      ariaEl.textContent = `Loading: ${label || ''} (${pct.toFixed(0)}%)`;

      document.body.style.userSelect = 'auto';      setProgress._last = pct;

    }

      // Dispatch event first  }

      try {  function setDetail(txt){ if(detailEl) detailEl.textContent = txt || ''; }

        document.dispatchEvent(new Event('honeyLoaderFinished'));

        console.log('🍯 Honey loader finished, dispatched event');  function finish(){

      } catch(e) {    if(finished) return;

        console.error('Error dispatching honeyLoaderFinished:', e);    finished = true;

      }    finishRequested = true;

    

      // Now hide overlay safely    setProgress(100,'Ready');

      if (overlay) {    setDetail('Complete!');

        try {    

          overlay.style.transition = 'opacity 0.3s ease';    // UNLOCK PAGE IMMEDIATELY - Don't wait for anything

          overlay.style.opacity = '0';    console.log('🍯 UNLOCKING PAGE NOW');

          overlay.style.pointerEvents = 'none';    document.body.style.pointerEvents = 'auto';

          // don't slam zIndex to -1 until after fade    document.body.style.overflow = 'auto';

          setTimeout(() => {    document.body.style.userSelect = 'auto';

            try {    

              overlay.style.display = 'none';    // Remove overlay from DOM flow immediately

              overlay.style.zIndex = '-1';    if(overlay) {

              if (overlay.remove) overlay.remove();      overlay.style.pointerEvents = 'none';

              console.log('🍯 Loader removed from DOM');      overlay.style.zIndex = '-1';

            } catch (remErr) {      console.log('🍯 Overlay disabled for interactions');

              console.error('🍯 Overlay removal failed:', remErr);    }

              overlay.style.display = 'none';    

            }    // Dispatch event for page initialization (non-blocking)

          }, 300);    try { 

        } catch(e) {      document.dispatchEvent(new Event('honeyLoaderFinished')); 

          console.error('🍯 Overlay hide error, forcing unlock:', e);      console.log('🍯 Honey loader finished, dispatched event');

          overlay.style.display = 'none';    } catch(e) {

        }      console.error('Error dispatching honeyLoaderFinished:', e);

      }    }

    }    

    // Hide loader overlay visually

    // Safety timeout – force finish if loader hangs    if(overlay) {

    setTimeout(() => {      overlay.style.transition = 'opacity 0.3s ease';

      if (!finished) {      overlay.style.opacity = '0';

        console.warn('🍯 SAFETY TIMEOUT: Forcing loader to finish');      setTimeout(() => { 

        finish();        overlay.style.display = 'none';

      }        overlay.remove(); // Completely remove from DOM

    }, SAFETY_TIMEOUT_MS);        console.log('🍯 Loader removed from DOM');

      }, 300);

    // Emergency unlock after 10s no matter what    }

    setTimeout(() => {  }

      if (!finished) {

        console.error('🍯 EMERGENCY UNLOCK: Page frozen, forcing unlock');  // Single safety timeout - force finish if loader hangs

        finish();  setTimeout(()=>{ 

      }    if(!finished) {

    }, 10000);      console.warn('🍯 SAFETY TIMEOUT: Forcing loader to finish');

      finish(); 

    if (skipBtn){    }

      skipBtn.addEventListener('click', () => {  }, SAFETY_TIMEOUT_MS);

        finish();  

      });  // Emergency page unlock after 10 seconds if EVERYTHING fails

    }  setTimeout(() => {

    if(overlay && overlay.style.display !== 'none') {

    // Diagnostics overlay construction      console.error('🍯 EMERGENCY UNLOCK: Page frozen, forcing unlock');

    let diagEl;      overlay.style.display = 'none';

    function initDiagnostics(){      document.body.style.pointerEvents = 'auto';

      if (!diagEnabled) return;      document.body.style.overflow = 'auto';

      diagEl = document.createElement('div');    }

      diagEl.id = 'honeyLoaderDiagnostics';  }, 10000);

      diagEl.style.cssText = 'position:fixed;top:8px;right:8px;z-index:99999;font:12px/1.3 monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:280px;box-shadow:0 0 6px #000;';

      diagEl.innerHTML = '<strong>Loader Diagnostics</strong><div style="margin-top:4px" id="honeyLoaderDiagRows"></div><div id="honeyLoaderDiagNow" style="margin-top:2px;color:#ccc;font-size:11px">Now: 0%</div><div style="margin-top:6px" id="honeyLoaderDiagSparkline"></div><div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>';  if(skipBtn){

      document.body.appendChild(diagEl);    skipBtn.addEventListener('click', ()=>{ showSkip(); finish(); });

    }  }

    function updateDiag(){  window.addEventListener('systemChecks:done', finish);

      if (!diagEnabled || !diagEl) return;

      const rowsEl = diagEl.querySelector('#honeyLoaderDiagRows');  // Diagnostics overlay construction

      const footer = diagEl.querySelector('#honeyLoaderDiagFooter');  let diagEl;

      const spark = diagEl.querySelector('#honeyLoaderDiagSparkline');  function initDiagnostics(){

      rowsEl.innerHTML = timings.map(t => {    if(!diagEnabled) return;

        const dur = (t.duration).toFixed(0);    diagEl = document.createElement('div');

        return `<div>${t.name}</div><div style="color:#aaa;margin-left:6px">${dur} ms</div>`;    diagEl.id = 'honeyLoaderDiagnostics';

      }).join('');    diagEl.style.cssText = 'position:fixed;top:8px;right:8px;z-index:99999;font:12px/1.3 monospace;background:rgba(20,18,10,.85);color:#f8d25c;padding:8px 10px;border:1px solid #f0c246;border-radius:6px;max-width:280px;box-shadow:0 0 6px #000;';

      if (spark){    diagEl.innerHTML = '<strong>Loader Diagnostics</strong><div style="margin-top:4px" id="honeyLoaderDiagRows"></div><div id="honeyLoaderDiagNow" style="margin-top:2px;color:#ccc;font-size:11px">Now: 0%</div><div style="margin-top:6px" id="honeyLoaderDiagSparkline"></div><div style="margin-top:4px;font-size:11px;opacity:.8" id="honeyLoaderDiagFooter"></div>';

        if (!timings.length){    document.body.appendChild(diagEl);

          spark.innerHTML = '<div style="opacity:.6">(waiting for data…)</div>';  }

        } else {  function updateDiag(){

          const max = Math.max(...timings.map(t=>t.duration),1);    if(!diagEnabled || !diagEl) return;

          const w = 240, h = 34, pad = 5;    const rowsEl = diagEl.querySelector('#honeyLoaderDiagRows');

          const pts = timings.map((t,i)=>{    const footer = diagEl.querySelector('#honeyLoaderDiagFooter');

            const x = pad + (i/(timings.length-1||1))*(w-pad*2);    const spark = diagEl.querySelector('#honeyLoaderDiagSparkline');

            const y = h - pad - (t.duration/max)*(h-pad*2);    rowsEl.innerHTML = timings.map(t => {

            return `${x},${y}`;      const dur = (t.duration).toFixed(0);

          });      return `<div>${t.name}</div><div style="color:#aaa;margin-left:6px">${dur} ms</div>`;

          const last = pts[pts.length-1].split(',');    }).join('');

          const svg = `<svg viewBox='0 0 ${w} ${h}' width='${w}' height='${h}' preserveAspectRatio='none'>`    if(spark){

            + `<polyline points='${pts.join(' ')}' fill='none' stroke='#f8d25c' stroke-width='2' stroke-linejoin='round' />`      if(!timings.length){

            + `<circle cx='${last[0]}' cy='${last[1]}' r='3' fill='#f0c246' stroke='#332600' stroke-width='1' />`        spark.innerHTML = '<div style="opacity:.6">(waiting for data…)</div>';

            + `</svg>`;      } else {

          spark.innerHTML = svg;        const max = Math.max(...timings.map(t=>t.duration),1);

        }        const w = 240, h = 34, pad = 5;

      }        const pts = timings.map((t,i)=>{

      const total = (performance.now() - startTs).toFixed(0);          const x = pad + (i/(timings.length-1||1))*(w-pad*2);

      footer.textContent = `Total: ${total} ms | ${(timings.reduce((a,t)=>a+t.duration,0)).toFixed(0)} ms task time`;          const y = h - pad - (t.duration/max)*(h-pad*2);

    }          return `${x},${y}`;

        });

    initDiagnostics();        const last = pts[pts.length-1].split(',');

        const svg = `<svg viewBox='0 0 ${w} ${h}' width='${w}' height='${h}' preserveAspectRatio='none'>`

    // Simplified execution          + `<polyline points='${pts.join(' ')}' fill='none' stroke='#f8d25c' stroke-width='2' stroke-linejoin='round' />`

    function runNext(){          + `<circle cx='${last[0]}' cy='${last[1]}' r='3' fill='#f0c246' stroke='#332600' stroke-width='1' />`

      if (finished) return;          + `</svg>`;

      if (currentIndex >= tasks.length){        spark.innerHTML = svg;

        console.log('🍯 All tasks complete, calling finish()');      }

        finish();    }

        return;    const total = (performance.now() - startTs).toFixed(0);

      }    footer.textContent = `Total: ${total} ms | ${(timings.reduce((a,t)=>a+t.duration,0)).toFixed(0)} ms task time`;

      const t = tasks[currentIndex];  }

      const weightPct = (t.weight / totalWeight) * 100;  function flushDiagnostics(){ updateDiag(); }

      setProgress(accumulated, t.name);

      setDetail(t.detail);  initDiagnostics();

      console.log(`🍯 Running task ${currentIndex + 1}/${tasks.length}: ${t.name}`);

  // START MATRIX ANIMATION IMMEDIATELY for instant visual feedback

      const start = performance.now();  console.log('🍯 Starting Matrix rain animation FIRST');

      let p;  initMatrixRain();

      try { p = t.fn(); } catch(e){

        console.error(`Task ${t.name} error:`, e);  // Simplified execution - no interpolation, instant progress

        p = Promise.resolve();  function runNext(){

      }    if(finished) return;

    if(currentIndex >= tasks.length){ 

      Promise.resolve(p)      console.log('🍯 All tasks complete, calling finish()');

        .catch(() => ({}))      finish(); 

        .finally(() => {      return; 

          const dur = performance.now() - start;    }

          timings.push({name: t.name, duration: dur});    const t = tasks[currentIndex];

          updateDiag();    const weightPct = (t.weight / totalWeight) * 100;

    setProgress(accumulated, t.name);

          accumulated = Math.min(100, accumulated + weightPct);    setDetail(t.detail);

          setProgress(accumulated, t.name);    console.log(`🍯 Running task ${currentIndex + 1}/${tasks.length}: ${t.name}`);

          currentIndex++;    

          runNext();    let p;

        });    try { p = t.fn(); } catch(e){ 

    }      console.error(`Task ${t.name} error:`, e);

      p = Promise.resolve(); 

    console.log('🍯 Delaying system checks to let Matrix animation start');    }

    

    // since emergencyBypass is now false, always run real tasks    Promise.resolve(p)

    setTimeout(() => {      .catch(() => ({}))

      console.log('🍯 Beginning system checks now');      .finally(()=>{

      runNext();        accumulated = Math.min(100, accumulated + weightPct);

    }, 100);        setProgress(accumulated, t.name);

  } // End initHoneyLoader        currentIndex++;

        runNext();

  // Start loader when DOM is ready      });

  if (document.readyState === 'loading') {  }

    document.addEventListener('DOMContentLoaded', initHoneyLoader);

  } else {  // Give Matrix 100ms to start rendering, THEN begin system checks

    initHoneyLoader();  console.log('🍯 Delaying system checks to let Matrix animation start');

  }  

})();  if (emergencyBypass) {

    console.warn('⚠️ EMERGENCY BYPASS ACTIVE - Skipping all async tasks');
    setTimeout(() => {
      console.log('🍯 Emergency bypass: Simulating quick load');
      setProgress(20, 'System Health');
      setTimeout(() => {
        setProgress(40, 'Quiz Content');
        setTimeout(() => {
          setProgress(70, 'Avatar System');
          setTimeout(() => {
            setProgress(90, 'Interface Ready');
            setTimeout(() => {
              setProgress(100, 'System Ready');
              setTimeout(() => {
                console.log('🍯 Emergency bypass: Finishing loader');
                finish();
              }, 100);
            }, 100);
          }, 100);
        }, 100);
      }, 100);
    }, 50); // Reduced from 500ms to 50ms for instant start
  } else {
    setTimeout(() => {
      console.log('🍯 Beginning system checks now');
      runNext();
    }, 100);
  }
  } // End initHoneyLoader
  
  // Start loader when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHoneyLoader);
  } else {
    // DOM already loaded
    initHoneyLoader();
  }
})();
