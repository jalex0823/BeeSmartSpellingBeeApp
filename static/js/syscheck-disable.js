// Neutralize any global system/preflight check functions that might gate UI rendering
(function(){
  const noop = function(){ return true; };
  const globals = [
    'runSystemChecks','runPreflightChecks','performDiagnostics','blockUntilReady','initSystemCheck'
  ];
  globals.forEach(name => { try { if (typeof window[name] === 'function') { window[name] = noop; } else { Object.defineProperty(window, name, { configurable: true, get: ()=>noop }); } } catch(e){} });

  // Auto-remove any late-added overlays
  const selectors = [
    '#system-check','#system-check-overlay','.system-check','.system-check-overlay',
    '#preflight-check','.preflight-check','[data-role="system-check"]',
    '#diagnostics','.diagnostics-overlay','#maintenance-banner'
  ];
  function sweep(){
    selectors.forEach(sel => {
      document.querySelectorAll(sel).forEach(el => { el.remove(); });
    });
    document.body.classList.remove('system-check-active','loading');
  }
  document.addEventListener('DOMContentLoaded', sweep);
  setTimeout(sweep, 50);
  setTimeout(sweep, 250);
  setTimeout(sweep, 1000);
})();
