/**
 * Capacitor Helper - Native platform detection and utilities
 * Use this to detect if app is running in native iOS/Android vs browser
 */

const CapHelper = {
  /**
   * Check if running in native app (iOS or Android)
   */
  isNative: function() {
    return window.Capacitor && window.Capacitor.isNativePlatform();
  },
  
  /**
   * Check specific platform
   * @param {string} platform - 'ios', 'android', or 'web'
   */
  isPlatform: function(platform) {
    if (!window.Capacitor) return platform === 'web';
    return window.Capacitor.getPlatform() === platform;
  },
  
  /**
   * Get current platform name
   * @returns {string} 'ios', 'android', or 'web'
   */
  getPlatform: function() {
    if (!window.Capacitor) return 'web';
    return window.Capacitor.getPlatform();
  },
  
  /**
   * Get API base URL (empty for native - uses capacitor.config server.url)
   */
  getApiBase: function() {
    // Capacitor proxies all requests to server.url automatically
    return '';
  },
  
  /**
   * Check if device has camera
   */
  hasCamera: function() {
    return this.isNative() && (this.isPlatform('ios') || this.isPlatform('android'));
  },
  
  /**
   * Check if device supports haptic feedback
   */
  hasHaptics: function() {
    return this.isNative();
  },
  
  /**
   * Get safe area insets for notched devices
   */
  getSafeArea: function() {
    if (!this.isNative()) {
      return { top: 0, bottom: 0, left: 0, right: 0 };
    }
    // iOS safe area env variables
    return {
      top: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sat') || '0'),
      bottom: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sab') || '0'),
      left: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sal') || '0'),
      right: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sar') || '0')
    };
  }
};

// Auto-detect and log platform on load
document.addEventListener('DOMContentLoaded', function() {
  const platform = CapHelper.getPlatform();
  console.log('🐝 BeeSmart Platform:', platform);
  
  if (CapHelper.isNative()) {
    console.log('📱 Running in native app');
    document.body.classList.add('capacitor-native');
    document.body.classList.add('capacitor-' + platform);
  } else {
    console.log('🌐 Running in browser');
    document.body.classList.add('capacitor-web');
  }
});

// Export for use in other scripts
window.CapHelper = CapHelper;
