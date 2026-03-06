/**
 * PayPal Webhook Processing Service
 * Handles incoming PayPal webhook events with signature verification and idempotent processing
 * Processes subscription, payment, and billing events
 */

import crypto from 'crypto';
import { trackStatusChange, getStatusHistory } from './subscriptionTracker.js';
import { updateCustomerStatus } from './customerManager.js';
import { queueWebhookForRetry, monitorPerformance } from './webhookRetry.js';

// Webhook event types we handle
const WEBHOOK_EVENTS = {
  BILLING_SUBSCRIPTION_CREATED: 'BILLING.SUBSCRIPTION.CREATED',
  BILLING_SUBSCRIPTION_ACTIVATED: 'BILLING.SUBSCRIPTION.ACTIVATED',
  BILLING_SUBSCRIPTION_CANCELLED: 'BILLING.SUBSCRIPTION.CANCELLED',
  BILLING_SUBSCRIPTION_SUSPENDED: 'BILLING.SUBSCRIPTION.SUSPENDED',
  BILLING_SUBSCRIPTION_UPDATED: 'BILLING.SUBSCRIPTION.UPDATED',
  PAYMENT_CAPTURE_COMPLETED: 'PAYMENT.CAPTURE.COMPLETED',
  PAYMENT_CAPTURE_DENIED: 'PAYMENT.CAPTURE.DENIED',
  PAYMENT_CAPTURE_REFUNDED: 'PAYMENT.CAPTURE.REFUNDED',
  PAYMENT_CAPTURE_REVERSED: 'PAYMENT.CAPTURE.REVERSED'
};

// Webhook processing state for idempotency
const processedWebhooks = new Map();
const WEBHOOK_RETENTION_TIME = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Verify PayPal webhook signature
 * @param {object} headers - Request headers from PayPal
 * @param {string} body - Raw request body
 * @param {string} webhookId - PayPal webhook ID
 * @returns {boolean} True if signature is valid
 */
export function verifyWebhookSignature(headers, body, webhookId) {
  try {
    const transmissionId = headers['paypal-transmission-id'];
    const transmissionTime = headers['paypal-transmission-time'];
    const certUrl = headers['paypal-cert-url'];
    const authAlgo = headers['paypal-auth-algo'];
    const transmissionSig = headers['paypal-transmission-sig'];

    if (!transmissionId || !transmissionTime || !certUrl || !authAlgo || !transmissionSig) {
      console.warn('Missing required webhook headers');
      return false;
    }

    // Create the expected signature
    const expectedSig = crypto
      .createHmac('sha256', process.env.PAYPAL_WEBHOOK_SECRET || 'webhook_secret')
      .update(`${transmissionId}|${transmissionTime}|${webhookId}|${body}`)
      .digest('base64');

    // Compare signatures (constant-time comparison to prevent timing attacks)
    const isValid = crypto.timingSafeEqual(
      Buffer.from(transmissionSig),
      Buffer.from(expectedSig)
    );

    return isValid;
  } catch (error) {
    console.error('Error verifying webhook signature:', error);
    return false;
  }
}

/**
 * Check if webhook has already been processed (idempotency)
 * @param {string} webhookId - Unique webhook ID from PayPal
 * @returns {boolean} True if webhook was already processed
 */
export function isWebhookProcessed(webhookId) {
  return processedWebhooks.has(webhookId);
}

/**
 * Mark webhook as processed
 * @param {string} webhookId - Unique webhook ID from PayPal
 */
export function markWebhookProcessed(webhookId) {
  processedWebhooks.set(webhookId, {
    processedAt: new Date(),
    expiresAt: new Date(Date.now() + WEBHOOK_RETENTION_TIME)
  });

  // Clean up old entries
  cleanupOldWebhooks();
}

/**
 * Clean up old webhook records to prevent memory leaks
 */
function cleanupOldWebhooks() {
  const now = new Date();
  for (const [webhookId, record] of processedWebhooks.entries()) {
    if (record.expiresAt < now) {
      processedWebhooks.delete(webhookId);
    }
  }
}

/**
 * Process incoming webhook event
 * @param {object} event - PayPal webhook event
 * @returns {Promise<object>} Processing result
 */
