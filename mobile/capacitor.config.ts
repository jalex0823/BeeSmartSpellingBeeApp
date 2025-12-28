import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// Store builds load bundled web assets (no remote hosting dependency)

const config: CapacitorConfig = {
  // Normalized to match root config for store builds
  appId: 'com.beesmart.spelling',
  appName: 'BeeSmart Spelling',
  // IMPORTANT: this wrapper lives in /mobile but should bundle the root app's web assets
  // (BeeSmart serves templates/static via Flask). For a packaged build we point at the
  // root `static/` folder.
  webDir: '../static',
  // IMPORTANT: No `server.url` here. Using it turns the app into a remote WebView.
  // We want a true wrapped app that ships the latest web build inside the bundle.
  server: {
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

