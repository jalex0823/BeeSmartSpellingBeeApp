// New Honeycomb Loader Controller
(function(){
  const el = document.getElementById('bee-honey-loader');
  if (!el) return;
  const fill = document.getElementById('loaderProgressFill');
  const text = document.getElementById('loaderProgressText');
  const center = el.querySelector('.loader-center');

  let progress = 0;
  let rafId = null;
  let running = true;

  function render(){
    if (fill) fill.style.width = progress + '%';
    if (text) text.textContent = Math.round(progress) + '%';
    if (center) center.setAttribute('data-progress', Math.round(progress) + '%');
  }

  function step(){
    if (!running) return;
    // Ease towards 90% while the page loads
    const target = 90;
    progress += Math.max(0.2, (target - progress) * 0.03);
    if (progress > target) progress = target;
    render();
    rafId = requestAnimationFrame(step);
  }

  function show(){ el.style.display = 'flex'; }
  function hide(){ running = false; if (rafId) cancelAnimationFrame(rafId); el.style.opacity = '0'; setTimeout(()=>{ el.style.display='none'; }, 250); }
  function setProgress(p){ progress = Math.max(0, Math.min(100, p)); render(); }

  // Expose API
  window.AppLoader = { show, hide, setProgress };

  // Start animation until window load
  render();
  rafId = requestAnimationFrame(step);

  window.addEventListener('load', function(){
    // Complete to 100% and hide
    setProgress(100);
    setTimeout(hide, 200);
  });
})();
