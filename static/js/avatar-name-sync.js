/* BeeSmart Avatar Name ⇄ Image Sync
 * Auto-updates the displayed avatar image whenever the visible avatar name changes.
 *
 * Usage (auto): Include this script and ensure your page has:
 *  - A name element (e.g., #avatar-name or .avatar-name) whose textContent is the avatar name
 *  - An image element (e.g., #avatar-image or .avatar-image) to display the avatar
 *
 * Optional manual init:
 *   BeeSmartAvatarSync.initialize({ nameSelector:'#avatar-name', imageSelector:'#avatar-image' })
 */
(function(){
  // Simple debounce utility
  function debounce(fn, wait){
    let t; return function(...args){ clearTimeout(t); t = setTimeout(()=>fn.apply(this,args), wait); };
  }
  const DEFAULT_NAME_SELECTORS = ['#avatar-name','.avatar-name','#current-avatar-name','.podium .name','#winner-name'];
  const DEFAULT_IMAGE_SELECTORS = ['#avatar-image','.avatar-image','#current-avatar','.podium .avatar img','#winner-avatar'];

  // Some filenames in repo contain historical typos or variants
  const SPECIAL_FILENAMES = {
    RockerBee: 'RockarBee',
    RockinBee: 'RockarBee',
    NurseBee: 'NureseBee',
    MissBee2: 'MissBee2'
  };

  const EXTENSIONS = ['png','jpg','jpeg','webp'];

  function toCandidates(name){
    if(!name) return [];
    const base = (name||'').toString().trim();
    // Normalize like: "Cool Bee" => "CoolBee"
    const letters = base.replace(/[^A-Za-z0-9]/g,'');
    if(!letters) return [];
    // Also make TitleCase attempt
    const title = letters.replace(/(^|[A-Z0-9])([a-z0-9]+)/g,(m,a,b)=> a + b.charAt(0).toUpperCase()+b.slice(1));
    const direct = title;
    const specialKey = SPECIAL_FILENAMES[direct] ? SPECIAL_FILENAMES[direct] : direct;
    const variants = [direct, specialKey];
    // A few common alternatives
    if(/missbee$/i.test(direct)) variants.unshift('MissBee2','MissBee');
    if(/rock(er|in)bee$/i.test(direct)) variants.unshift('RockarBee','RockerBee','RockinBee');
    if(/nursebee$/i.test(direct)) variants.unshift('NureseBee','NurseBee');
    return Array.from(new Set(variants));
  }

  function buildUrlCandidates(baseNames){
    const urls = [];
    for(const b of baseNames){
      for(const ext of EXTENSIONS){
        urls.push(`/static/images/avatars/${b}.${ext}`);
      }
      // Fallback to GLB thumbnails if present
      urls.push(`/static/assets/avatars/glb_files/AvatarThumbnails/${b}!.png`);
      urls.push(`/static/assets/avatars/glb_files/AvatarThumbnails/${b}.png`);
    }
    return urls;
  }

  function trySetImage(img, urls){
    if(!img) return;
    let i = 0;
    const attempt = ()=>{
      if(i >= urls.length){ return; }
      const url = urls[i++];
      img.onerror = ()=> attempt();
      img.onload = ()=> { img.onerror = null; };
      img.src = url;
    };
    attempt();
  }

  // Guard against races when names change quickly
  let lastToken = 0;
  function updateFromName(imgEl, nameText){
    const token = ++lastToken;
    const candidates = toCandidates(nameText);
    const urls = buildUrlCandidates(candidates);
    // Slight delay to allow other UI updates to settle
    setTimeout(()=>{ if(token === lastToken) trySetImage(imgEl, urls); }, 200);
  }

  function autoDetect(selectorList){
    for(const sel of selectorList){
      const el = document.querySelector(sel);
      if(el) return el;
    }
    return null;
  }

  function observeName(nameEl, imageEl){
    const current = ()=> (nameEl.textContent||'').trim();
    // Initial sync
    updateFromName(imageEl, current());
    // Observe changes with debounce
    const debounced = debounce(()=>{ updateFromName(imageEl, current()); }, 250);
    const obs = new MutationObserver(debounced);
    obs.observe(nameEl, {characterData:true, childList:true, subtree:true});
  }

  const API = {
    initialize(options={}){
      const nameEl = options.nameEl || (options.nameSelector ? document.querySelector(options.nameSelector) : autoDetect(DEFAULT_NAME_SELECTORS));
      const imageEl = options.imageEl || (options.imageSelector ? document.querySelector(options.imageSelector) : autoDetect(DEFAULT_IMAGE_SELECTORS));
      if(!nameEl || !imageEl){
        // No-op if elements not present
        return false;
      }
      observeName(nameEl, imageEl);
      return true;
    }
  };

  window.BeeSmartAvatarSync = API;

  function autoInit(){
    API.initialize({});
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }
})();
