/**
 * Environment Configuration
 * 
 * Centralized configuration for all environment variables
 * Provides type-safe access to env vars with defaults
 */

export const env = {
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:7880',
    timeout: 10000,
  },

  // OAuth Configuration
  oauth: {
    googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
    githubClientId: import.meta.env.VITE_GITHUB_CLIENT_ID || '',
    enabled: import.meta.env.VITE_ENABLE_OAUTH === 'true',
  },

  // PayPal Configuration
  paypal: {
    clientId: import.meta.env.VITE_PAYPAL_CLIENT_ID || '',
    mode: import.meta.env.VITE_PAYPAL_MODE || 'sandbox',
    enabled: import.meta.env.VITE_ENABLE_PAYPAL === 'true',
  },

  // App Configuration
  app: {
    name: import.meta.env.VITE_APP_NAME || 'Tero AI Receptionist',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  },

  // Feature Flags
  features: {
    oauth: import.meta.env.VITE_ENABLE_OAUTH === 'true',
    paypal: import.meta.env.VITE_ENABLE_PAYPAL === 'true',
    websockets: import.meta.env.VITE_ENABLE_WEBSOCKETS === 'true',
  },

  // Development
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  debug: import.meta.env.VITE_DEBUG === 'true',
};

export default env;
