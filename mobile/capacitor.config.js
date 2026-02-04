// BeeSmart Spelling Bee - Capacitor Configuration (JS for environments without TypeScript)
// Store builds load from server.url (https://beesmartspelling.app)

module.exports = {
  appId: 'com.beesmart.spellingbee',
  appName: 'BeeSmart Spelling',
  webDir: 'www',
  server: {
    url: 'https://beesmartspelling.app',
    cleartext: false
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#FFD700',
      showSpinner: false,
      androidScaleType: 'CENTER_CROP',
      splashFullScreen: true,
      splashImmersive: false
    },
    StatusBar: {
      style: 'light',
      backgroundColor: '#FFD700'
    }
  }
};
