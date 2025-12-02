import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// This connects your mobile app to the Railway backend

const config: CapacitorConfig = {
  // Normalized to match root config for store builds
  appId: 'com.beesmart.spelling',
  appName: 'BeeSmart Spelling',
  webDir: 'static',
  server: {
    // Production Railway URL (canonical)
    url: 'https://beesmartspellingbeeapp-production.up.railway.app',
    cleartext: true,
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

