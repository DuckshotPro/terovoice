import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../services/api';

/**
 * BillingContext - Manages billing and subscription data
 *
 * Provides:
 * - Subscription management
 * - Invoice history
 * - Payment methods
 * - Billing statistics
 */

const BillingContext = createContext(null);

export const BillingProvider = ({ children }) => {
  const [subscription, setSubscription] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSubscription = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.billing.getSubscription();
      setSubscription(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch subscription';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchInvoices = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.billing.getInvoices();
      setInvoices(response.data.invoices || []);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch invoices';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSubscription = useCallback(async (planId, paymentMethodId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.billing.createSubscription({
        plan_id: planId,
        payment_method_id: paymentMethodId,
      });
      setSubscription(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to create subscription';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const cancelSubscription = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      await api.billing.cancelSubscription();
      setSubscription(null);
      return true;
    } catch (err) {
      const errorMessage = err.message || 'Failed to cancel subscription';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updatePaymentMethod = useCallback(async (paymentMethodId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.billing.updatePaymentMethod({
        payment_method_id: paymentMethodId,
      });
      setSubscription(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to update payment method';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    subscription,
    invoices,
    isLoading,
    error,
    fetchSubscription,
    fetchInvoices,
    createSubscription,
    cancelSubscription,
    updatePaymentMethod,
  };

  return <BillingContext.Provider value={value}>{children}</BillingContext.Provider>;
};

export const useBilling = () => {
  const context = useContext(BillingContext);
  if (!context) {
    throw new Error('useBilling must be used within BillingProvider');
  }
  return context;
};
