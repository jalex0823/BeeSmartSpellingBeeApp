/**
 * BeeSmart Honey Loader - Ultra-Safe Edition
 * 
 * Key Features:
 * - Micro-task slicing: yields after every step with requestAnimationFrame
 * - Progress moves BEFORE network calls (UI stays responsive)
 * - Hard 1400ms timeouts on all fetches with AbortController
 * - CSS-driven matrix animation (can't be blocked by JS)
 * - Dedupe guard prevents double execution
 * - Events dispatched for downstream components
 * 
 * This version prevents Safari "page not responding" by never blocking the main thread.
 */
(function () {
  // prevent double load
  if (window.beeSmartLoaderBooted) {
    console.log("[loader] Already booted - skipping duplicate load");
    return;
  }
  window.beeSmartLoaderBooted = true;

  const percentEl   = document.getElementById("loader-percent");
  const statusEl    = document.getElementById("loader-status");
  const subStatusEl = document.getElementById("loader-substatus");

  let uiProgress = 0;
  let targetProgress = 0;

  // smooth % updater - runs independently on timer
  const pctTimer = setInterval(() => {
    uiProgress += (targetProgress - uiProgress) * 0.35;
    const shown = Math.floor(uiProgress);
    if (percentEl) percentEl.textContent = shown + "%";
  }, 110);

  /**
   * SAFE fetch with AbortController timeout
   * Returns null if fetch fails or times out
   */
  async function fetchWithTimeout(url, ms = 1400, opts = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ms);
    try {
      const res = await fetch(url, { ...opts, signal: controller.signal });
      clearTimeout(timer);
      return res;
    } catch (err) {
      clearTimeout(timer);
      console.warn(`[loader] fetch failed: ${url}`, err.name);
      return null;
    }
  }

  /**
   * Yield back to browser - lets animations/paint run
   */
  function nextFrame() {
    return new Promise(res => requestAnimationFrame(() => res()));
  }

  /**
   * Steps to run - each yields before and after execution
   */
  const steps = [
    {
      label: "Loading Avatars…",
      weight: 30,
      task: async () => {
        const res = await fetchWithTimeout("/api/avatars/light", 1400);
        if (!res || !res.ok) {
          console.warn("[loader] avatar light failed");
          if (subStatusEl) subStatusEl.textContent = "Avatars: fallback mode";
          return;
        }
        const data = await res.json().catch(() => null);
        document.dispatchEvent(new CustomEvent("BeeSmart:avatarsReady", { detail: { avatars: data } }));
        if (subStatusEl) subStatusEl.textContent = "Avatars ready ✓";
      }
    },
    {
      label: "Loading Quizzes…",
      weight: 40,
      task: async () => {
        const res = await fetchWithTimeout("/api/quizzes/light", 1400);
        if (!res || !res.ok) {
          console.warn("[loader] quizzes failed");
          if (subStatusEl) subStatusEl.textContent = "Quizzes: fallback mode";
          return;
        }
        const data = await res.json().catch(() => null);
        document.dispatchEvent(new CustomEvent("BeeSmart:quizzesReady", { detail: { quizzes: data } }));
        if (subStatusEl) subStatusEl.textContent = "Quizzes ready ✓";
      }
    },
    {
      label: "Loading Analytics…",
      weight: 30,
      task: async () => {
        const res = await fetchWithTimeout("/api/analytics/ping", 1400);
        if (!res || !res.ok) {
          console.warn("[loader] analytics failed");
          if (subStatusEl) subStatusEl.textContent = "Analytics: offline";
          return;
        }
        document.dispatchEvent(new Event("BeeSmart:analyticsReady"));
        if (subStatusEl) subStatusEl.textContent = "Analytics enabled ✓";
      }
    }
  ];

  /**
   * Run after initial render so Safari paints first
   */
  requestAnimationFrame(() => {
    runSteps();
  });

  async function runSteps() {
    for (const step of steps) {
      if (statusEl) statusEl.textContent = step.label;

      // MOVE percent right away so UI is snappy (even if network stalls)
      targetProgress += step.weight;

      // yield so animation / CSS can run
      await nextFrame();

      // run the actual network task, but even if it stalls, we've already moved %
      try {
        await step.task();
      } catch (err) {
        console.warn("[loader] step crashed", step.label, err);
      }

      // yield again after task completes
      await nextFrame();
    }

    // finish
    targetProgress = 100;
    if (statusEl) statusEl.textContent = "System check complete ✔";
    if (subStatusEl) subStatusEl.textContent = "Launching BeeSmart…";

    document.dispatchEvent(new Event("BeeSmart:loaderComplete"));

    // let user see 100% for a moment
    setTimeout(() => {
      // hand off to your app here
      if (window.BeeSmartApp && typeof window.BeeSmartApp.start === "function") {
        window.BeeSmartApp.start();
      } else {
        console.log("[loader] No BeeSmartApp.start() found - loader complete");
        // Optionally redirect: window.location.href = "/app";
      }
      clearInterval(pctTimer);
      
      // Hide loader overlay if it exists
      const loaderRoot = document.getElementById("loader-root");
      if (loaderRoot) {
        loaderRoot.style.transition = "opacity 0.5s ease-out";
        loaderRoot.style.opacity = "0";
        setTimeout(() => {
          loaderRoot.style.display = "none";
        }, 500);
      }
    }, 500);
  }
})();
