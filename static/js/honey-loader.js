// Honeycomb Loader Controller
(function(){
  const el = document.getElementById('appHoneyLoader');
  if(!el){ return; }
  const percentText = document.getElementById('loaderPercentText');
  const processName = document.getElementById('loaderProcessName');
  const detailText = document.getElementById('loaderStatusDetail');

  let progress = 0;
  let done = false;

  function setProgress(p, status){
    progress = Math.max(0, Math.min(100, p|0));
    if (percentText) percentText.textContent = progress + '%';
    if (status) { processName.textContent = status; }
  }
  function setDetail(msg){ if(detailText) detailText.textContent = msg; }
  function finish(){ done = true; setProgress(100, 'Ready'); setDetail(''); setTimeout(()=>{ el.classList.add('hidden'); }, 250); }

  // Expose a small API other scripts can call
  window.SystemChecks = window.SystemChecks || {};
  window.SystemChecks.setProgress = setProgress;
  window.SystemChecks.setDetail = setDetail;
  window.SystemChecks.finish = finish;

  // Default progression if no one drives it explicitly
  const timer = setInterval(()=>{
    if(done) { clearInterval(timer); return; }
    // Ease towards 90% until onload; then finish()
    if(progress < 90){ setProgress(progress + Math.max(1, Math.round((90-progress)/10))); }
  }, 200);

  // If the page fully loads, we finish shortly after
  window.addEventListener('load', ()=>{
    setDetail('Finalizing checks...');
    setTimeout(finish, 400);
  });

  // Optional: listen for custom complete event to close early
  window.addEventListener('systemChecks:done', finish);
})();
