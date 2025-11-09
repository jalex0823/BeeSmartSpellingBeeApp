// loader-disable.js
// Temporary override to neutralize broken loader.
(function(){
  function nuke(selector){
    document.querySelectorAll(selector).forEach(el=>{el.style.display='none';});
  }
  ['#loading-screen','.loading-screen','#app-loader','.app-loader','#loader','.loader','#splash','.splash','#preload','.preload'].forEach(nuke);
  // Provide safe no-op global API if referenced elsewhere.
  window.showLoader = function(){};
  window.hideLoader = function(){};
})();
