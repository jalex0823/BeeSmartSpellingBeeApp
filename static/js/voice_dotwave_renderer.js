// BeeSmart dotted ribbon voice visualizer
// Renders multi-wave dotted ribbon synced to announcer speech.
// Reads settings from window.BeeSmartVoiceVizCfg if present.
(function (global) {
  const Cfg = () => Object.assign({
    // Denser, smoother default look
    MAX_WAVES: 11,
    DOTS_PER_WAVE: 128,
    DOT_RADIUS: 2.6,
    WAVE_SPACING: 14,
    HORIZONTAL_PAD_CSS: 18,
    VERTICAL_BUFFER: 18, // px top & bottom to prevent clipping
    // Honey & brown palette from light honey to deep amber/brown
    waveColors: [
      'rgba(255, 230, 170, 0.95)', // light honey
      'rgba(255, 216, 140, 0.95)',
      'rgba(255, 204, 102, 0.95)',
      'rgba(255, 190, 76, 0.95)',
      'rgba(255, 171, 52, 0.95)',
      'rgba(255, 153, 26, 0.95)',
      'rgba(240, 132, 20, 0.95)',
      'rgba(220, 118, 18, 0.95)',
      'rgba(199, 103, 16, 0.95)',
      'rgba(168, 85, 12, 0.95)',  // amber-brown
      'rgba(140, 70, 10, 0.95)'   // deeper brown
    ],
    gradientLR: { enabled: true, alpha: 0.28, stops: [ {offset:0,color:'rgba(255,216,140,1)'}, {offset:1,color:'rgba(168,85,12,1)'} ] },
    endFade: { enabled: true, fraction: 0.32 },
    thicknessBulge: { enabled: true, magnitude: 0.18, speed: 0.002, cycles: 1.0 },
    centerGlow: { enabled: true, alpha: 0.55, verticalSpan: 0.58, energyScale: 1.0, horizontalFraction: 0.12 },
    tipPinch: { enabled: true, power: 2.1 },
    energyTargets: { speaking: 1.0, pausing: 0.06, idle: 0.04 },
    easing: { energy: 0.2, wavePack: 0.24, dipDecay: 0.16, surgeDecay: 0.12 },
    boostScales: { dip: 0.6, surge: 0.2 },
    waveShape: { baseFreq: 2.2, freqStep: 0.28, ampBase: 26, ampStep: 6.5, rippleFreq: 11, rippleBase: 4.5 }
  }, (global.BeeSmartVoiceVizCfg||{}));

  function clamp(v,a,b){return Math.max(a,Math.min(b,v));}

  function makeGradient(ctx, x0, y0, x1, y1, stops){
    const g = ctx.createLinearGradient(x0,y0,x1,y1);
    for(const s of stops){ g.addColorStop(s.offset, s.color); }
    return g;
  }

  function create(container, options={}){
    // Canvas
    const canvas = document.createElement('canvas');
    canvas.style.width='100%';
    canvas.style.height=(options.height||180)+'px';
    canvas.style.display='block';
    canvas.style.filter='drop-shadow(0 0 4px rgba(0,0,0,0.08))';
    container.innerHTML='';
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    let dpr = Math.max(1, global.devicePixelRatio||1);

    const cfg = Cfg();
    let width=0, height=0, innerLeft=0, innerRight=0, innerWidth=0, centerY=0, vBuffer=0, innerTop=0, innerBottom=0, innerHeight=0;
    let energy = 0, targetEnergy = cfg.energyTargets.idle;
    let wavePack = 0; // packs waves together slightly when speaking
    let dip = 0, surge = 0; // transient boosts
    let t0 = performance.now();

    function resize(){
      const rect = container.getBoundingClientRect();
      width = Math.max(10, rect.width);
      height = Math.max(10, options.height||180);
      canvas.width = Math.floor(width*dpr);
      canvas.height = Math.floor(height*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0);
      innerLeft = cfg.HORIZONTAL_PAD_CSS;
      innerRight = width - cfg.HORIZONTAL_PAD_CSS;
      innerWidth = Math.max(10, innerRight - innerLeft);
      vBuffer = Math.max(0, cfg.VERTICAL_BUFFER||0);
      innerTop = vBuffer;
      innerBottom = height - vBuffer;
      innerHeight = Math.max(10, innerBottom - innerTop);
      centerY = Math.floor(innerTop + innerHeight*0.5);
    }
    resize();
    global.addEventListener('resize', resize);

    function setMode(mode){
      targetEnergy = cfg.energyTargets[mode] ?? cfg.energyTargets.idle;
    }

    function onStart(){ setMode('speaking'); surge = Math.max(surge, cfg.boostScales.surge); }
    function onEnd(){ setMode('pausing'); dip = Math.max(dip, cfg.boostScales.dip); }
    function onBoundary(){ surge = Math.max(surge, cfg.boostScales.surge*1.1); }

    global.addEventListener('quiz-speech-start', onStart);
    global.addEventListener('quiz-speech-end', onEnd);
    global.addEventListener('quiz-speech-boundary', onBoundary);

    function draw(now){
      const dt = Math.min(0.06, (now - t0)/1000); t0 = now;
      // Energy easing
      energy += (targetEnergy - energy) * clamp(cfg.easing.energy,0.01,0.5);
      dip *= (1 - clamp(cfg.easing.dipDecay,0.02,0.6));
      surge *= (1 - clamp(cfg.easing.surgeDecay,0.02,0.6));
      const energyNow = clamp(energy + surge - dip, 0, 1.2);

      ctx.clearRect(0,0,width,height);

      const waves = Math.max(1, cfg.MAX_WAVES|0);
      const dots = Math.max(8, cfg.DOTS_PER_WAVE|0);
      const spacing = cfg.WAVE_SPACING;
      const ampBase = cfg.waveShape.ampBase;
      const ampStep = cfg.waveShape.ampStep;
      const baseFreq = cfg.waveShape.baseFreq;
      const freqStep = cfg.waveShape.freqStep;
      const rippleFreq = cfg.waveShape.rippleFreq;
      const rippleBase = cfg.waveShape.rippleBase;

      // Thickness bulge over X
      const bulgeMag = cfg.thicknessBulge.enabled? cfg.thicknessBulge.magnitude: 0;
      const bulgeSpeed = cfg.thicknessBulge.speed||0;
      const bulgeCycles = cfg.thicknessBulge.cycles||1;
      const bulgePhase = now*bulgeSpeed;

      // Gradient LR overlay
      let gradLR = null;
      if(cfg.gradientLR?.enabled){ gradLR = makeGradient(ctx, innerLeft,0, innerRight,0, cfg.gradientLR.stops); }

      for(let wi=0; wi<waves; wi++){
        const color = cfg.waveColors[wi % cfg.waveColors.length] || 'rgba(255, 180, 55, 0.9)';
        ctx.fillStyle = color;
        const yBase = centerY + (wi - (waves-1)/2) * (spacing - wavePack*2);
        const amp = (ampBase + wi*ampStep) * (0.4 + 0.6*energyNow);
        const freq = baseFreq + wi*freqStep;

        for(let di=0; di<dots; di++){
          const u = di/(dots-1); // 0..1
          const x = innerLeft + u*innerWidth;
          // Tip pinch: attenuate amplitude near edges
          let edgeFactor = 1.0;
          if(cfg.tipPinch?.enabled){
            const dEdge = Math.min(u, 1-u); // 0 at edges
            edgeFactor = Math.pow(dEdge*2, cfg.tipPinch.power||1.2); // 0..1
          }
          const bulge = bulgeMag ? (1 + bulgeMag*Math.sin((u*bulgeCycles + bulgePhase)*Math.PI*2)) : 1;
          let A = amp * edgeFactor * bulge;
          // Strict vertical confinement: never exceed innerTop/innerBottom with a small safety margin
          const maxA = (innerHeight*0.5) - 2; // 2px safety
          A = Math.min(A, maxA);
          const ripple = Math.sin((u * rippleFreq + now*0.0015)*Math.PI*2)*rippleBase*energyNow;
          let y = yBase + Math.sin((u*freq + now*0.0018)*Math.PI*2) * A + ripple;
          if (y < innerTop+1) y = innerTop+1;
          if (y > innerBottom-1) y = innerBottom-1;

          // End fade alpha
          let alphaMul = 1.0;
          if(cfg.endFade?.enabled){
            const f = clamp(cfg.endFade.fraction ?? 0.18, 0, 0.5);
            const left = clamp(u/f, 0, 1);
            const right = clamp((1-u)/f, 0, 1);
            alphaMul = Math.min(left, right);
          }
          // Smaller near tips to help "points together" mouth tips
          const r = Math.max(0.8, cfg.DOT_RADIUS) * (0.85 + 0.35*energyNow) * (0.62 + 0.38*edgeFactor);
          ctx.globalAlpha = alphaMul;
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI*2);
          ctx.fill();

          // Optional gradient overlay pass
          if(gradLR){
            ctx.globalAlpha = (cfg.gradientLR.alpha ?? 0.35) * alphaMul;
            ctx.fillStyle = gradLR;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = color;
          }
        }
      }

      // Center glow overlay
      if(cfg.centerGlow?.enabled){
        const gA = (cfg.centerGlow.alpha??0.5) * (1 + (cfg.centerGlow.energyScale??1)*energyNow*0.5);
        const span = clamp(cfg.centerGlow.verticalSpan??0.6, 0.1, 1);
        const h2 = height*span;
        const gy0 = centerY - h2/2, gy1 = centerY + h2/2;
        const g = ctx.createLinearGradient(0, gy0, 0, gy1);
        g.addColorStop(0, 'rgba(255,255,255,0)');
        g.addColorStop(0.5, `rgba(255,255,255,${gA})`);
        g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.globalAlpha = 1;
        ctx.fillStyle = g;
        ctx.fillRect(innerLeft, gy0, innerWidth, h2);
      }

      requestAnimationFrame(draw);
    }

    // Speech fallback polling (optional)
    if(typeof speechSynthesis !== 'undefined'){
      setInterval(()=>{
        const speaking = speechSynthesis.speaking;
        if(speaking) setMode('speaking'); else setMode('pausing');
      }, 250);
    }

    requestAnimationFrame(draw);

    return { canvas, destroy(){
      global.removeEventListener('resize', resize);
      global.removeEventListener('quiz-speech-start', onStart);
      global.removeEventListener('quiz-speech-end', onEnd);
      global.removeEventListener('quiz-speech-boundary', onBoundary);
      if(canvas.parentNode) canvas.parentNode.removeChild(canvas);
    }};
  }

  global.DotWaveVisualizer = { init: create };
})(window);
