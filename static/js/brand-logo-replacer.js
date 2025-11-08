/* Brand Logo Replacer (Reintroduced)
 * Ensures any legacy logo assets are swapped to the unified crest.
 * If window.BeeSmartBrand.logoPath is set, uses that; otherwise falls back to BeeSmartCrestLogo1.png.
 */
(function(){
  const FALLBACK = '/static/images/LogoBee&WordingTM.png';
  const TARGET = (window.BeeSmartBrand && window.BeeSmartBrand.logoPath) || '/static/images/LogoBee&WordingTM.png';
  const LEGACY_PATTERNS = [
    /BeeSmartLogo(?:2)?\.(png|jpg|svg)/i,
    /BeeSmartTitle\.(png|jpg|svg)/i,
    /LogoBee.*\.(png|jpg|svg)/i,
    /LogoBanner\.(png|jpg|svg)/i,
    /AppIconLogo.*\.(png|jpg|svg)/i,
    /BeeSmartCrestLogo.*\.(png|jpg|svg)/i,
    /BeeSmartLogoTransparent\.(png|jpg|svg)/i,
    /BeeSmartBee\.(png|jpg|svg)/i
  ];

  function matchesLegacy(src){
    if(!src) return false; return LEGACY_PATTERNS.some(r=> r.test(src));
  }

  function swapImages(){
    document.querySelectorAll('img').forEach(img=>{
      const src = img.getAttribute('src');
      if(matchesLegacy(src)){
        img.setAttribute('data-old-src', src);
        img.src = TARGET;
        if(!img.alt || !/logo/i.test(img.alt)) img.alt = 'BeeSmart Logo';
      }
      // Handle srcset as well
      const srcset = img.getAttribute('srcset');
      if (matchesLegacy(srcset)) {
        img.setAttribute('data-old-srcset', srcset);
        img.setAttribute('srcset', TARGET);
      }
    });

    // <picture><source> tags
    document.querySelectorAll('source[srcset]').forEach(source => {
      const ss = source.getAttribute('srcset');
      if (matchesLegacy(ss)) {
        source.setAttribute('data-old-srcset', ss);
        source.setAttribute('srcset', TARGET);
      }
    });
  }

  function swapFavicons(){
    document.querySelectorAll('link[rel*="icon"], link[rel="apple-touch-icon"]').forEach(link=>{
      if(matchesLegacy(link.href)){
        link.setAttribute('data-old-href', link.href);
        link.href = TARGET;
      }
    });
  }

  function swapBackgrounds(){
    // Inline background-image styles only (avoid touching stylesheets)
    document.querySelectorAll('[style*="background"]').forEach(el => {
      const style = el.getAttribute('style') || '';
      if (matchesLegacy(style)) {
        el.setAttribute('data-old-bg', style);
        // Replace any url(...) occurrences that match legacy with TARGET
        const updated = style.replace(/url\(([^)]+)\)/gi, (m, p1) => {
          return matchesLegacy(p1) ? `url(${TARGET})` : m;
        });
        el.setAttribute('style', updated);
      }
    });
  }

  function run(){ swapImages(); swapFavicons(); swapBackgrounds(); }

  // Ensure the crest target actually exists; if not, switch to fallback immediately
  function verifyTargetThenRun(){
    try {
      const tester = new Image();
      tester.onload = function(){ run(); installObserver(); };
      tester.onerror = function(){ try { if (window.BeeSmartBrand) window.BeeSmartBrand.logoPath = FALLBACK; } catch(_){}
        run(); installObserver(); };
      tester.src = TARGET;
    } catch(_){ run(); installObserver(); }
  }

  function installObserver(){
    try {
      const obs = new MutationObserver((mutations)=>{
        let shouldRun = false;
        for (const m of mutations) {
          if (m.type === 'attributes') {
            const name = m.attributeName || '';
            if (name === 'src' || name === 'srcset' || name === 'style' || name === 'href') {
              shouldRun = true; break;
            }
          }
          if (m.type === 'childList' && (m.addedNodes && m.addedNodes.length)) { shouldRun = true; break; }
        }
        if (shouldRun) run();
      });
      obs.observe(document.documentElement || document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['src','srcset','style','href'] });
    } catch(_) {}
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ verifyTargetThenRun(); });
  } else { verifyTargetThenRun(); }
})();