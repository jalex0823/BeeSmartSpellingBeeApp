import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// Store builds load bundled web assets (no remote hosting dependency)

const config: CapacitorConfig = {
  // Normalized to match root config for store builds
  appId: 'com.beesmart.spellingbee',
  appName: 'BeeSmart Spelling',
  // Production wrapper: load the deployed site (DigitalOcean)
  // NOTE: If you want a fully-offline/bundled build later, remove server.url.
  webDir: 'www',
  server: {
    url: 'https://beesmartspelling.app/',
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