export async function processWebhookEvent(event) {
  const startTime = Date.now();

  try {
    // Check for duplicate processing
    if (isWebhookProcessed(event.id)) {
      console.log(`Webhook ${event.id} already processed, skipping`);
      return {
        success: true,
        isDuplicate: true,
        processingTime: Date.now() - startTime
      };
    }

    // Route to appropriate handler
    let result;
    switch (event.event_type) {
      case WEBHOOK_EVENTS.BILLING_SUBSCRIPTION_CREATED:
        result = await handleSubscriptionCreated(event);
        break;
      case WEBHOOK_EVENTS.BILLING_SUBSCRIPTION_ACTIVATED:
        result = await handleSubscriptionActivated(event);
        break;
      case WEBHOOK_EVENTS.BILLING_SUBSCRIPTION_CANCELLED:
        result = await handleSubscriptionCancelled(event);
        break;
      case WEBHOOK_EVENTS.BILLING_SUBSCRIPTION_SUSPENDED:
        result = await handleSubscriptionSuspended(event);
        break;
      case WEBHOOK_EVENTS.BILLING_SUBSCRIPTION_UPDATED:
        result = await handleSubscriptionUpdated(event);
        break;
      case WEBHOOK_EVENTS.PAYMENT_CAPTURE_COMPLETED:
        result = await handlePaymentCompleted(event);
        break;
      case WEBHOOK_EVENTS.PAYMENT_CAPTURE_DENIED:
        result = await handlePaymentDenied(event);
        break;
      case WEBHOOK_EVENTS.PAYMENT_CAPTURE_REFUNDED:
        result = await handlePaymentRefunded(event);
        break;
      default:
        console.warn(`Unknown webhook event type: ${event.event_type}`);
        result = { success: true, handled: false };
    }

    // Mark as processed
    markWebhookProcessed(event.id);

    const processingTime = Date.now() - startTime;

    // Monitor performance
    const performance = monitorPerformance(processingTime);
    if (performance.warning) {
      console.warn(`Webhook processing performance warning: ${processingTime}ms (target: 30s)`);
    }

    return {
      success: true,
      isDuplicate: false,
      eventType: event.event_type,
      processingTime,
      performance,
      result
    };
  } catch (error) {
    console.error('Error processing webhook:', error);

    const processingTime = Date.now() - startTime;

    // Queue for retry on error
    await queueWebhookForRetry(event, 0, error);

    return {
      success: false,
      error: error.message,
      processingTime,
      queued_for_retry: true
    };
  }
}

/**
 * Handle subscription created event
 */
async function handleSubscriptionCreated(event) {
  const { resource } = event;
  const subscriptionId = resource.id;

  console.log(`Processing subscription created: ${subscriptionId}`);

  try {
    await trackStatusChange(subscriptionId, 'APPROVAL_PENDING', {
      oldStatus: 'CREATED',
      reason: 'Subscription created by customer',
      source: 'webhook',
      webhookId: event.id
    });

    return {
      handled: true,
      subscriptionId,
      status: 'APPROVAL_PENDING'
    };
  } catch (error) {
    console.error(`Error handling subscription created: ${error.message}`);
    throw error;
  }
}

/**
 * Handle subscription activated event
 */
async function handleSubscriptionActivated(event) {
  const { resource } = event;
  const subscriptionId = resource.id;

  console.log(`Processing subscription activated: ${subscriptionId}`);

  try {
    await trackStatusChange(subscriptionId, 'ACTIVE', {
      oldStatus: 'APPROVAL_PENDING',
      reason: 'Customer approved subscription',
      source: 'webhook',
      webhookId: event.id
    });

    // Update customer status
    if (resource.subscriber?.payer_id) {
      await updateCustomerStatus(resource.subscriber.payer_id, 'ACTIVE');
    }

    return {
      handled: true,
      subscriptionId,
      status: 'ACTIVE'
    };
  } catch (error) {
    console.error(`Error handling subscription activated: ${error.message}`);
    throw error;
  }
}

/**
 * Handle subscription cancelled event
 */
async function handleSubscriptionCancelled(event) {
  const { resource } = event;
  const subscriptionId = resource.id;

  console.log(`Processing subscription cancelled: ${subscriptionId}`);

  try {
    await trackStatusChange(subscriptionId, 'CANCELLED', {
      oldStatus: 'ACTIVE',
      reason: resource.status_update_note || 'Subscription cancelled',
      source: 'webhook',
      webhookId: event.id
    });

    // Update customer status
    if (resource.subscriber?.payer_id) {
      await updateCustomerStatus(resource.subscriber.payer_id, 'CANCELLED');
    }

    return {
      handled: true,
      subscriptionId,
      status: 'CANCELLED'
    };
  } catch (error) {
    console.error(`Error handling subscription cancelled: ${error.message}`);
    throw error;
  }
}

/**
 * Handle subscription suspended event
 */
