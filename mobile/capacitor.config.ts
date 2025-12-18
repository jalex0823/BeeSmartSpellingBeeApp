import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// This connects your mobile app to the Railway backend

const config: CapacitorConfig = {
  // Normalized to match root config for store builds
  appId: 'com.beesmart.spelling',
  appName: 'BeeSmart Spelling',
  webDir: 'static',
  server: {
    // Canonical production URL (stable for App Review + store listings)
    url: 'https://beesmartspelling.app',
    cleartext: false,
    androidScheme: 'https'
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

