/**
 * API Client Configuration
 * 
 * Centralized Axios instance with interceptors for:
 * - JWT token management
 * - Request/response logging
 * - Error handling
 * - Base URL configuration
 */

import axios from 'axios';
import env from '../config/env';

// API Configuration
const API_BASE_URL = env.api.baseUrl;
const API_TIMEOUT = env.api.timeout;

// Create Axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management utilities
const tokenManager = {
  getToken: () => localStorage.getItem('auth_token'),
  setToken: (token) => localStorage.setItem('auth_token', token),
  removeToken: () => localStorage.removeItem('auth_token'),
  isTokenExpired: (token) => {
    if (!token) return true;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
};

// Request interceptor - Add JWT token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    
    if (token && !tokenManager.isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (env.debug) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle responses and errors
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (env.debug) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized - Token expired or invalid
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          tokenManager.setToken(access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
      }
      
      // If refresh fails, clear tokens and redirect to login
      tokenManager.removeToken();
      localStorage.removeItem('refresh_token');
      
      // Dispatch custom event for auth failure
      window.dispatchEvent(new CustomEvent('auth:logout'));
      
      return Promise.reject(error);
    }
    
    // Handle other errors
    const errorMessage = error.response?.data?.message || error.message || 'An error occurred';
    
    console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
    });
    
    // Create standardized error object
    const apiError = {
      status: error.response?.status || 0,
      message: errorMessage,
      data: error.response?.data,
      isNetworkError: !error.response,
      isServerError: error.response?.status >= 500,
      isClientError: error.response?.status >= 400 && error.response?.status < 500,
    };
    
    return Promise.reject(apiError);
  }
);

// API Methods
export const api = {
  // Generic HTTP methods
  get: (url, config = {}) => apiClient.get(url, config),
  post: (url, data = {}, config = {}) => apiClient.post(url, data, config),
  put: (url, data = {}, config = {}) => apiClient.put(url, data, config),
  patch: (url, data = {}, config = {}) => apiClient.patch(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config),
  
  // Health check
  health: () => apiClient.get('/health'),
  
  // Authentication endpoints
  auth: {
    register: (userData) => apiClient.post('/auth/register', userData),
    login: (credentials) => apiClient.post('/auth/login', credentials),
    logout: () => apiClient.post('/auth/logout'),
    refresh: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
    me: () => apiClient.get('/auth/me'),
    forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
    resetPassword: (token, password) => apiClient.post('/auth/reset-password', { token, password }),
  },
  
  // User management
  users: {
    getProfile: () => apiClient.get('/users/profile'),
    updateProfile: (userData) => apiClient.put('/users/profile', userData),
    changePassword: (passwordData) => apiClient.post('/users/change-password', passwordData),
    deleteAccount: () => apiClient.delete('/users/account'),
  },
  
  // Client management
  clients: {
    list: (params = {}) => apiClient.get('/clients', { params }),
    get: (id) => apiClient.get(`/clients/${id}`),
    create: (clientData) => apiClient.post('/clients', clientData),
    update: (id, clientData) => apiClient.put(`/clients/${id}`, clientData),
    delete: (id) => apiClient.delete(`/clients/${id}`),
    stats: (id) => apiClient.get(`/clients/${id}/stats`),
  },
  
  // Call management
  calls: {
    list: (params = {}) => apiClient.get('/calls', { params }),
    get: (id) => apiClient.get(`/calls/${id}`),
    create: (callData) => apiClient.post('/calls', callData),
    export: (params = {}) => apiClient.get('/calls/export', { 
      params,
      responseType: 'blob' // For CSV download
    }),
  },
  
  // Analytics
  analytics: {
    dashboard: () => apiClient.get('/analytics/dashboard'),
    callsPerDay: (params = {}) => apiClient.get('/analytics/calls-per-day', { params }),
    sentiment: (params = {}) => apiClient.get('/analytics/sentiment', { params }),
    clientStats: (clientId) => apiClient.get(`/analytics/client/${clientId}/stats`),
    revenue: (params = {}) => apiClient.get('/analytics/revenue', { params }),
  },
  
  // Billing & Subscriptions (to be implemented with PayPal)
  billing: {
    getSubscription: () => apiClient.get('/billing/subscription'),
    createSubscription: (planData) => apiClient.post('/billing/subscription', planData),
    updateSubscription: (subscriptionData) => apiClient.put('/billing/subscription', subscriptionData),
    cancelSubscription: () => apiClient.delete('/billing/subscription'),
    getInvoices: (params = {}) => apiClient.get('/billing/invoices', { params }),
    downloadInvoice: (invoiceId) => apiClient.get(`/billing/invoices/${invoiceId}/download`, {
      responseType: 'blob'
    }),
  },
  
  // Settings
  settings: {
    get: () => apiClient.get('/settings'),
    update: (settings) => apiClient.put('/settings', settings),
    getApiKeys: () => apiClient.get('/settings/api-keys'),
    createApiKey: (keyData) => apiClient.post('/settings/api-keys', keyData),
    revokeApiKey: (keyId) => apiClient.delete(`/settings/api-keys/${keyId}`),
  },
};

// Export token manager for use in auth context
export { tokenManager };

// Export default API client for custom requests
export default apiClient;