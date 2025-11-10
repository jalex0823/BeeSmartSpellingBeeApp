// Dark Honeycomb Loader – dynamic gated progress
(function(){
  const el = document.getElementById('appHoneyLoader');
  if(!el){ return; }

  const percentText = document.getElementById('loaderPercentText');
  const processName = document.getElementById('loaderProcessName');
  const detailText   = document.getElementById('loaderStatusDetail');

  let progress = 0;       // integer percent
  let done = false;       // finished flag
  let currentTask = 0;    // index in tasks

  function render(){
    if (percentText) percentText.textContent = progress + '%';
  }
  function setProgress(p, label){
    progress = Math.max(0, Math.min(100, p|0));
    if(label){ processName.textContent = label; }
    render();
  }
  function setDetail(msg){ if(detailText) detailText.textContent = msg; }
  function finish(){
    if(done) return;
    done = true;
    setProgress(100, 'Ready');
    setDetail('');
    // Stop matrix animation
    try { document.dispatchEvent(new Event('honeyLoaderFinished')); } catch(e) {}
    // small delay for user to register 100%
    setTimeout(()=>{ el.classList.add('hidden'); }, 350);
  }

  // Public API for external scripts (optional extension)
  window.SystemChecks = Object.assign(window.SystemChecks || {}, {
    setProgress, setDetail, finish
  });

  // Sequential task list – each returns a promise
  const tasks = [
    {
      name: 'Core', detail: 'Preparing interface…', fn: () => Promise.resolve()
    },
    {
      name: 'Health', detail: 'Checking system health…', fn: () => fetch('/health',{cache:'no-store'})
        .then(r=>r.json()).catch(()=>({}))
    },
    {
      name: 'Wordbank', detail: 'Loading word lists…', fn: () => fetch('/api/wordbank',{cache:'no-store'})
        .then(r=>r.json()).catch(()=>({}))
    },
    {
      name: 'Avatars', detail: 'Caching avatars…', fn: () => new Promise(res=>setTimeout(res,400))
    }
  ];

  const slice = Math.floor(100 / tasks.length); // equal weight slices

  function runNext(){
    if(done) return;
    const task = tasks[currentTask];
    if(!task){ finish(); return; }
    setProgress(currentTask * slice, task.name + '…');
    setDetail(task.detail);
    Promise.resolve()
      .then(task.fn)
      .then(()=>{
        currentTask++;
        // Advance progress into next slice but cap at 99 until final finish
        const base = Math.min(99, currentTask * slice);
        setProgress(base, task.name + ' done');
        setDetail('');
        setTimeout(runNext, 75); // brief pause for readability
      })
      .catch(()=>{
        // Non‑fatal – mark slice complete and continue
        currentTask++;
        setProgress(Math.min(99, currentTask * slice), task.name + ' skipped');
        setDetail('');
        setTimeout(runNext, 50);
      });
  }

  // Safety timeout: never leave user stuck > 8s
  setTimeout(()=>{ if(!done) finish(); }, 8000);

  // Start tasks after DOM is ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', runNext);
  } else {
    runNext();
  }

  // Allow external scripts to fast‑finish early if they know readiness
  window.addEventListener('systemChecks:done', finish);
})();
