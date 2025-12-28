import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../services/api';

/**
 * UserContext - Manages user profile and settings
 * 
 * Provides:
 * - User profile data
 * - User settings
 * - Profile update operations
 */

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.users.getProfile();
      setProfile(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch profile';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.settings.get();
      setSettings(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch settings';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (profileData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.users.updateProfile(profileData);
      setProfile(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to update profile';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (settingsData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.settings.update(settingsData);
      setSettings(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to update settings';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const changePassword = useCallback(async (currentPassword, newPassword) => {
    setIsLoading(true);
    setError(null);
    try {
      await api.users.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      return true;
    } catch (err) {
      const errorMessage = err.message || 'Failed to change password';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    profile,
    settings,
    isLoading,
    error,
    fetchProfile,
    fetchSettings,
    updateProfile,
    updateSettings,
    changePassword,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
};
