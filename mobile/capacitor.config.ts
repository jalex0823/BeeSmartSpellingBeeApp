import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// Store builds load bundled web assets (no remote hosting dependency)

const config: CapacitorConfig = {
  // Normalized to match root config for store builds
  appId: 'com.beesmart.spelling',
  appName: 'BeeSmart Spelling',
  // IMPORTANT: Flask app loads from hosted URL (beesmartspelling.app)
  // The app is a web wrapper that loads your production site
  webDir: 'www',  // placeholder directory (not used with server.url)
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

export default config;

