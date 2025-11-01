import { CapacitorConfig } from '@capacitor/cli';

// Minimal Capacitor config pointing to the hosted web app.
// Note: You still need to `npm i -D @capacitor/cli @capacitor/core` in this folder
// and run `npx cap init` to create native projects.

const config: CapacitorConfig = {
  appId: 'app.beesmartspelling',
  appName: 'BeeSmart Spelling Bee',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    url: 'https://beesmartspelling.app',
    cleartext: false,
    androidScheme: 'https'
  }
};

export default config;
