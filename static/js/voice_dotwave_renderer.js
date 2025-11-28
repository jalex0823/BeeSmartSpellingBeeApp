// BeeSmart dotted ribbon voice visualizer
// Renders multi-wave dotted ribbon synced to announcer speech.
// Reads settings from window.BeeSmartVoiceVizCfg if present.
(function (global) {
  // Configuration factory merges user overrides
  const Cfg = () => Object.assign({
    // Higher density & more waves for richer lip surface
    MAX_WAVES: 13,
    DOTS_PER_WAVE: 160,
    DOT_RADIUS: 2.4,
    WAVE_SPACING: 13,
    HORIZONTAL_PAD_CSS: 22, // a touch more padding left/right
    VERTICAL_BUFFER: 14,    // top/bottom buffer to avoid clipping
    VERTICAL_SOFT_CLAMP: 6, // extra soft clamp inside buffer
    // Taper & mapping
    TIP_PINCH_POWER: 2.6,   // stronger taper at ends
    NON_LINEAR_X_MAP: true, // cluster points toward tips (mouth shape)
    // Dynamically generated honey/brown palette (light → dark)
    waveColors: (function(){
      const stops = [
        [255, 235, 185], // very light honey
        [255, 222, 150], // honey
        [255, 208, 110], // golden
        [255, 194, 78],  // deep golden
        [255, 178, 52],  // rich amber
        [247, 160, 32],  // amber mid
        [235, 140, 24],  // darker amber
        [220, 125, 20],  // burnt honey
        [202, 110, 18],  // soft brown
        [182, 96, 16],   // cocoa honey
        [160, 82, 14],   // brown
        [138, 70, 12],   // deeper brown
        [118, 58, 10]    // near molasses
      ];
      return stops.map(([r,g,b]) => `rgba(${r},${g},${b},0.95)`);
    })(),
    gradientLR: { enabled: true, alpha: 0.30, stops: [ {offset:0,color:'rgba(255,235,185,1)'}, {offset:1,color:'rgba(118,58,10,1)'} ] },
    endFade: { enabled: true, fraction: 0.34 },
    thicknessBulge: { enabled: true, magnitude: 0.22, speed: 0.0018, cycles: 1.0 },
    centerGlow: { enabled: true, alpha: 0.6, verticalSpan: 0.55, energyScale: 1.0, horizontalFraction: 0.1 },
    energyTargets: { speaking: 1.0, pausing: 0.07, idle: 0.045 },
    easing: { energy: 0.22, wavePack: 0.26, dipDecay: 0.17, surgeDecay: 0.13 },
    boostScales: { dip: 0.62, surge: 0.22 },
    waveShape: { baseFreq: 2.3, freqStep: 0.26, ampBase: 28, ampStep: 7.0, rippleFreq: 12, rippleBase: 5 }
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

      // Precompute lip shaping function for horizontal domain (smooth ellipse narrowing at tips)
      function mapU(u){
        if(!cfg.NON_LINEAR_X_MAP) return innerLeft + u*innerWidth;
        // Cosine ease: clusters more points near ends (mouth tips)
        const eased = 0.5 - 0.5*Math.cos(Math.PI*u); // 0..1 with more density near 0/1
        return innerLeft + eased*innerWidth;
      }
      function edgeTaper(u){
        const edge = Math.min(u, 1-u); // 0 at tips
        // Power curve accentuates taper; TIP_PINCH_POWER controls steepness
        return Math.pow(edge*2, cfg.TIP_PINCH_POWER || 2.4); // 0..1
      }
      function lipProfile(u){
        // Elliptical profile emphasizing center fullness
        // sin(pi*u) gives 0 at ends, 1 at center
        return Math.pow(Math.sin(Math.PI*u), 1.15); // mild sharpening
      }

      for(let wi=0; wi<waves; wi++){
        const color = cfg.waveColors[wi % cfg.waveColors.length] || 'rgba(255,180,55,0.9)';
        ctx.fillStyle = color;
        // Slight vertical staggering with wavePack and a soft center compression while idle
        const idleCompress = 1 - 0.25*energyNow; // narrower stack when quiet
        const yBase = centerY + (wi - (waves-1)/2) * (spacing*idleCompress - wavePack*2);
        const amp = (ampBase + wi*ampStep) * (0.42 + 0.58*energyNow);
        const freq = baseFreq + wi*freqStep;

        for(let di=0; di<dots; di++){
          const u = di/(dots-1); // normalized domain
          const x = mapU(u);
          const taper = edgeTaper(u);         // 0 at ends → reduces amplitude & radius
          const profile = lipProfile(u);      // center fullness
          const bulge = bulgeMag ? (1 + bulgeMag*Math.sin((u*bulgeCycles + bulgePhase)*Math.PI*2)) : 1;
          // Combined amplitude shaping
          let A = amp * taper * profile * bulge;
          const maxA = (innerHeight*0.5) - (cfg.VERTICAL_SOFT_CLAMP || 4);
          if (A > maxA) A = maxA;
          const ripple = Math.sin((u * rippleFreq + now*0.0014)*Math.PI*2)*rippleBase*energyNow;
          let waveY = Math.sin((u*freq + now*0.0017)*Math.PI*2) * A + ripple;
          let y = yBase + waveY;
          // Hard vertical confinement (respect top/bottom buffers)
          const topLimit = innerTop + (cfg.VERTICAL_SOFT_CLAMP||4);
          const bottomLimit = innerBottom - (cfg.VERTICAL_SOFT_CLAMP||4);
          if (y < topLimit) y = topLimit;
          if (y > bottomLimit) y = bottomLimit;

          // Alpha fade at ends
          let alphaMul = 1.0;
          if(cfg.endFade?.enabled){
            const f = clamp(cfg.endFade.fraction ?? 0.2, 0, 0.55);
            const left = clamp(u/f, 0, 1);
            const right = clamp((1-u)/f, 0, 1);
            alphaMul = Math.min(left, right);
          }
          // Dynamic radius scaling: smaller near tips + subtle breathing
          const baseR = Math.max(0.75, cfg.DOT_RADIUS);
          const breathing = 0.85 + 0.3*energyNow;
          const r = baseR * breathing * (0.55 + 0.45*taper) * (0.7 + 0.3*profile);

            ctx.globalAlpha = alphaMul;
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI*2);
          ctx.fill();

          // Gradient overlay adds depth & honey sheen
          if(gradLR){
            ctx.globalAlpha = (cfg.gradientLR.alpha ?? 0.32) * alphaMul;
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
