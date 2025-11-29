// static/js/bee_swarm_canvas.js
// 2D Canvas Particle Wave Visualizer - glowing dots forming wave shape with center-out animation and edge tapering

(function(global){

  const cfgDefault = {
    letterCount: 1200,     // number of particle dots (increased for better wave density)
    baseSize: 8,           // base particle size
    attractStrength: 0.08, // weaker attraction (more loose swarm feel)
    damp: 0.82,            // less damping (more bouncy)
    baseNoise: 0.15,       // procedural noise for wandering
    centerOffsetX: -0.26,  // shift swarm center horizontally (-1..1 of width) - favor left alignment
    centerOffsetY: -0.02,  // shift swarm center vertically (-1..1 of height) - slight upward centering
    // brown/gold palette for glowing particle effect
    palette: [
      "#8B6914", // dark brown
      "#A0826D", // warm brown
      "#B8860B", // golden brown
      "#CD853F", // peru
      "#C19A6B", // khaki brown
      "#D4A347", // honey brown
      "#DAA520", // goldenrod
      "#C89F3F", // dark honey
      "#DEB887", // burlywood
      "#D2B48C", // tan
      "#BC8F8F", // rosy brown
      "#8B7355", // deep brown
      "#A0522D", // sienna
      "#8B4513", // saddle brown
      "#D2691E"  // chocolate
    ]
  };

  let canvas = null, ctx = null, containerEl = null;
  let width = 860, height = 260;
  let letters = [];
  let baseTargets = [];
  let running = false;
  let rafId = null;

  // announcer-driven state
  let isSpeaking = false;
  let amplitude = 0;
  let ampSmooth = 0;
  let pulsePhase = 0; // for rhythm-synced pulsing
  let lastBoundaryTime = 0; // track speech boundaries for rhythm
  let boundaryBoost = 0; // transient boost on each boundary for visible pulses

  // Discrete mouth states (0=closed, 1-3 speaking variants)
  let mouthState = 0; // current state index
  const MOUTH_STATES = {
    0: { rx: 0.95, ry: 0.35, gap: 0.00, tilt: 0.00 }, // closed (ellipse, minimal height)
    1: { rx: 1.05, ry: 0.55, gap: 0.08, tilt: -0.05 }, // small open (slight vertical)
    2: { rx: 1.15, ry: 0.65, gap: 0.16, tilt: 0.00 },  // medium open
    3: { rx: 1.25, ry: 0.75, gap: 0.24, tilt: 0.06 }   // wide open
  };
  let targetState = 0;
  let stateLerp = 0; // 0..1 interpolation toward target

  const BeeSwarmCanvas = {
    init,
    destroy
  };

  global.BeeSwarmCanvas = BeeSwarmCanvas;

  // ============================
  //  Init / Destroy
  // ============================
  async function init(container, options = {}) {
    const cfg = Object.assign({}, cfgDefault, options);

    containerEl = container;
    if (!containerEl) {
      console.error("🐝 BeeSwarmCanvas: container not found.");
      return null;
    }

    // Wait for container to have dimensions
    let attempts = 0;
    await new Promise((resolve) => {
      const check = () => {
        const rect = containerEl.getBoundingClientRect();
        attempts++;
        if ((rect.width > 0 && rect.height > 0) || attempts > 20) {
          width = rect.width;
          height = rect.height;
          console.log(`🐝 Container ready after ${attempts} attempts: ${width}x${height}px`);
          resolve();
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    });

    // Create canvas
    canvas = document.createElement("canvas");
    canvas.id = "beeSwarmCanvas";
    canvas.style.position = "absolute";
    canvas.style.inset = "0";
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.pointerEvents = "none";
    canvas.style.background = "transparent";
    containerEl.appendChild(canvas);

    ctx = canvas.getContext("2d");
    resize();
    window.addEventListener("resize", resize);

    // Optional mask support: use options.maskSrc or global __BeeSwarmMaskUrl
    const maskUrl = options.maskSrc || window.__BeeSwarmMaskUrl || null;
    if (maskUrl) {
      try {
        await loadMask(maskUrl);
        buildLetterSwarm(cfg.letterCount, cfg);
      } catch (e) {
        console.warn('BeeSwarm: mask failed, continuing freeform', e);
        buildLetterSwarm(cfg.letterCount, cfg);
      }
    } else {
      // Build swarm of dancing letters (freeform)
      buildLetterSwarm(cfg.letterCount, cfg);
    }

    // Setup speech events
    setupSpeechEvents();

    running = true;
    rafId = requestAnimationFrame((t) => step(t, cfg));

    console.log(`🐝 Particle wave swarm initialized with ${letters.length} dots (center-out animation, tapered edges)`);
    console.log(`🐝 Listening to announcer speech events`);
    return BeeSwarmCanvas;
  }
  // ============================
  //  Mask Support
  // ============================
  let maskCanvas = null;
  let maskCtx = null;
  let maskImgData = null;
  let maskWidth = 0;
  let maskHeight = 0;
  let maskReady = false;
  const MASK_THRESHOLD = 110; // 0..255 darkness threshold; <= inside (raised to include near-black edges)

  // Map mask image to container without resizing the container.
  // canvasXY = maskFit.offsetX + maskPixelXY * maskFit.scale
  let maskFit = { scale: 1, offsetX: 0, offsetY: 0 };
  // Dark region (<= threshold) bounds in mask pixel coordinates
  let darkBounds = { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0, cx: 0, cy: 0 };
  // Dark region mapped into canvas coordinates
  let darkBoundsCanvas = { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0, cx: 0, cy: 0 };
  // Scale used to turn normalized shape coords into canvas pixels (derived from dark bounds)
  let shapeScale = 1;

  function computeMaskFit() {
    if (!containerEl || !maskReady) return;
    const rect = containerEl.getBoundingClientRect();
    const sx = rect.width / maskWidth;
    const sy = rect.height / maskHeight;
    const scale = Math.min(sx, sy); // contain
    const drawnW = maskWidth * scale;
    const drawnH = maskHeight * scale;
    const offsetX = (rect.width - drawnW) / 2;
    const offsetY = (rect.height - drawnH) / 2;
    maskFit = { scale, offsetX, offsetY };

    // Map dark bounds to canvas
    if (darkBounds.width > 0 && darkBounds.height > 0) {
      const minX = offsetX + darkBounds.minX * scale;
      const maxX = offsetX + darkBounds.maxX * scale;
      const minY = offsetY + darkBounds.minY * scale;
      const maxY = offsetY + darkBounds.maxY * scale;
      const widthC = Math.max(0, maxX - minX);
      const heightC = Math.max(0, maxY - minY);
      const cx = offsetX + darkBounds.cx * scale;
      const cy = offsetY + darkBounds.cy * scale;
      darkBoundsCanvas = { minX, minY, maxX, maxY, width: widthC, height: heightC, cx, cy };
    } else {
      const minX = offsetX;
      const minY = offsetY;
      const maxX = offsetX + drawnW;
      const maxY = offsetY + drawnH;
      const widthC = drawnW;
      const heightC = drawnH;
      const cx = offsetX + drawnW / 2;
      const cy = offsetY + drawnH / 2;
      darkBoundsCanvas = { minX, minY, maxX, maxY, width: widthC, height: heightC, cx, cy };
    }

    // Conservative scaling: keep letters within dark region with some margin
    shapeScale = Math.max(1, Math.min(darkBoundsCanvas.width, darkBoundsCanvas.height) * 0.45);
  }

  function loadMask(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        maskCanvas = document.createElement('canvas');
        maskWidth = img.width;
        maskHeight = img.height;
        maskCanvas.width = maskWidth;
        maskCanvas.height = maskHeight;
        maskCtx = maskCanvas.getContext('2d');
        maskCtx.drawImage(img, 0, 0);
        maskImgData = maskCtx.getImageData(0, 0, maskWidth, maskHeight);
        // Compute dark region bounds within mask pixels
        let minX = maskWidth, minY = maskHeight, maxX = 0, maxY = 0;
        let sumX = 0, sumY = 0, count = 0;
        const data = maskImgData.data;
        for (let y = 0; y < maskHeight; y++) {
          const row = y * maskWidth;
          for (let x = 0; x < maskWidth; x++) {
            const idx = (row + x) * 4;
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            const brightness = (r + g + b) / 3;
            if (brightness <= MASK_THRESHOLD) {
              if (x < minX) minX = x;
              if (y < minY) minY = y;
              if (x > maxX) maxX = x;
              if (y > maxY) maxY = y;
              sumX += x; sumY += y; count++;
            }
          }
        }
        if (count > 0) {
          const width = Math.max(1, maxX - minX + 1);
          const height = Math.max(1, maxY - minY + 1);
          const cx = sumX / count;
          const cy = sumY / count;
          darkBounds = { minX, minY, maxX, maxY, width, height, cx, cy };
        } else {
          darkBounds = { minX: 0, minY: 0, maxX: maskWidth, maxY: maskHeight, width: maskWidth, height: maskHeight, cx: maskWidth/2, cy: maskHeight/2 };
        }
        maskReady = true;
        // Establish how the mask maps into the current container
        computeMaskFit();
        console.log(`🪄 Mask loaded: ${maskWidth}x${maskHeight}`);
        resolve();
      };
      img.onerror = (e) => reject(e);
      img.src = url;
    });
  }

  // Check inclusion against the mask using canvas-space coordinates
  function isInsideMaskCanvas(x, y) {
    if (!maskReady) return true;
    const mx = (x - maskFit.offsetX) / maskFit.scale;
    const my = (y - maskFit.offsetY) / maskFit.scale;
    const px = Math.round(mx);
    const py = Math.round(my);
    if (px < 0 || py < 0 || px >= maskWidth || py >= maskHeight) return false;
    const idx = (py * maskWidth + px) * 4;
    const r = maskImgData.data[idx];
    const g = maskImgData.data[idx + 1];
    const b = maskImgData.data[idx + 2];
    const brightness = (r + g + b) / 3;
    return brightness <= MASK_THRESHOLD;
  }

  function destroy() {
    running = false;
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    window.removeEventListener("resize", resize);
    if (containerEl && canvas && containerEl.contains(canvas)) {
      containerEl.removeChild(canvas);
    }
    canvas = null;
    ctx = null;
    letters = [];
    containerEl = null;
  }

  // ============================
  //  Canvas Setup
  // ============================
  function resize() {
    if (!containerEl) return;
    
    const rect = containerEl.getBoundingClientRect();
    width = rect.width;
    height = rect.height;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";

    ctx.scale(dpr, dpr);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    console.log(`🐝 Canvas resizing to ${width}x${height}px (DPR: ${dpr})`);
    if (maskReady) {
      computeMaskFit();
    }
  }

  // ============================
  //  Build Dancing Letter Swarm - Hive/Mouth Spread
  // ============================
  function buildLetterSwarm(letterCount, cfg) {
    letters = [];

    // Parameters for wave shape
    const radiusX = 1.25;      // widen horizontally
    const radiusY = 0.75;      // taller for wave feel
    const outwardBias = 0.55;  // <1 moves more particles outward (0.5 uniform, <0.5 stronger ring)

    for (let i = 0; i < letterCount; i++) {
      // Sample until inside mask (if available)
      let x = 0, y = 0;
      for (let tries = 0; tries < 50; tries++) {
        const angle = Math.random() * Math.PI * 2;
        const r = Math.pow(Math.random(), outwardBias);
        const tx = Math.cos(angle) * radiusX * r;
        const ty = Math.sin(angle) * radiusY * r;
        // Map sample to canvas and ensure it's within the dark mask area when mask is ready
        const candX = (darkBoundsCanvas.cx || width * 0.5) + tx * shapeScale;
        const candY = (darkBoundsCanvas.cy || height * 0.5) + ty * shapeScale;
        if (!maskReady || isInsideMaskCanvas(candX, candY)) { x = tx; y = ty; break; }
      }

      // Mild hex/banded perturbation for organic hive feel
      // mild hive wobble (skip if mask enforces strict boundary)
      if (!maskReady) {
        const wobA = Math.sin(x * 6 + y * 4) * 0.05;
        const wobB = Math.cos(x * 5 - y * 3) * 0.04;
        x += wobA * (1 - Math.min(1, Math.sqrt(x*x + y*y)));
        y += wobB * (1 - Math.min(1, Math.sqrt(x*x + y*y)));
      }

      // Scatter noise
      x += (Math.random() - 0.5) * 0.12;
      y += (Math.random() - 0.5) * 0.10;

      // Size variation for particles
      const size = cfg.baseSize - 1 + Math.random() * 2.2;
      
      // Calculate distance from center for tapering effect (0 at center, 1 at edge)
      const distFromCenter = Math.sqrt(x*x + y*y) / Math.max(radiusX, radiusY);
      const taperFactor = 1 - Math.pow(distFromCenter, 1.8); // Taper more aggressively at edges

      const color = cfg.palette[Math.floor(Math.random() * cfg.palette.length)];

      const letter = {
        // Base position: wave shape
        baseX: x,
        baseY: y,
        // Current position with slight random offset
        x: x + (Math.random() - 0.5) * 0.5,
        y: y + (Math.random() - 0.5) * 0.5,
        vx: (Math.random() - 0.5) * 0.05,
        vy: (Math.random() - 0.5) * 0.05,
        size,
        color,
        // Procedural noise for wandering
        noisePhase: Math.random() * Math.PI * 2,
        noiseSpeed: 0.5 + Math.random() * 1.5,
        // Taper and animation delay from center
        taperFactor: taperFactor,
        distFromCenter: distFromCenter,
        animDelay: distFromCenter * 0.15 // Delay animation based on distance from center
      };

      letters.push(letter);
    }

      // --- Separation relaxation to reduce overlaps (simple O(n^2) passes) ---
      const passes = 3;
      const minDist = 14; // minimal separation in canvas units (pre-scale)
      for (let p = 0; p < passes; p++) {
        for (let i = 0; i < letters.length; i++) {
          for (let j = i + 1; j < letters.length; j++) {
            const a = letters[i];
            const b = letters[j];
            const dx = a.baseX - b.baseX;
            const dy = a.baseY - b.baseY;
            const d = Math.sqrt(dx * dx + dy * dy);
            if (d > 0 && d < minDist / 100) { // divide because base coords are small (~1 range)
              const push = (minDist / 100 - d) * 0.5;
              const nx = dx / d;
              const ny = dy / d;
              a.baseX += nx * push;
              a.baseY += ny * push;
              b.baseX -= nx * push;
              b.baseY -= ny * push;
            }
          }
        }
      }

    console.log(`🐝 Built ${letters.length} particle dots forming wave shape with center-out animation and edge tapering`);
  }

  // ============================
  //  Announcer Events → Amplitude
  // ============================
  function setupSpeechEvents() {
    console.log('🎙️ Setting up speech event listeners');
    
    const onSpeechStart = () => {
      console.log('✅ quiz-speech-start fired');
      isSpeaking = true;
      pulsePhase = 0; // reset pulse on speech start
      lastBoundaryTime = performance.now();
      boundaryBoost = 1; // initial strong pulse
      // pick initial speaking state (medium open)
      targetState = 2;
    };

    const onSpeechEnd = () => {
      console.log('✅ quiz-speech-end fired');
      isSpeaking = false;
      pulsePhase = 0; // stop pulsing
      boundaryBoost = 0; // remove boost
      // go to closed
      targetState = 0;
    };

    const onSpeechBoundary = () => {
      console.log('✅ quiz-speech-boundary fired');
      lastBoundaryTime = performance.now(); // mark boundary for rhythm sync
      pulsePhase = 0; // restart pulse on each boundary
      boundaryBoost = 1; // spike on each boundary for visible pulse
      // cycle between speaking states 1→2→3→2 for natural variation
      if (!isSpeaking) return;
      if (targetState === 1) targetState = 2;
      else if (targetState === 2) targetState = 3;
      else if (targetState === 3) targetState = 2;
      else targetState = 2;
    };

    // Listen on both document and window (dispatch site varies)
    [document, window].forEach(src => {
      src.addEventListener("quiz-speech-start", onSpeechStart);
      src.addEventListener("quiz-speech-end", onSpeechEnd);
      src.addEventListener("quiz-speech-boundary", onSpeechBoundary);
    });
    
    console.log('🎙️ Speech event listeners registered');
  }

  // ============================
  //  Animation Step
  // ============================
  function step(time, cfg) {
    if (!running || !ctx) return;

    rafId = requestAnimationFrame((t) => step(t, cfg));

    // Update amplitude based on speech state
    // Fallback: poll speechSynthesis if events failed
    if (typeof speechSynthesis !== 'undefined') {
      const speakingNow = speechSynthesis.speaking;
      // If synthesis is speaking but we never got a start event, activate fallback
      if (speakingNow && !isSpeaking) {
        isSpeaking = true;
        boundaryBoost = Math.max(boundaryBoost, 0.8);
        // throttle logging
        if (!window.__beeFallbackLog || time - window.__beeFallbackLog > 2000) {
          window.__beeFallbackLog = time;
          console.log('[BeeSwarm] ⚠️ Fallback speech detection engaged (speechSynthesis.speaking)');
        }
      } else if (!speakingNow && isSpeaking && boundaryBoost < 0.05) {
        // if speech truly ended and boost decayed, mark silent
        isSpeaking = false;
      }
    }
    if (isSpeaking) {
      amplitude = Math.min(1, amplitude + 0.10);
    } else {
      amplitude = Math.max(0, amplitude - 0.05);
    }

    // Boundary boost decays quickly to create word pulses
    boundaryBoost *= 0.78; // fast decay so each boundary is a distinct blip
    const effectiveAmp = Math.min(1, amplitude * 0.6 + boundaryBoost * 0.9); // combine base speech + pulses
    ampSmooth = ampSmooth * 0.75 + effectiveAmp * 0.25; // slightly more responsive

    // Diagnostic logging (throttled ~1/sec)
    // (Diagnostics removed after verification)
    // if (!window.__beePulseLog || time - window.__beePulseLog > 1000) {
    //   window.__beePulseLog = time;
    //   console.log('[BeeSwarm] amp', amplitude.toFixed(2), 'boost', boundaryBoost.toFixed(2), 'eff', effectiveAmp.toFixed(2), 'smooth', ampSmooth.toFixed(2));
    // }

    // Progress shape interpolation toward target mouth state
    stateLerp = Math.min(1, stateLerp + (isSpeaking ? 0.08 : 0.12));

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const tSec = time * 0.001;
    // Apply requested center offsets so swarm aligns with mask center
    // Center on dark region of the mask (mapped to canvas); allow user offsets
    const centerX = (darkBoundsCanvas.cx || width * 0.5) + (cfg.centerOffsetX || 0) * width;
    const centerY = (darkBoundsCanvas.cy || height * 0.5) + (cfg.centerOffsetY || 0) * height;
    // Use shapeScale derived from dark bounds so swarm stays confined
    const scale = maskReady ? shapeScale : Math.max(width, height) * 0.33;

    // ===================================
    // Speech rhythm-synced pulse effect
    // ===================================
    // When NOT speaking: pulse stops completely (0)
    // When speaking: pulse at 4.5 Hz rhythm, resets on each speech boundary
    let voicePulse = 0;
    if (isSpeaking) {
      // Rhythm based on repeated boundaries; speed slightly modulated by current amplitude
      pulsePhase += 0.025 + ampSmooth * 0.03; // 2.5–5.5 Hz
      const basePulse = Math.sin(pulsePhase * Math.PI * 2) * 0.5 + 0.5;
      // Blend with boundaryBoost for sharper peaks
      voicePulse = Math.min(1, basePulse * 0.55 + boundaryBoost * 1.0);
    } else {
      voicePulse = 0;
      pulsePhase = 0;
    }
    
    const voiceFreq = isSpeaking ? Math.sin(tSec * 2.2) * Math.sin(tSec * 3.7) : 0;

    // Compute current mouth parameters via lerp between current and target states
    const cur = MOUTH_STATES[mouthState];
    const tgt = MOUTH_STATES[targetState];
    const rx = cur.rx + (tgt.rx - cur.rx) * stateLerp;
    const ry = cur.ry + (tgt.ry - cur.ry) * stateLerp;
    const gap = cur.gap + (tgt.gap - cur.gap) * stateLerp; // vertical lip separation
    const tilt = cur.tilt + (tgt.tilt - cur.tilt) * stateLerp; // slight rotation

    // Commit when reached
    if (stateLerp >= 1) {
      mouthState = targetState;
      stateLerp = 0;
    }

    // Draw each letter
    for (let i = 0; i < letters.length; i++) {
      const letter = letters[i];

      // Update noise phase for wandering
      letter.noisePhase += letter.noiseSpeed * 0.01;

      // Procedural noise for wandering movement (Perlin-like)
      const noiseX = Math.sin(letter.noisePhase) * Math.cos(letter.noisePhase * 0.7);
      const noiseY = Math.cos(letter.noisePhase * 1.3) * Math.sin(letter.noisePhase * 0.5);
      
      // Attraction to base position + noise wandering
      // Compute mouth shape position from base polar approximation
      // Re-map base coords to oval with upper/lower lip separation using 'gap'
      const bx = letter.baseX * rx;
      const by = letter.baseY * ry;
      // Apply tilt (rotation around origin)
      const cosT = Math.cos(tilt);
      const sinT = Math.sin(tilt);
      const tx0 = bx * cosT - by * sinT;
      const ty0 = bx * sinT + by * cosT;
      // Separate lips: push points above/below midline apart by 'gap'
      const lipY = ty0 + (ty0 >= 0 ? gap : -gap);

      let targetX = tx0 * scale + noiseX * cfg.baseNoise * 40;
      let targetY = lipY * scale + noiseY * cfg.baseNoise * 28;

      // If mask is present, clamp target back inside mask edge using canvas-space checks
      if (maskReady && !isInsideMaskCanvas(targetX, targetY)) {
        const bxc = centerX + tx0 * scale;
        const byc = centerY + lipY * scale;
        let px = targetX, py = targetY;
        for (let k = 0; k < 8; k++) {
          px = (px + bxc) * 0.5;
          py = (py + byc) * 0.5;
          if (isInsideMaskCanvas(px, py)) break;
        }
        targetX = px;
        targetY = py;
      }

      // When speaking: add extra jitter and slight expansion
      const jitterScale = 1 + ampSmooth * 0.3;
      const jitterX = Math.sin(tSec * 4 + i) * ampSmooth * 20;
      const jitterY = Math.cos(tSec * 3 + i * 0.5) * ampSmooth * 15;

      // NOTE: targetX/Y are already in canvas coordinates relative to center; don't add center again
      const finalTargetX = (targetX + jitterX) * jitterScale;
      const finalTargetY = (targetY + jitterY) * jitterScale;

      // Physics: attraction + velocity
      const dx = finalTargetX - letter.x;
      const dy = finalTargetY - letter.y;

      letter.vx += dx * cfg.attractStrength;
      letter.vy += dy * cfg.attractStrength;

      // Add some randomness to velocity
      letter.vx += (Math.random() - 0.5) * 0.03 * cfg.baseNoise;
      letter.vy += (Math.random() - 0.5) * 0.03 * cfg.baseNoise;

      // Apply damping
      letter.vx *= cfg.damp;
      letter.vy *= cfg.damp;

      // Update position
      letter.x += letter.vx;
      letter.y += letter.vy;

      // Global swarm breathing expansion based on voicePulse (reduced for discrete states)
      const swarmExpand = 1 + voicePulse * ampSmooth * 0.18;
      letter.x = centerX + (letter.x - centerX) * swarmExpand;
      letter.y = centerY + (letter.y - centerY) * swarmExpand;

      // Pulsing size: stronger factor for visibility
      const sizePulse = 1 + ampSmooth * 0.40 * voicePulse; // slightly calmer
      const fontSize = letter.size * sizePulse;

      // Pulsing opacity (increase range for clarity)
      const opacityPulse = 0.45 + ampSmooth * 0.55 * voicePulse;
      const alpha = opacityPulse;

      // Draw tiny alphabet letter
      // Final mask guard: skip drawing if outside the dark region
      if (maskReady && !isInsideMaskCanvas(letter.x, letter.y)) {
        continue;
      }

      // Edge taper: fade and shrink letters near mask border to avoid hard clipping
      let taperAlpha = 1.0;
      let taperSizeMul = 1.0;
      if (maskReady) {
        const dist = distanceToMaskBorder(letter.x, letter.y);
        const band = 14; // pixels inside border to start tapering
        if (dist < band) {
          const t = Math.max(0, dist) / band; // 0 at edge, 1 further inside
          taperAlpha = 0.3 + 0.7 * t;         // fade near edge
          taperSizeMul = 0.65 + 0.35 * t;     // shrink near edge
        }
      }

      // Apply taper factor to size and opacity based on distance from center
      const taperedSize = fontSize * taperSizeMul * letter.taperFactor;
      const taperedAlpha = alpha * taperAlpha * letter.taperFactor;
      
      // Center-out animation: particles near center animate first
      const animPhase = Math.max(0, Math.min(1, (tSec * 2 - letter.animDelay)));
      const centerOutAlpha = taperedAlpha * animPhase;
      
      // Draw as glowing dot/particle instead of letter
      const dotRadius = Math.max(1.5, taperedSize * 0.4);
      
      ctx.globalAlpha = Math.max(0, Math.min(1, centerOutAlpha));
      
      // Outer glow for particles when speaking
      if (ampSmooth > 0.15) {
        // Convert hex color to rgba for gradient
        const hexToRgba = (hex, alpha) => {
          const r = parseInt(hex.slice(1, 3), 16);
          const g = parseInt(hex.slice(3, 5), 16);
          const b = parseInt(hex.slice(5, 7), 16);
          return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };
        
        const gradient = ctx.createRadialGradient(letter.x, letter.y, 0, letter.x, letter.y, dotRadius * 2.5);
        gradient.addColorStop(0, letter.color);
        gradient.addColorStop(0.4, hexToRgba(letter.color, 0.4));
        gradient.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(letter.x, letter.y, dotRadius * 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
      
      // Main dot particle
      ctx.fillStyle = letter.color;
      ctx.beginPath();
      ctx.arc(letter.x, letter.y, dotRadius, 0, Math.PI * 2);
      ctx.fill()
    }

    ctx.globalAlpha = 1.0; // reset
  }

})(window);

// Helper: approximate distance to nearest mask border in canvas pixels
function distanceToMaskBorder(x, y) {
  // Uses the isInsideMaskCanvas function bound in closure via window accessor
  try {
    const maxStep = 18;
    const dirs = [
      [1,0],[-1,0],[0,1],[0,-1],
      [0.707,0.707],[-0.707,0.707],[0.707,-0.707],[-0.707,-0.707]
    ];
    for (let step=0; step<=maxStep; step++) {
      for (let i=0;i<dirs.length;i++) {
        const nx = x + dirs[i][0]*step;
        const ny = y + dirs[i][1]*step;
        // Call through to the module-scoped function via window
        if (window && window.BeeSwarmCanvas && typeof window.isInsideMaskCanvas === 'function') {
          if (!window.isInsideMaskCanvas(nx, ny)) return step;
        }
      }
    }
    return maxStep;
  } catch(e) {
    return 18;
  }
}
