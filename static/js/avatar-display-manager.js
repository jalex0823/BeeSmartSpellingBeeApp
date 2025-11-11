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

  function AvatarDisplayManager(){ }

  AvatarDisplayManager.prototype.init = function(){
    // Prevent double initialization
    if (window._avatarDisplayManagerInitialized) return;
    window._avatarDisplayManagerInitialized = true;
    
    try {
      var isAuth = !!(window && window.IS_AUTH === true);
      var guestWrap = document.getElementById('guestAvatarCarousel');
      var mascot = document.getElementById('mascotBee3D');

      if (isAuth) {
        // Registered mode: ensure guest carousel stays hidden if present
        if (guestWrap) guestWrap.style.display = 'none';
        // Avatar is loaded by the page's deferred loader (initDefaultMascot), nothing else to do
        return;
      }

      // Guest mode: ensure mascot container (if any) is hidden
      if (mascot && mascot.parentElement) {
        try { mascot.parentElement.style.display = 'none'; } catch(_){}
      }

      // Initialize carousel if page didn’t already
      try {
        var used3D = false;
        if (typeof window.initGuestAvatar3DCarousel === 'function') {
          used3D = !!window.initGuestAvatar3DCarousel();
        }
        if (!used3D && typeof window.initGuestAvatarCarousel === 'function') {
          window.initGuestAvatarCarousel();
        }
      } catch(_){}

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
