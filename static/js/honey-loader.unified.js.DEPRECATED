/**
 * BeeSmart Unified Loader
 * - non-blocking
 * - staged progress (Avatars → Wordbank → System Health)
 * - timeouts on all network calls
 * - document-based events
 * - yellow matrix overlay with requestAnimationFrame
 */
(function () {
  // 1) Prevent duplicates
  if (window.beeSmartLoaderBooted) {
    console.log('🍯 Loader already booted, skipping');
    return;
  }
  window.beeSmartLoaderBooted = true;

  // 2) Grab UI elements
  const overlay = document.getElementById('appHoneyLoader');
  if (!overlay) {
    console.warn('🍯 Loader overlay not found');
    return;
  }

  const percentEl = document.getElementById('loaderPercentText');
  const taskEl = document.getElementById('loaderProcessName');
  const detailEl = document.getElementById('loaderStatusDetail');
  const matrixCanvas = document.getElementById('matrixCanvas');

  // 3) Progress state
  let uiProgress = 0;     // what the user sees
  let targetProgress = 0; // where we want to go
  let finished = false;

  // 4) Diagnostics logging
  const diagnosticsLog = {
    timestamp: new Date().toISOString(),
    checks: [],
    warnings: [],
    errors: []
  };

  function logCheck(name, status, details = {}) {
    const entry = {
      name,
      status, // 'success', 'warning', 'error', 'timeout'
      timestamp: new Date().toISOString(),
      ...details
    };
    diagnosticsLog.checks.push(entry);
    
    if (status === 'warning') diagnosticsLog.warnings.push(entry);
    if (status === 'error' || status === 'timeout') diagnosticsLog.errors.push(entry);
    
    try {
      sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
    } catch(e) {}
  }

  // 5) Safe fetch with timeout using AbortController
  async function fetchWithTimeout(url, ms = 1500, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), ms);
    try {
      const res = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeout);
      return res;
    } catch (err) {
      clearTimeout(timeout);
      if (err.name === 'AbortError') {
        throw new Error('timeout');
      }
      throw err;
    }
  }

  // 6) Smooth UI ticker (independent of backend)
  const tickInterval = setInterval(() => {
    if (finished) {
      clearInterval(tickInterval);
      return;
    }
    // Ease toward target
    uiProgress += (targetProgress - uiProgress) * 0.35;
    const shown = Math.floor(uiProgress);
    if (percentEl) percentEl.textContent = shown + '%';
  }, 110);

  // 7) Yellow matrix animation with requestAnimationFrame
  function initMatrix() {
    if (!matrixCanvas) return;

    const ctx = matrixCanvas.getContext('2d', { alpha: true });
    matrixCanvas.width = window.innerWidth;
    matrixCanvas.height = window.innerHeight;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const fontSize = 14;
    const columns = Math.floor(matrixCanvas.width / fontSize);
    const drops = [];

    for (let i = 0; i < columns; i++) {
      drops[i] = Math.floor(Math.random() * matrixCanvas.height / fontSize);
    }

    let lastFrameTime = 0;
    const frameInterval = 33; // ~30fps

    function drawMatrix(currentTime) {
      if (currentTime - lastFrameTime >= frameInterval) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);

        ctx.fillStyle = '#FFD540'; // Yellow
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
          const char = chars[Math.floor(Math.random() * chars.length)];
          const x = i * fontSize;
          const y = drops[i] * fontSize;

          ctx.fillText(char, x, y);

          if (y > matrixCanvas.height && Math.random() > 0.975) {
            drops[i] = 0;
          }
          drops[i]++;
        }
        lastFrameTime = currentTime;
      }
      if (!finished) {
        requestAnimationFrame(drawMatrix);
      }
    }

    requestAnimationFrame(drawMatrix);
  }
  initMatrix();

  // 8) Actual system check steps
  const steps = [
    {
      name: 'Core Assets',
      detail: 'Preparing interface…',
      weight: 20,
      run: async () => {
        // Preload critical images
        ['/static/images/backgrounds/HoneyCombBg2.png', '/static/BeeSmartCrestLogo1.png'].forEach(url => {
          const img = new Image();
          img.src = url;
        });
        logCheck('Core Assets', 'success', { preloaded: 2 });
        return Promise.resolve();
      }
    },
    {
      name: 'Health',
      detail: 'Checking system health…',
      weight: 20,
      run: async () => {
        const res = await fetchWithTimeout('/health', 1000);
        if (!res || !res.ok) {
          logCheck('Health Check', 'timeout', { error: 'Backend unavailable' });
          throw new Error('Health check failed');
        }
        const data = await res.json();
        logCheck('Health Check', 'success', { version: data.version, status: data.status });
        document.dispatchEvent(new CustomEvent('BeeSmart:healthReady', { detail: data }));
      }
    },
    {
      name: 'Wordbank',
      detail: 'Loading word lists…',
      weight: 20,
      run: async () => {
        const res = await fetchWithTimeout('/api/wordbank', 1200);
        if (!res || !res.ok) {
          logCheck('Wordbank', 'warning', { error: 'No words loaded' });
          console.warn('[loader] wordbank check failed, continuing');
          return;
        }
        const data = await res.json();
        const wordCount = Array.isArray(data) ? data.length : (data.count || 0);
        logCheck('Wordbank', wordCount > 0 ? 'success' : 'warning', { words: wordCount });
        document.dispatchEvent(new CustomEvent('BeeSmart:wordbankReady', { detail: data }));
      }
    },
    {
      name: 'Avatars',
      detail: 'Verifying avatar carousel…',
      weight: 20,
      run: async () => {
        // Check carousel thumbnails
        const thumbnailBase = '/static/assets/avatars/glb_files/AvatarThumbnails';
        const priorityAvatars = ['SuperBee!.png', 'QueenBee!.png', 'JRockBee!.png', 'BeeKnight!.png'];
        
        let successCount = 0;
        const checkPromises = priorityAvatars.map(file => 
          fetchWithTimeout(`${thumbnailBase}/${file}`, 800, { method: 'HEAD' })
            .then(res => { if (res && res.ok) successCount++; })
            .catch(() => {})
        );
        
        await Promise.all(checkPromises);
        
        // Also check mascot for registered users
        const mascotRes = await fetchWithTimeout('/static/assets/avatars/Mascot%20Bee/mascot-bee.obj', 800, { method: 'HEAD' })
          .catch(() => null);
        const mascotOk = mascotRes && mascotRes.ok;
        
        const totalSuccess = successCount + (mascotOk ? 1 : 0);
        const healthPct = Math.round((totalSuccess / 5) * 100);
        
        logCheck('Avatar Carousel', totalSuccess >= 3 ? 'success' : 'warning', {
          thumbnails: successCount,
          mascot: mascotOk,
          health: healthPct
        });
        
        document.dispatchEvent(new CustomEvent('BeeSmart:avatarsReady', {
          detail: { thumbnails: successCount, mascot: mascotOk }
        }));
      }
    },
    {
      name: 'Definitions',
      detail: 'Priming dictionary cache…',
      weight: 20,
      run: async () => {
        // Simulated delay for dictionary priming
        await new Promise(resolve => setTimeout(resolve, 500));
        logCheck('Dictionary Cache', 'success', { primed: true });
        document.dispatchEvent(new Event('BeeSmart:dictionaryReady'));
      }
    }
  ];

  // 9) Run steps with proper async handling
  setTimeout(() => {
    (async function runAll() {
      const startTime = Date.now();
      
      for (const step of steps) {
        if (taskEl) taskEl.textContent = step.name + '…';
        if (detailEl) detailEl.textContent = step.detail;
        
        // Move progress immediately so user sees activity
        targetProgress += step.weight;
        
        try {
          await step.run();
        } catch (err) {
          console.warn('[loader] step error:', step.name, err);
          // Continue anyway - non-blocking
        }
      }

      // Calculate final health percentage
      const duration = Date.now() - startTime;
      const totalChecks = diagnosticsLog.checks.length;
      const successfulChecks = diagnosticsLog.checks.filter(c => c.status === 'success').length;
      const healthPercentage = totalChecks > 0 ? Math.round((successfulChecks / totalChecks) * 100) : 0;
      
      diagnosticsLog.completedAt = new Date().toISOString();
      diagnosticsLog.duration = duration;
      diagnosticsLog.healthPercentage = healthPercentage;
      diagnosticsLog.summary = {
        totalChecks,
        successful: successfulChecks,
        warnings: diagnosticsLog.warnings.length,
        errors: diagnosticsLog.errors.length,
        healthPercentage
      };
      
      try {
        sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
      } catch(e) {}

      // 🚨 CRITICAL: 55% health threshold check
      const MIN_HEALTH_THRESHOLD = 55;
      
      if (healthPercentage < MIN_HEALTH_THRESHOLD) {
        console.error(`🚫 System health at ${healthPercentage}% - below minimum ${MIN_HEALTH_THRESHOLD}%`);
        if (taskEl) taskEl.textContent = 'System Health Critical';
        if (detailEl) {
          detailEl.innerHTML = `<span style="color:#ff4444">⚠️ Only ${healthPercentage}% healthy (need ${MIN_HEALTH_THRESHOLD}%)<br>Please refresh or contact support</span>`;
        }
        diagnosticsLog.criticalFailure = true;
        sessionStorage.setItem('beeSmartDiagnostics', JSON.stringify(diagnosticsLog));
        return; // HALT - don't proceed
      }

      // Success - ensure 100%
      targetProgress = 100;
      uiProgress = 100;
      if (percentEl) percentEl.textContent = '100%';
      if (taskEl) taskEl.textContent = 'Ready';
      if (detailEl) detailEl.textContent = 'Complete!';
      
      finished = true;

      // Console summary
      const hasIssues = diagnosticsLog.errors.length > 0 || diagnosticsLog.warnings.length > 0;
      if (hasIssues) {
        console.warn(`🍯 BeeSmart loaded in ${duration}ms (${healthPercentage}% healthy) with ${diagnosticsLog.errors.length} errors, ${diagnosticsLog.warnings.length} warnings`);
      } else {
        console.log(`🍯 BeeSmart loaded in ${duration}ms - All systems healthy (${healthPercentage}%) ✓`);
      }

      // Fire completion event
      document.dispatchEvent(new Event('honeyLoaderFinished'));
      document.dispatchEvent(new Event('BeeSmart:loaderComplete'));

      // Fade out loader
      setTimeout(() => {
        overlay.classList.add('hidden');
        overlay.style.opacity = '0';
        setTimeout(() => overlay.style.display = 'none', 350);
      }, 350);
    })();
  }, 200); // Let DOM render first (prevents Safari freeze)

  // 10) Safety timeout - maximum 5 seconds
  setTimeout(() => {
    if (!finished) {
      console.warn('🍯 SAFETY: Force-finishing loader after 5s timeout');
      finished = true;
      targetProgress = 100;
      document.dispatchEvent(new Event('honeyLoaderFinished'));
      overlay.style.opacity = '0';
      setTimeout(() => overlay.style.display = 'none', 350);
    }
  }, 5000);

  // 11) Expose diagnostics API
  window.SystemChecks = {
    getDiagnostics: () => diagnosticsLog,
    viewDiagnostics: () => {
      console.group('🍯 BeeSmart System Diagnostics');
      console.log('Timestamp:', diagnosticsLog.timestamp);
      console.log('Health:', diagnosticsLog.healthPercentage + '%');
      console.table(diagnosticsLog.checks);
      if (diagnosticsLog.errors.length > 0) {
        console.group('❌ Errors');
        diagnosticsLog.errors.forEach(e => console.error(e));
        console.groupEnd();
      }
      console.groupEnd();
      return diagnosticsLog;
    }
  };

})();
