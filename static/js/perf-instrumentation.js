// perf-instrumentation.js
// Lightweight client-side performance logging without blocking rendering.
(function(){
  const perf = window.performance;
  function stamp(label, extra){
    const t = Math.round(perf.now());
    if (extra !== undefined) {
      console.log('[perf]', label, t+'ms', extra);
    } else {
      console.log('[perf]', label, t+'ms');
    }
  }
  // DOM readiness
  window.addEventListener('DOMContentLoaded', ()=> stamp('domContentLoaded'));
  window.addEventListener('load', ()=> stamp('windowLoad'));
  // Largest Contentful Paint
  try {
    new PerformanceObserver(list => {
      const entries = list.getEntries();
      const last = entries[entries.length - 1];
      stamp('LCP', 'node='+ (last.element ? last.element.tagName : 'n/a'));
    }).observe({type:'largest-contentful-paint', buffered:true});
  } catch(e){}
  // First Input Delay
  try {
    new PerformanceObserver(list => {
      const first = list.getEntries()[0];
      if(first) {
        const fid = Math.round(first.processingStart - first.startTime);
        console.log('[perf] FID', fid+'ms');
      }
    }).observe({type:'first-input', buffered:true});
  } catch(e){}
  // Layout shifts (CLS accumulation)
  let cls = 0;
  try {
    new PerformanceObserver(list => {
      list.getEntries().forEach(entry => {
        if(!entry.hadRecentInput) cls += entry.value;
        stamp('CLS_update', 'total='+cls.toFixed(3));
      });
    }).observe({type:'layout-shift', buffered:true});
  } catch(e){}
  // Asset timing (optional quick sample of largest JS)
  window.addEventListener('load', ()=> {
    (perf.getEntriesByType('resource')||[]).filter(r=>r.initiatorType==='script').sort((a,b)=>b.transferSize-a.transferSize).slice(0,3).forEach(r=>{
      console.log('[perf] scriptTop', r.name, 'transferSize='+r.transferSize);
    });
  });
})();
