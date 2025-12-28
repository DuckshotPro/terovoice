import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, tokenManager } from '../services/api';

/**
 * AuthContext - Manages authentication state and operations
 * 
 * Provides:
 * - User authentication state
 * - Login/signup/logout functions
 * - Token management
 * - Session persistence
 */

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = tokenManager.getToken();
        
        if (token && !tokenManager.isTokenExpired(token)) {
          // Token exists and is valid, fetch user profile
          const response = await api.auth.me();
          setUser(response.data);
          setIsAuthenticated(true);
        } else if (token) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await api.auth.refresh(refreshToken);
              tokenManager.setToken(response.data.access_token);
              const userResponse = await api.auth.me();
              setUser(userResponse.data);
              setIsAuthenticated(true);
            } catch (err) {
              // Refresh failed, clear auth
              tokenManager.removeToken();
              localStorage.removeItem('refresh_token');
              setIsAuthenticated(false);
            }
          }
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    // Listen for logout events from other tabs/windows
    const handleLogout = () => {
      setUser(null);
      setIsAuthenticated(false);
    };

    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  const login = useCallback(async (email, password) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.auth.login({ email, password });
      const { access_token, refresh_token, user: userData } = response.data;
      
      tokenManager.setToken(access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return userData;
    } catch (err) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(async (email, password, name) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.auth.register({ email, password, name });
      const { access_token, refresh_token, user: userData } = response.data;
      
      tokenManager.setToken(access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return userData;
    } catch (err) {
      const errorMessage = err.message || 'Signup failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await api.auth.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      tokenManager.removeToken();
      localStorage.removeItem('refresh_token');
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (userData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.users.updateProfile(userData);
      setUser(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Profile update failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    signup,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
