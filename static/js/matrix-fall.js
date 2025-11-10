// Yellow Matrix Falling Symbols Animation (optimized for low-powered devices)
(function(){
  const el = document.getElementById('appHoneyLoader');
  if(!el) return;

  const prefersReduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const lowMem = typeof navigator.deviceMemory === 'number' && navigator.deviceMemory <= 2; // <=2GB
  const lowCores = typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency <= 2; // <=2 cores
  const LOW_POWER = prefersReduced || lowMem || lowCores;

  // create canvas if not present
  let canvas = document.getElementById('matrixCanvas');
  if(!canvas){
    canvas = document.createElement('canvas');
    canvas.id = 'matrixCanvas';
    canvas.setAttribute('aria-hidden','true');
    el.insertBefore(canvas, el.firstChild);
  }
  const ctx = canvas.getContext('2d');

  const DPR = LOW_POWER ? 1 : Math.min(window.devicePixelRatio || 1, 1.5);
  let colW = LOW_POWER ? 20 : 16; // wider columns reduce total draws
  const baseStep = LOW_POWER ? 10 : 14;
  const jitter = LOW_POWER ? 2 : 4;
  const fadeAlpha = LOW_POWER ? 0.16 : 0.12;
  const fontPx = 14;
  const yellow = 'rgba(255,213,64,'; // alpha appended

  let width=0, height=0, cols=0; let drops=[];
  let rafId=0, intervalId=0, active=true;
  let liteOffset=0; // for interval mode alternating columns

  const CHARS='BEE0123456789';
  function CHAR_AT(){ return CHARS[(Math.random()*CHARS.length)|0]; }

  // Center fade mask over crest/logo to gently dim streams behind it
  const overlayEl = document.getElementById('loaderProgressOverlay') || document.querySelector('.loader-logo-wrapper');
  let mask = { cx: 0, cy: 0, innerR: 0, outerR: 0, ready: false };
  function updateMaskMetrics(){
    if(!overlayEl){ mask.ready = false; return; }
    const elRect = el.getBoundingClientRect();
    const oRect = overlayEl.getBoundingClientRect();
    const cx = (oRect.left - elRect.left) + oRect.width/2;
    const cy = (oRect.top  - elRect.top)  + oRect.height/2;
    const minDim = Math.max(1, Math.min(oRect.width, oRect.height));
    // Inner radius fully faded, outer radius feather
    mask = {
      cx, cy,
      innerR: (minDim * 0.38),  // slightly larger inner fade to smooth under-logo transition
      outerR: (minDim * 0.70),  // expanded feather for softer blend
      ready: true
    };
  }
  function applyLogoFadeMask(){
    if(!mask.ready) return;
    // Erase some of the canvas under the crest using a soft radial gradient
    const g = ctx.createRadialGradient(mask.cx, mask.cy, mask.innerR, mask.cx, mask.cy, mask.outerR);
    // destination-out subtracts alpha: more opaque at center, feather outward
    g.addColorStop(0.0, 'rgba(0,0,0,0.75)');
    g.addColorStop(1.0, 'rgba(0,0,0,0.0)');
    ctx.save();
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(mask.cx, mask.cy, mask.outerR, 0, Math.PI*2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function sizeCanvas(){
    const w = Math.max(1, el.clientWidth);
    const h = Math.max(1, el.clientHeight);
    canvas.width = Math.floor(w * DPR);
    canvas.height = Math.floor(h * DPR);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(DPR,0,0,DPR,0,0);
    width = w; height = h;
    cols = Math.max(1, Math.floor(width / colW));
    if(drops.length < cols){
      for(let i=drops.length;i<cols;i++){ drops[i] = Math.random()*height; }
    } else if(drops.length > cols){ drops.length = cols; }
    updateMaskMetrics();
  }

  let resizeTimer;
  function onResize(){
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(sizeCanvas, 80);
  }
  window.addEventListener('resize', onResize, { passive:true });
  // Recompute mask on logo / overlay size changes
  if('ResizeObserver' in window && overlayEl){
    const ro = new ResizeObserver(()=>{ updateMaskMetrics(); });
    ro.observe(overlayEl);
  }

  function stepFull(){
    if(!active) return;
    ctx.fillStyle = `rgba(0,0,0,${fadeAlpha})`;
    ctx.fillRect(0,0,width,height);
    ctx.font = `${fontPx}px Menlo,Consolas,Monaco,monospace`;
    for(let i=0;i<cols;i++){
      const x=i*colW+4;
      const y=(drops[i] = drops[i] + baseStep + Math.random()*jitter);
      ctx.fillStyle = yellow + (0.65 + Math.random()*0.25) + ')';
      ctx.fillText(CHAR_AT(), x, y);
      if(y>height && Math.random()>0.975){ drops[i]=0; }
    }
    applyLogoFadeMask();
    rafId = requestAnimationFrame(stepFull);
  }

  function stepLite(){
    if(!active) return;
    ctx.fillStyle = `rgba(0,0,0,${fadeAlpha})`;
    ctx.fillRect(0,0,width,height);
    ctx.font = `${fontPx}px Menlo,Consolas,Monaco,monospace`;
    for(let i=liteOffset;i<cols;i+=2){
      const x=i*colW+4;
      const y=(drops[i] = drops[i] + baseStep + Math.random()*jitter);
      ctx.fillStyle = yellow + (0.55 + Math.random()*0.25) + ')';
      ctx.fillText(CHAR_AT(), x, y);
      if(y>height && Math.random()>0.98){ drops[i]=0; }
    }
    liteOffset = liteOffset ^ 1;
    applyLogoFadeMask();
  }

  function drawStatic(){
    ctx.clearRect(0,0,width,height);
    ctx.font = `${fontPx}px Menlo,Consolas,Monaco,monospace`;
    for(let i=0;i<cols;i++){
      const x=i*colW+4;
      const y=Math.random()*height;
      ctx.fillStyle = yellow + (0.35 + Math.random()*0.35) + ')';
      ctx.fillText(CHAR_AT(), x, y);
    }
  }

  function stop(){
    active=false;
    if(rafId){ cancelAnimationFrame(rafId); rafId=0; }
    if(intervalId){ clearInterval(intervalId); intervalId=0; }
  }

  function start(){
    if(prefersReduced){ drawStatic(); return; }
    stop();
    active=true;
    if(LOW_POWER){
      intervalId = setInterval(stepLite, 50); // ~20fps
    } else {
      rafId = requestAnimationFrame(stepFull);
    }
  }

  document.addEventListener('visibilitychange', ()=>{
    if(document.hidden){ stop(); }
    else if(!prefersReduced){ start(); }
  });
  document.addEventListener('honeyLoaderFinished', stop);

  drops = []; sizeCanvas();
  start();
})();