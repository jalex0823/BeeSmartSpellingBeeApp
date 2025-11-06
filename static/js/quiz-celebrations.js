(function(){
  // Quiz celebrations: persona overlay + confetti + optional stinger
  const STATE = {
    stylesInjected: false,
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    enabled: true
  };

  // Load persisted preference (default true)
  try {
    const raw = localStorage.getItem('celebrations_enabled');
    if (raw !== null) STATE.enabled = raw === 'true';
    else if (STATE.reducedMotion) STATE.enabled = false; // default off for reduced-motion unless user opts in
  } catch(_){ }

  function injectStyles(){
    if (STATE.stylesInjected) return;
    const css = `
    .quiz-celebrate-layer{position:absolute;inset:0;pointer-events:none;z-index:10000;}
    .quiz-celebrate-layer *, .quiz-celebrate-layer{will-change: transform, opacity;}
    .quiz-confetti-canvas{position:absolute;inset:0;}
    .quiz-persona-bits{position:absolute;left:0;right:0;top:0;bottom:0;}
    .quiz-persona-bits .bit{position:absolute;font-size:22px;opacity:0;transform:translate3d(0,0,0);}
    @keyframes floatUpFade{0%{transform:translateY(8px) scale(0.9);opacity:0}20%{opacity:1}100%{transform:translateY(-60px) scale(1.05);opacity:0}}
    @keyframes popPulse{0%{transform:scale(0.8);opacity:0}50%{transform:scale(1.1);opacity:1}100%{transform:scale(1);opacity:0}}
    .celebrate-glow{position:absolute;inset:0;border-radius:18px;box-shadow:0 0 0 0 rgba(255,215,0,.7);animation:glowPulse .9s ease-out forwards}
    @keyframes glowPulse{0%{box-shadow:0 0 0 0 rgba(255,215,0,.7)}100%{box-shadow:0 0 0 14px rgba(255,215,0,0)}}
    `;
    const el = document.createElement('style');
    el.textContent = css;
    document.head.appendChild(el);
    STATE.stylesInjected = true;
  }

  function withLayer(container, fn){
    injectStyles();
    const root = container || document.body;
    // Ensure the root is position:relative to place absolute layer
    const prevPos = root.style.position;
    if (!getComputedStyle(root).position || getComputedStyle(root).position === 'static') {
      root.style.position = 'relative';
    }
    const layer = document.createElement('div');
    layer.className = 'quiz-celebrate-layer allow-anim';
    root.appendChild(layer);
    try { fn(layer); } catch(_){ /* no-op */ }
    // Auto cleanup after 1800ms
    setTimeout(()=>{ if(layer.parentNode){ layer.parentNode.removeChild(layer); } root.style.position = prevPos; }, 1800);
  }

  // Tiny confetti burst (no deps)
  function burstConfetti(layer){
    if (STATE.reducedMotion) return; // respect reduced motion
    const canvas = document.createElement('canvas');
    canvas.className = 'quiz-confetti-canvas';
    layer.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = layer.clientWidth; canvas.height = layer.clientHeight; }
    resize();
    const colors = ['#FFD700','#FF69B4','#42A5F5','#66BB6A','#FFA000','#AB47BC'];
    const count = Math.max(24, Math.min(80, Math.floor((canvas.width*canvas.height)/50000)));
    const parts = Array.from({length: count}, ()=>({
      x: canvas.width*0.5 + (Math.random()-0.5)*60,
      y: canvas.height*0.4 + (Math.random()-0.5)*40,
      vx: (Math.random()-0.5)*5,
      vy: -4 - Math.random()*3,
      g: 0.18 + Math.random()*0.05,
      size: 3 + Math.random()*3,
      color: colors[Math.floor(Math.random()*colors.length)],
      life: 900 + Math.random()*500
    }));
    let start = null;
    function tick(ts){
      if(!start) start = ts;
      const dt = Math.min(32, ts - start); // clamp frame delta
      start = ts;
      ctx.clearRect(0,0,canvas.width,canvas.height);
      let any = false;
      for(const p of parts){
        p.vy += p.g;
        p.x += p.vx;
        p.y += p.vy;
        p.life -= dt;
        if (p.life<=0) continue;
        any = true;
        ctx.save();
        ctx.globalAlpha = Math.max(0, Math.min(1, p.life/1000));
        ctx.fillStyle = p.color;
        ctx.translate(p.x, p.y);
        ctx.rotate(((p.life%360)/180)*Math.PI);
        ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size);
        ctx.restore();
      }
      if(any){ requestAnimationFrame(tick); }
    }
    requestAnimationFrame(tick);
    // Resize guard
    const ro = new ResizeObserver(()=>resize());
    try { ro.observe(layer); } catch(_){}
    // Cleanup observer with layer removal
    setTimeout(()=>{ try { ro.disconnect(); } catch(_){ } }, 1800);
  }

  // Minimal persona overlays (emoji-based for light weight)
  function personaBits(layer, avatarId){
    const id = String(avatarId||'').toLowerCase();
    let symbols = ['⭐','✨','🌟'];
    if (id.includes('al-bee') || id.includes('albee') || id.includes('professor')) symbols = ['➗','➕','✖️','🧪','📐'];
    else if (id.includes('rocker')) symbols = ['🎸','🎵','🥁','🎶'];
    else if (id.includes('super') || id.includes('ware-bee')) symbols = ['⚡','🛡️','✨','🌟'];
    else if (id.includes('queen')) symbols = ['👑','✨','💫'];
    else if (id.includes('selfie')) symbols = ['📸','✨','💫'];
    else if (id.includes('monster') || id.includes('zom')) symbols = ['🧪','💥','✨'];

    const wrap = document.createElement('div');
    wrap.className = 'quiz-persona-bits';
    layer.appendChild(wrap);
    const n = STATE.reducedMotion ? 8 : 16;
    const rect = layer.getBoundingClientRect();
    for(let i=0;i<n;i++){
      const bit = document.createElement('div');
      bit.className = 'bit';
      bit.textContent = symbols[i % symbols.length];
      const x = (rect.width*0.3) + Math.random()*rect.width*0.4;
      const y = (rect.height*0.45) + (Math.random()-0.5)*20;
      bit.style.left = `${x}px`;
      bit.style.top = `${y}px`;
      const dur = 700 + Math.random()*500;
      bit.style.animation = `floatUpFade ${dur}ms ease-out forwards`;
      bit.style.filter = 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))';
      wrap.appendChild(bit);
    }
    // Subtle container glow
    const glow = document.createElement('div');
    glow.className = 'celebrate-glow';
    layer.appendChild(glow);
  }

  function playStinger(){
    if (STATE.reducedMotion) return; // treat as global quiet mode
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = 'triangle';
      o.connect(g); g.connect(ctx.destination);
      const t0 = ctx.currentTime;
      // fast two-note arpeggio
      o.frequency.setValueAtTime(659.25, t0); // E5
      o.frequency.setValueAtTime(783.99, t0 + 0.09); // G5
      g.gain.setValueAtTime(0.18, t0);
      g.gain.exponentialRampToValueAtTime(0.01, t0 + 0.35);
      o.start(t0); o.stop(t0 + 0.38);
      // auto close context later to avoid leaks
      setTimeout(()=>{ try { ctx.close(); } catch(_){} }, 500);
    } catch(_){ }
  }

  function celebrateCorrect(container, options={}){
    if (!STATE.enabled) return;
    const root = container || document.body;
    const avatarId = (window.userAvatarLoader && window.userAvatarLoader.getAvatarId && window.userAvatarLoader.getAvatarId()) || 'mascot-bee';
    withLayer(root, (layer)=>{
      personaBits(layer, avatarId);
      burstConfetti(layer);
    });
    if (options.sound !== false) playStinger();
  }

  function setEnabled(v){
    STATE.enabled = !!v;
    try { localStorage.setItem('celebrations_enabled', String(STATE.enabled)); } catch(_){ }
  }
  function getEnabled(){ return !!STATE.enabled; }

  window.QuizCelebrations = { celebrateCorrect, setEnabled, getEnabled };
})();
