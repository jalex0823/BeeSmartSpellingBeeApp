// Dark Honeycomb Loader – dynamic gated progress (clean)
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
  const allowMotion = overlay.dataset.allowMotion !== 'false';

  // Reduced motion
  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(prefersReduced){ overlay.classList.add('reduced-motion'); }

  // State
  let progress = 0;       // numeric percent
  let currentTask = 0;    // index in tasks
  let finished = false;   // completion flag
  let skipShown = false;  // skip visibility flag
  const startTs = Date.now();

  // Tasks (ordered)
  const tasks = [
    {
      name: 'Core', detail: 'Preparing interface…', fn: () => {
        ['/static/images/backgrounds/HoneyCombBg2.png','/static/BeeSmartCrestLogo1.png'].forEach(u=>{ const img=new Image(); img.src=u; });
        return Promise.resolve();
      }
    },
    { name: 'Health', detail: 'Checking system health…', fn: () => fetch('/health',{cache:'no-store'}).then(r=>r.json()).catch(()=>({error:true})) },
    { name: 'Wordbank', detail: 'Loading word lists…', fn: () => fetch('/api/wordbank',{cache:'no-store'}).then(r=>r.json()).catch(()=>({error:true})) },
    { name: 'Avatars', detail: 'Caching avatars…', fn: () => new Promise(res=>setTimeout(res,600)) },
    { name: 'Definitions', detail: 'Priming dictionary cache…', fn: () => new Promise(res=>setTimeout(res,500)) }
  ];
  const slice = Math.floor(100 / tasks.length); // integer slice size

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
    finished = true;
    setProgress(100,'Ready');
    setDetail('');
    try{ document.dispatchEvent(new Event('honeyLoaderFinished')); }catch{}
    setTimeout(()=>{ overlay.classList.add('hidden'); }, 350);
  }

  // Expose minimal API
  window.SystemChecks = Object.assign(window.SystemChecks||{}, { setProgress, setDetail, finish });

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

  // Perception nudge: if still at first slice after 2.5s, advance slightly
  setTimeout(()=>{
    if(finished) return;
    const current = parseInt((percentEl?.textContent||'').replace(/[^0-9]/g,''),10) || 0;
    const oneSlice = Math.floor(100 / tasks.length);
    if(current <= oneSlice && allowMotion && !prefersReduced){
      setProgress(Math.max(1, oneSlice - 1), tasks[1]? tasks[1].name + '…':'Loading…');
    }
  },2500);

  // Safety timeout
  setTimeout(()=>{ if(!finished) finish(); }, 8000);

  // Skip button
  if(skipBtn){ skipBtn.addEventListener('click', ()=> finish()); }

  // Start
  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', runNext); } else { runNext(); }

  // External early finish hook
  window.addEventListener('systemChecks:done', finish);
})();