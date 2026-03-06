/**
 * PayPal Services Index
 * Exports all PayPal-related services for subscription management, webhooks, and billing
 */

export { default as subscriptionManager } from './subscriptionManager.js';
export { default as customerManager } from './customerManager.js';
export { default as subscriptionTracker } from './subscriptionTracker.js';
export { default as webhookProcessor } from './webhookProcessor.js';
export { default as webhookRetry } from './webhookRetry.js';

export {
  createSubscription,
  getSubscription,
  cancelSubscription,
  updateSubscription,
  listSubscriptions,
  getPlanDetails,
  getAllPlans,
  SUBSCRIPTION_PLANS
} from './subscriptionManager.js';

export {
  createCustomerFromSubscription,
  linkPayPalCustomer,
  syncCustomerData,
  getCustomer,
  getCustomerByPayPalId,
  updateCustomerStatus,
  listCustomers,
  deleteCustomer
} from './customerManager.js';

export {
  trackStatusChange,
  getStatusHistory,
  getCurrentStatus,
  isSubscriptionActive,
  getStatusTimeline,
  getSubscriptionMetrics,
  getSubscriptionsByStatus,
  getStatusSummary
} from './subscriptionTracker.js';

export {
  verifyWebhookSignature,
  isWebhookProcessed,
  markWebhookProcessed,
  processWebhookEvent,
  WEBHOOK_EVENTS,
  WEBHOOK_RETENTION_TIME
} from './webhookProcessor.js';

export {
  calculateBackoffDelay,
  queueWebhookForRetry,
  getRetryStatus,
  getPendingRetries,
  cancelRetry,
  getRetryStats,
  monitorPerformance,
  cleanupOldRetries,
  RETRY_CONFIG
} from './webhookRetry.js';
