/*
 * AvatarDisplayManager
 * Unifies home screen avatar display:
 *  - Guests: show carousel only; clicking prompts registration/login
 *  - Registered: show selected avatar only; hide carousel
 *
 * This is a thin coordinator that builds on existing functions:
 *  - initGuestAvatar3DCarousel / initGuestAvatarCarousel (defined in template)
 *  - initDefaultMascot / initUserAvatar3D + UserAvatarLoader (for registered users)
 */
(function(window, document){
  'use strict';

  function isThreeReady() {
    try {
      return (
        typeof window !== 'undefined' &&
        typeof window.THREE !== 'undefined' &&
        typeof window.THREE.GLTFLoader !== 'undefined' &&
        !!window.WebGLRenderingContext
      );
    } catch (_e) {
      return false;
    }
  }

  function AvatarDisplayManager(){ }

  AvatarDisplayManager.prototype.init = function(){
    // Prevent double initialization
    if (window._avatarDisplayManagerInitialized) return;
    if (window._avatarDisplayManagerInitInProgress) return;
    window._avatarDisplayManagerInitInProgress = true;
    
    try {
      var isAuth = !!(window && window.IS_AUTH === true);
      var guestWrap = document.getElementById('guestAvatarCarousel');
      var mascot = document.getElementById('mascotBee3D');

      if (isAuth) {
        // Registered mode: ensure guest carousel stays hidden if present
        if (guestWrap) guestWrap.style.display = 'none';
        window._avatarDisplayManagerInitialized = true;
        window._avatarDisplayManagerInitInProgress = false;
        // Avatar is loaded by the page's deferred loader (initDefaultMascot), nothing else to do
        return;
      }

      // Guest mode: ensure mascot container (if any) is hidden
      if (mascot && mascot.parentElement) {
        try { mascot.parentElement.style.display = 'none'; } catch(_){}
      }

      // Show the guest carousel wrapper immediately (don't wait for GLB load)
      if (guestWrap) {
        guestWrap.style.display = 'block';
        var canvasWrap = document.getElementById('guestAvatar3D');
        if (canvasWrap) canvasWrap.style.display = 'block';
      }

      // Initialize a fast 2D carousel immediately, then upgrade to 3D when Three.js is ready.
      // This prevents getting stuck in PNG mode if initialization happens before vendor scripts load.
      try {
        if (typeof window.initGuestAvatarCarousel === 'function') {
          window.initGuestAvatarCarousel();
        }
      } catch(_){ }

      // Attempt 3D upgrade with retries (best effort)
      (function attempt3DUpgrade(){
        var maxAttempts = 12; // ~12s worst case with 1s interval
        var attempt = 0;

        function tryOnce(){
          attempt += 1;
          try {
            // Only attempt if Three is actually ready (avoid locking into 2D due to timing)
            if (!isThreeReady()) {
              return false;
            }
            if (typeof window.initGuestAvatar3DCarousel === 'function') {
              var ok = !!window.initGuestAvatar3DCarousel();
              if (ok) {
                // Stop the 2D carousel timer if it is running
                try {
                  if (window._guestCarouselTimer) {
                    clearInterval(window._guestCarouselTimer);
                    window._guestCarouselTimer = null;
                  }
                } catch(_e) {}
                return true;
              }
            }
          } catch(_e) {}
          return false;
        }

        // Try now, otherwise retry shortly
        if (tryOnce()) {
          return;
        }
        var t = setInterval(function(){
          // If 3D init succeeds, stop retrying
          if (tryOnce()) {
            clearInterval(t);
            return;
          }
          if (attempt >= maxAttempts) {
            clearInterval(t);
          }
        }, 1000);
      })();

      window._avatarDisplayManagerInitialized = true;
      window._avatarDisplayManagerInitInProgress = false;

      // Click anywhere on carousel to navigate to registration
      try {
        var wrap = document.getElementById('guestAvatarCarousel');
        if (wrap) {
          wrap.style.cursor = 'pointer';
          wrap.addEventListener('click', function(){ window.location.href = '/auth/register'; });
        }
      } catch(_){}
    } catch (e) {
      // best effort only
      console.warn('[AvatarDisplayManager] init failed:', e);
      window._avatarDisplayManagerInitInProgress = false;
    }
  };

  // Expose
  window.AvatarDisplayManager = AvatarDisplayManager;

  // DEFERRED: Wait for honey loader to finish before initializing 3D carousel
  // This prevents blocking the main thread during initial page load
  document.addEventListener('BeeSmart:loaderComplete', function(){
    // Add small delay to let page fully paint first
    setTimeout(function(){
      try { new AvatarDisplayManager().init(); } catch(_){}
    }, 100);
  });

  // Fallback: if loader never fires, init after 3 seconds
  setTimeout(function(){
    if (!window._avatarDisplayManagerInitialized) {
      try { new AvatarDisplayManager().init(); } catch(_){}
    }
  }, 3000);

})(window, document);
