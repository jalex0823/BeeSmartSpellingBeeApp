/* Brand Logo Replacer (Reintroduced)
 * Ensures any legacy logo assets are swapped to the unified crest.
 * If window.BeeSmartBrand.logoPath is set, uses that; otherwise falls back to BeeSmartCrestLogo1.png.
 */
(function(){
  const TARGET = (window.BeeSmartBrand && window.BeeSmartBrand.logoPath) || '/static/images/BeeSmartCrestLogo1.png';
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

  function run(){ swapImages(); swapFavicons(); }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', run);
  } else { run(); }
})();