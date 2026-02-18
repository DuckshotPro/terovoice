/**
 * PayPal Subscription Tracker Service
 * Tracks subscription status changes and maintains history
 * Uses real PayPal API via PayPalAPIClient
 */

import PayPalAPIClient from './apiClient.js';

// Initialize PayPal API client
const paypalClient = new PayPalAPIClient(
  process.env.PAYPAL_CLIENT_ID,
  process.env.PAYPAL_CLIENT_SECRET,
  process.env.PAYPAL_ENVIRONMENT || 'sandbox'
);

// Database for status history (in production, use real database)
const statusHistoryDatabase = new Map();
const subscriptionDatabase = new Map();

/**
 * Track subscription status changes
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} newStatus - New subscription status
 * @param {object} metadata - Additional metadata
 * @returns {Promise<object>} Status update record
 */
export async function trackStatusChange(subscriptionId, newStatus, metadata = {}) {
  try {
    const statusRecord = {
      id: `status_${Math.random().toString(36).substr(2, 9)}`,
      subscriptionId: subscriptionId,
      oldStatus: metadata.oldStatus || 'UNKNOWN',
      newStatus: newStatus,
      metadata: metadata,
      createdAt: new Date().toISOString()
    };

    // Store status history
    if (!statusHistoryDatabase.has(subscriptionId)) {
      statusHistoryDatabase.set(subscriptionId, []);
    }
    statusHistoryDatabase.get(subscriptionId).push(statusRecord);

    // Update current subscription status
    const subscription = subscriptionDatabase.get(subscriptionId) || {};
    subscription.status = newStatus;
    subscription.updatedAt = new Date().toISOString();
    subscriptionDatabase.set(subscriptionId, subscription);

    return statusRecord;
  } catch (error) {
    console.error('Error tracking status change:', error);
    throw error;
  }
}

/**
 * Get subscription status history
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<array>} Status history records
 */
export async function getStatusHistory(subscriptionId) {
  try {
    const history = statusHistoryDatabase.get(subscriptionId) || [];
    return history.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  } catch (error) {
    console.error('Error getting status history:', error);
    throw error;
  }
}

/**
 * Get current subscription status from PayPal
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<string>} Current status
 */
export async function getCurrentStatus(subscriptionId) {
  try {
    // Try to get from cache first
    const cached = subscriptionDatabase.get(subscriptionId);
    if (cached?.status) {
      return cached.status;
    }

    // Get from PayPal API
    const subscription = await paypalClient.getSubscription(subscriptionId);

    // Cache the status
    subscriptionDatabase.set(subscriptionId, {
      status: subscription.status,
      updatedAt: new Date().toISOString()
    });

    return subscription.status;
  } catch (error) {
    console.error('Error getting current status:', error);
    throw error;
  }
}

/**
 * Check if subscription is active
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<boolean>} Is active
 */
export async function isSubscriptionActive(subscriptionId) {
  try {
    const status = await getCurrentStatus(subscriptionId);
    return status === 'ACTIVE';
  } catch (error) {
    console.error('Error checking subscription active status:', error);
    throw error;
  }
}

/**
 * Get subscription status timeline
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<array>} Timeline of status changes
 */
export async function getStatusTimeline(subscriptionId) {
  try {
    const history = await getStatusHistory(subscriptionId);

    return history.map(record => ({
      status: record.newStatus,
      timestamp: record.createdAt,
      reason: record.metadata.reason || 'Status change',
      details: record.metadata
    }));
  } catch (error) {
    console.error('Error getting status timeline:', error);
    throw error;
  }
}

/**
 * Get subscription metrics
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<object>} Subscription metrics
 */
export async function getSubscriptionMetrics(subscriptionId) {
  try {
    const history = await getStatusHistory(subscriptionId);
    const currentStatus = await getCurrentStatus(subscriptionId);

    // Calculate metrics
    const statusCounts = {};
    history.forEach(record => {
      statusCounts[record.newStatus] = (statusCounts[record.newStatus] || 0) + 1;
    });

    const createdRecord = history[history.length - 1];
    const createdAt = createdRecord?.createdAt || new Date().toISOString();
    const daysActive = Math.floor((Date.now() - new Date(createdAt).getTime()) / (1000 * 60 * 60 * 24));

    return {
      subscriptionId: subscriptionId,
      currentStatus: currentStatus,
      statusCounts: statusCounts,
      totalStatusChanges: history.length,
      daysActive: daysActive,
      createdAt: createdAt,
      lastUpdated: history[0]?.createdAt || createdAt
    };
  } catch (error) {
    console.error('Error getting subscription metrics:', error);
    throw error;
  }
}

/**
 * Get all subscriptions with a specific status
 * @param {string} status - Status to filter by
 * @returns {Promise<array>} Array of subscription IDs
 */
export async function getSubscriptionsByStatus(status) {
  try {
    const subscriptions = [];

    for (const [subscriptionId, subscription] of subscriptionDatabase) {
      if (subscription.status === status) {
        subscriptions.push(subscriptionId);
      }
    }

    return subscriptions;
  } catch (error) {
    console.error('Error getting subscriptions by status:', error);
    throw error;
  }
}

/**
 * Get subscription status summary
 * @returns {Promise<object>} Summary of all subscription statuses
 */
export async function getStatusSummary() {
  try {
    const summary = {};

    for (const [, subscription] of subscriptionDatabase) {
      const status = subscription.status;
      summary[status] = (summary[status] || 0) + 1;
    }

    return {
      total: subscriptionDatabase.size,
      byStatus: summary,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error getting status summary:', error);
    throw error;
  }
}

/**
 * Sync subscription status with PayPal
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<object>} Synced subscription data
 */
export async function syncSubscriptionStatus(subscriptionId) {
  try {
    // Get current status from PayPal
    const subscription = await paypalClient.getSubscription(subscriptionId);

    // Get cached status
    const cached = subscriptionDatabase.get(subscriptionId);
    const oldStatus = cached?.status || 'UNKNOWN';

    // Track the change if status changed
    if (oldStatus !== subscription.status) {
      await trackStatusChange(subscriptionId, subscription.status, {
        oldStatus: oldStatus,
        reason: 'Synced from PayPal',
        syncTime: new Date().toISOString()
      });
    }

    // Update cache
    subscriptionDatabase.set(subscriptionId, {
      status: subscription.status,
      updatedAt: new Date().toISOString(),
      paypalData: subscription
    });

    return {
      subscriptionId: subscriptionId,
      status: subscription.status,
      synced: true,
      syncTime: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error syncing subscription status:', error);
    throw error;
  }
}

export default {
  trackStatusChange,
  getStatusHistory,
  getCurrentStatus,
  isSubscriptionActive,
  getStatusTimeline,
  getSubscriptionMetrics,
  getSubscriptionsByStatus,
  getStatusSummary,
  syncSubscriptionStatus,
  paypalClient
};