async function handleSubscriptionSuspended(event) {
  const { resource } = event;
  const subscriptionId = resource.id;

  console.log(`Processing subscription suspended: ${subscriptionId}`);

  try {
    await trackStatusChange(subscriptionId, 'SUSPENDED', {
      oldStatus: 'ACTIVE',
      reason: resource.status_update_note || 'Subscription suspended',
      source: 'webhook',
      webhookId: event.id
    });

    // Update customer status
    if (resource.subscriber?.payer_id) {
      await updateCustomerStatus(resource.subscriber.payer_id, 'SUSPENDED');
    }

    return {
      handled: true,
      subscriptionId,
      status: 'SUSPENDED'
    };
  } catch (error) {
    console.error(`Error handling subscription suspended: ${error.message}`);
    throw error;
  }
}

/**
 * Handle subscription updated event
 */
async function handleSubscriptionUpdated(event) {
  const { resource } = event;
  const subscriptionId = resource.id;

  console.log(`Processing subscription updated: ${subscriptionId}`);

  try {
    // Get current status to determine old status
    const history = await getStatusHistory(subscriptionId);
    const currentStatus = history[0]?.newStatus || 'UNKNOWN';

    await trackStatusChange(subscriptionId, 'UPDATED', {
      oldStatus: currentStatus,
      reason: 'Subscription updated',
      source: 'webhook',
      webhookId: event.id,
      updateDetails: resource
    });

    return {
      handled: true,
      subscriptionId,
      status: 'UPDATED'
    };
  } catch (error) {
    console.error(`Error handling subscription updated: ${error.message}`);
    throw error;
  }
}

/**
 * Handle payment completed event
 */
async function handlePaymentCompleted(event) {
  const { resource } = event;
  const paymentId = resource.id;

  console.log(`Processing payment completed: ${paymentId}`);

  try {
    // Extract subscription ID if available
    const subscriptionId = resource.supplementary_data?.related_ids?.subscription_id;

    if (subscriptionId) {
      await trackStatusChange(subscriptionId, 'PAYMENT_RECEIVED', {
        oldStatus: 'ACTIVE',
        reason: 'Payment received',
        source: 'webhook',
        webhookId: event.id,
        paymentId,
        amount: resource.amount?.value,
        currency: resource.amount?.currency_code
      });
    }

    return {
      handled: true,
      paymentId,
      subscriptionId,
      status: 'COMPLETED'
    };
  } catch (error) {
    console.error(`Error handling payment completed: ${error.message}`);
    throw error;
  }
}

/**
 * Handle payment denied event
 */
async function handlePaymentDenied(event) {
  const { resource } = event;
  const paymentId = resource.id;

  console.log(`Processing payment denied: ${paymentId}`);

  try {
    // Extract subscription ID if available
    const subscriptionId = resource.supplementary_data?.related_ids?.subscription_id;

    if (subscriptionId) {
      await trackStatusChange(subscriptionId, 'PAYMENT_FAILED', {
        oldStatus: 'ACTIVE',
        reason: 'Payment denied',
        source: 'webhook',
        webhookId: event.id,
        paymentId,
        statusDetails: resource.status_details
      });
    }

    return {
      handled: true,
      paymentId,
      subscriptionId,
      status: 'DENIED'
    };
  } catch (error) {
    console.error(`Error handling payment denied: ${error.message}`);
    throw error;
  }
}

/**
 * Handle payment refunded event
 */
async function handlePaymentRefunded(event) {
  const { resource } = event;
  const refundId = resource.id;

  console.log(`Processing payment refunded: ${refundId}`);

  try {
    // Extract subscription ID if available
    const subscriptionId = resource.links?.[0]?.href?.match(/subscriptions\/([^/]+)/)?.[1];

    if (subscriptionId) {
      await trackStatusChange(subscriptionId, 'REFUNDED', {
        oldStatus: 'PAYMENT_RECEIVED',
        reason: 'Payment refunded',
        source: 'webhook',
        webhookId: event.id,
        refundId,
        amount: resource.amount?.value,
        currency: resource.amount?.currency_code
      });
    }

    return {
      handled: true,
      refundId,
      subscriptionId,
      status: 'REFUNDED'
    };
  } catch (error) {
    console.error(`Error handling payment refunded: ${error.message}`);
    throw error;
  }
}

export default {
  verifyWebhookSignature,
  isWebhookProcessed,
  markWebhookProcessed,
  processWebhookEvent,
  WEBHOOK_EVENTS,
  WEBHOOK_RETENTION_TIME
};
