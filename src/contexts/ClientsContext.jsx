import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../services/api';

/**
 * ClientsContext - Manages client data and operations
 *
 * Provides:
 * - List of clients
 * - Client CRUD operations
 * - Client statistics
 */

const ClientsContext = createContext(null);

export const ClientsProvider = ({ children }) => {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  const fetchClients = useCallback(async (page = 1, pageSize = 10) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.clients.list({
        page,
        page_size: pageSize,
      });
      setClients(response.data.clients || []);
      setPagination({
        page,
        pageSize,
        total: response.data.total || 0,
      });
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch clients';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getClient = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.clients.get(id);
      setSelectedClient(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch client';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createClient = useCallback(
    async (clientData) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.clients.create(clientData);
        setClients([response.data, ...clients]);
        return response.data;
      } catch (err) {
        const errorMessage = err.message || 'Failed to create client';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [clients]
  );

  const updateClient = useCallback(
    async (id, clientData) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.clients.update(id, clientData);
        setClients(clients.map((c) => (c.id === id ? response.data : c)));
        if (selectedClient?.id === id) {
          setSelectedClient(response.data);
        }
        return response.data;
      } catch (err) {
        const errorMessage = err.message || 'Failed to update client';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [clients, selectedClient]
  );

  const deleteClient = useCallback(
    async (id) => {
      setIsLoading(true);
      setError(null);
      try {
        await api.clients.delete(id);
        setClients(clients.filter((c) => c.id !== id));
        if (selectedClient?.id === id) {
          setSelectedClient(null);
        }
        return true;
      } catch (err) {
        const errorMessage = err.message || 'Failed to delete client';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [clients, selectedClient]
  );

  const getClientStats = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.clients.stats(id);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch client stats';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    clients,
    selectedClient,
    setSelectedClient,
    isLoading,
    error,
    pagination,
    fetchClients,
    getClient,
    createClient,
    updateClient,
    deleteClient,
    getClientStats,
  };

  return <ClientsContext.Provider value={value}>{children}</ClientsContext.Provider>;
};

export const useClients = () => {
  const context = useContext(ClientsContext);
  if (!context) {
    throw new Error('useClients must be used within ClientsProvider');
  }
  return context;
};
