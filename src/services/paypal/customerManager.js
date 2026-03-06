/**
 * PayPal Customer Management Service
 * Handles customer creation, linking, and data synchronization
 * Uses real PayPal API via PayPalAPIClient
 */

import PayPalAPIClient from './apiClient.js';

// Initialize PayPal API client
const paypalClient = new PayPalAPIClient(
  process.env.PAYPAL_CLIENT_ID,
  process.env.PAYPAL_CLIENT_SECRET,
  process.env.PAYPAL_ENVIRONMENT || 'sandbox'
);

// Database for customer records (in production, use real database)
const customerDatabase = new Map();

/**
 * Create customer record on subscription completion
 * @param {object} subscriptionData - Subscription data from PayPal
 * @returns {Promise<object>} Customer record
 */
export async function createCustomerFromSubscription(subscriptionData) {
  const { subscriptionId, customerId, planId, price } = subscriptionData;

  try {
    // Get subscription details from PayPal to verify
    const subscription = await paypalClient.getSubscription(subscriptionId);

    const customer = {
      id: `cust_${Math.random().toString(36).substr(2, 9)}`,
      paypalCustomerId: customerId,
      paypalSubscriptionId: subscriptionId,
      planId: planId,
      status: 'ACTIVE',
      email: subscription.subscriber?.email_address,
      firstName: subscription.subscriber?.name?.given_name,
      lastName: subscription.subscriber?.name?.surname,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    // Store in database
    customerDatabase.set(customer.id, customer);

    return customer;
  } catch (error) {
    console.error('Error creating customer:', error);
    throw error;
  }
}

/**
 * Link PayPal customer ID with internal customer database
 * @param {string} internalCustomerId - Internal customer ID
 * @param {string} paypalCustomerId - PayPal customer ID
 * @returns {Promise<object>} Updated customer record
 */
export async function linkPayPalCustomer(internalCustomerId, paypalCustomerId) {
  try {
    const customer = customerDatabase.get(internalCustomerId);

    if (!customer) {
      throw new Error(`Customer not found: ${internalCustomerId}`);
    }

    customer.paypalCustomerId = paypalCustomerId;
    customer.updatedAt = new Date().toISOString();

    customerDatabase.set(internalCustomerId, customer);

    return customer;
  } catch (error) {
    console.error('Error linking PayPal customer:', error);
    throw error;
  }
}

/**
 * Synchronize customer data with PayPal
 * @param {string} customerId - Internal customer ID
 * @param {object} updates - Data to update
 * @returns {Promise<object>} Updated customer record
 */
export async function syncCustomerData(customerId, updates) {
  try {
    const customer = customerDatabase.get(customerId);

    if (!customer) {
      throw new Error(`Customer not found: ${customerId}`);
    }

    // Update customer data
    if (updates.email) customer.email = updates.email;
    if (updates.firstName) customer.firstName = updates.firstName;
    if (updates.lastName) customer.lastName = updates.lastName;
    if (updates.phone) customer.phone = updates.phone;
    if (updates.company) customer.company = updates.company;

    customer.updatedAt = new Date().toISOString();

    customerDatabase.set(customerId, customer);

    return customer;
  } catch (error) {
    console.error('Error syncing customer data:', error);
    throw error;
  }
}

/**
 * Get customer by ID
 * @param {string} customerId - Internal customer ID
 * @returns {Promise<object>} Customer record
 */
export async function getCustomer(customerId) {
  try {
    const customer = customerDatabase.get(customerId);

    if (!customer) {
      throw new Error(`Customer not found: ${customerId}`);
    }

    return customer;
  } catch (error) {
    console.error('Error getting customer:', error);
    throw error;
  }
}

/**
 * Get customer by PayPal ID
 * @param {string} paypalCustomerId - PayPal customer ID
 * @returns {Promise<object>} Customer record
 */
export async function getCustomerByPayPalId(paypalCustomerId) {
  try {
    for (const [, customer] of customerDatabase) {
      if (customer.paypalCustomerId === paypalCustomerId) {
        return customer;
      }
    }

    throw new Error(`Customer not found with PayPal ID: ${paypalCustomerId}`);
  } catch (error) {
    console.error('Error getting customer by PayPal ID:', error);
    throw error;
  }
}

/**
 * Get customer by subscription ID
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<object>} Customer record
 */
export async function getCustomerBySubscriptionId(subscriptionId) {
  try {
    for (const [, customer] of customerDatabase) {
      if (customer.paypalSubscriptionId === subscriptionId) {
        return customer;
      }
    }

    throw new Error(`Customer not found with subscription ID: ${subscriptionId}`);
  } catch (error) {
    console.error('Error getting customer by subscription ID:', error);
    throw error;
  }
}

/**
 * Update customer subscription status
 * @param {string} customerId - Internal customer ID
 * @param {string} newStatus - New subscription status
 * @returns {Promise<object>} Updated customer record
 */
export async function updateCustomerStatus(customerId, newStatus) {
  try {
    const customer = customerDatabase.get(customerId);

    if (!customer) {
      throw new Error(`Customer not found: ${customerId}`);
    }

    customer.status = newStatus;
    customer.updatedAt = new Date().toISOString();

    customerDatabase.set(customerId, customer);

    return customer;
  } catch (error) {
    console.error('Error updating customer status:', error);
    throw error;
  }
}

/**
 * List all customers
 * @returns {Promise<array>} Array of customer records
 */
export async function listCustomers() {
  try {
    return Array.from(customerDatabase.values());
  } catch (error) {
    console.error('Error listing customers:', error);
    throw error;
  }
}

/**
 * Delete customer record
 * @param {string} customerId - Internal customer ID
 * @returns {Promise<boolean>} Deletion success
 */
export async function deleteCustomer(customerId) {
  try {
    const deleted = customerDatabase.delete(customerId);
    return deleted;
  } catch (error) {
    console.error('Error deleting customer:', error);
    throw error;
  }
}

export default {
  createCustomerFromSubscription,
  linkPayPalCustomer,
  syncCustomerData,
  getCustomer,
  getCustomerByPayPalId,
  getCustomerBySubscriptionId,
  updateCustomerStatus,
  listCustomers,
  deleteCustomer,
  paypalClient
};
