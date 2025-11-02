import { CapacitorConfig } from '@capacitor/cli';

// BeeSmart Spelling Bee - Capacitor Configuration
// This connects your mobile app to the Railway backend

const config: CapacitorConfig = {
  appId: 'app.beesmartspelling',
  appName: 'BeeSmart Spelling Bee',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    // Production Railway URL
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

