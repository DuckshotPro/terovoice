/**
 * PayPal Webhook Retry Handler
 * Implements exponential backoff retry logic for failed webhook processing
 * Includes performance monitoring and error recovery
 */

// Retry configuration
const RETRY_CONFIG = {
  maxRetries: 5,
  initialDelayMs: 1000, // 1 second
  maxDelayMs: 60000, // 1 minute
  backoffMultiplier: 2,
  performanceTargetMs: 30000 // 30 second target
};

// Retry queue for failed webhooks
const retryQueue = new Map();

/**
 * Calculate exponential backoff delay
 * @param {number} retryCount - Current retry attempt number
 * @returns {number} Delay in milliseconds
 */
export function calculateBackoffDelay(retryCount) {
  const delay = Math.min(
    RETRY_CONFIG.initialDelayMs * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount),
    RETRY_CONFIG.maxDelayMs
  );

  // Add jitter to prevent thundering herd
  const jitter = Math.random() * 0.1 * delay;
  return Math.floor(delay + jitter);
}

/**
 * Queue webhook for retry
 * @param {object} webhook - Webhook event to retry
 * @param {number} retryCount - Current retry attempt
 * @param {Error} error - Error that caused the retry
 * @returns {Promise<object>} Retry schedule
 */
export async function queueWebhookForRetry(webhook, retryCount = 0, error = null) {
  if (retryCount >= RETRY_CONFIG.maxRetries) {
    console.error(`Webhook ${webhook.id} exceeded max retries (${RETRY_CONFIG.maxRetries})`);
    return {
      queued: false,
      reason: 'Max retries exceeded',
      webhookId: webhook.id,
      retryCount
    };
  }

  const delay = calculateBackoffDelay(retryCount);
  const scheduledTime = new Date(Date.now() + delay);

  // Store retry information
  const retryRecord = {
    webhookId: webhook.id,
    webhook,
    retryCount: retryCount + 1,
    scheduledTime,
    delay,
    error: error?.message,
    createdAt: new Date(),
    attempts: [
      {
        timestamp: new Date(),
        error: error?.message,
        retryCount
      }
    ]
  };

  retryQueue.set(webhook.id, retryRecord);

  console.log(
    `Webhook ${webhook.id} queued for retry #${retryCount + 1} in ${delay}ms`
  );

  // Schedule retry
  scheduleRetry(webhook.id, delay);

  return {
    queued: true,
    webhookId: webhook.id,
    retryCount: retryCount + 1,
    scheduledTime,
    delay
  };
}

/**
 * Schedule webhook retry
 * @param {string} webhookId - Webhook ID to retry
 * @param {number} delayMs - Delay in milliseconds
 */
function scheduleRetry(webhookId, delayMs) {
  setTimeout(async () => {
    const retryRecord = retryQueue.get(webhookId);

    if (!retryRecord) {
      console.warn(`Retry record not found for webhook ${webhookId}`);
      return;
    }

    try {
      console.log(`Retrying webhook ${webhookId} (attempt ${retryRecord.retryCount})`);

      // Re-process the webhook
      const { processWebhookEvent } = await import('./webhookProcessor.js');
      const result = await processWebhookEvent(retryRecord.webhook);

      if (result.success) {
        console.log(`Webhook ${webhookId} succeeded on retry #${retryRecord.retryCount}`);
        retryQueue.delete(webhookId);
      } else {
        // Queue for another retry
        await queueWebhookForRetry(
          retryRecord.webhook,
          retryRecord.retryCount,
          new Error(result.error)
        );
      }
    } catch (error) {
      console.error(`Error retrying webhook ${webhookId}:`, error);

      // Queue for another retry
      await queueWebhookForRetry(
        retryRecord.webhook,
        retryRecord.retryCount,
        error
      );
    }
  }, delayMs);
}

/**
 * Get retry status for a webhook
 * @param {string} webhookId - Webhook ID
 * @returns {object|null} Retry status or null if not in queue
 */
export function getRetryStatus(webhookId) {
  const record = retryQueue.get(webhookId);

  if (!record) {
    return null;
  }

  return {
    webhookId: record.webhookId,
    retryCount: record.retryCount,
    scheduledTime: record.scheduledTime,
    delay: record.delay,
    error: record.error,
    createdAt: record.createdAt,
    attempts: record.attempts
  };
}

/**
 * Get all pending retries
 * @returns {array} Array of pending retry records
 */
export function getPendingRetries() {
  return Array.from(retryQueue.values()).map(record => ({
    webhookId: record.webhookId,
    retryCount: record.retryCount,
    scheduledTime: record.scheduledTime,
    error: record.error,
    createdAt: record.createdAt
  }));
}

/**
 * Cancel retry for a webhook
 * @param {string} webhookId - Webhook ID
 * @returns {boolean} True if retry was cancelled
 */
export function cancelRetry(webhookId) {
  const removed = retryQueue.delete(webhookId);

  if (removed) {
    console.log(`Cancelled retry for webhook ${webhookId}`);
  }

  return removed;
}

/**
 * Get retry statistics
 * @returns {object} Retry statistics
 */
export function getRetryStats() {
  const records = Array.from(retryQueue.values());

  const stats = {
    totalPending: records.length,
    byRetryCount: {},
    oldestRetry: null,
    newestRetry: null,
    averageRetries: 0
  };

  if (records.length === 0) {
    return stats;
  }

  // Count by retry attempt
  records.forEach(record => {
    const count = record.retryCount;
    stats.byRetryCount[count] = (stats.byRetryCount[count] || 0) + 1;
  });

  // Find oldest and newest
  const sorted = records.sort((a, b) => a.createdAt - b.createdAt);
  stats.oldestRetry = sorted[0].createdAt;
  stats.newestRetry = sorted[sorted.length - 1].createdAt;

  // Calculate average
  stats.averageRetries = records.reduce((sum, r) => sum + r.retryCount, 0) / records.length;

  return stats;
}

/**
 * Monitor webhook processing performance
 * @param {number} processingTimeMs - Processing time in milliseconds
 * @returns {object} Performance analysis
 */
export function monitorPerformance(processingTimeMs) {
  const targetMs = RETRY_CONFIG.performanceTargetMs;
  const percentOfTarget = (processingTimeMs / targetMs) * 100;

  return {
    processingTimeMs,
    targetMs,
    percentOfTarget: Math.round(percentOfTarget),
    withinTarget: processingTimeMs <= targetMs,
    warning: percentOfTarget > 80,
    critical: percentOfTarget > 100
  };
}

/**
 * Clean up old retry records
 * @param {number} maxAgeMs - Maximum age in milliseconds (default: 24 hours)
 * @returns {number} Number of records cleaned up
 */
export function cleanupOldRetries(maxAgeMs = 24 * 60 * 60 * 1000) {
  const now = new Date();
  let cleaned = 0;

  for (const [webhookId, record] of retryQueue.entries()) {
    const age = now - record.createdAt;

    if (age > maxAgeMs) {
      console.warn(`Removing old retry record for webhook ${webhookId} (age: ${age}ms)`);
      retryQueue.delete(webhookId);
      cleaned++;
    }
  }

  return cleaned;
}

export default {
  calculateBackoffDelay,
  queueWebhookForRetry,
  getRetryStatus,
  getPendingRetries,
  cancelRetry,
  getRetryStats,
  monitorPerformance,
  cleanupOldRetries,
  RETRY_CONFIG
};
