/**
 * PayPal Webhook Endpoint Handler
 * Receives and processes PayPal webhook events
 * Implements signature verification and error handling
 */

import express from 'express';
import { verifyWebhookSignature, processWebhookEvent } from '../../services/paypal/webhookProcessor.js';

const router = express.Router();

// Middleware to capture raw body for signature verification
router.use(express.raw({ type: 'application/json' }));

/**
 * POST /api/webhooks/paypal
 * Receive PayPal webhook events
 */
router.post('/', async (req, res) => {
  const startTime = Date.now();

  try {
    // Get raw body for signature verification
    const rawBody = req.body;
    const bodyString = typeof rawBody === 'string' ? rawBody : JSON.stringify(rawBody);

    // Verify webhook signature
    const isValid = verifyWebhookSignature(
      req.headers,
      bodyString,
      process.env.PAYPAL_WEBHOOK_ID
    );

    if (!isValid) {
      console.warn('Invalid webhook signature received');
      return res.status(401).json({
        success: false,
        error: 'Invalid webhook signature'
      });
    }

    // Parse JSON body
    const event = typeof rawBody === 'string' ? JSON.parse(rawBody) : rawBody;

    // Validate event structure
    if (!event.id || !event.event_type || !event.resource) {
      console.warn('Invalid webhook event structure');
      return res.status(400).json({
        success: false,
        error: 'Invalid event structure'
      });
    }

    // Log incoming webhook
    console.log(`Received PayPal webhook: ${event.event_type} (ID: ${event.id})`);

    // Process webhook event
    const result = await processWebhookEvent(event);

    // Return success immediately (PayPal expects response within 30 seconds)
    res.status(200).json({
      success: true,
      webhookId: event.id,
      processingTime: Date.now() - startTime
    });

    // Log processing result
    if (result.success) {
      console.log(`Webhook processed successfully: ${event.event_type} (${result.processingTime}ms)`);
    } else {
      console.error(`Webhook processing failed: ${result.error}`);
    }
  } catch (error) {
    console.error('Error handling PayPal webhook:', error);

    // Return error response
    res.status(500).json({
      success: false,
      error: error.message,
      processingTime: Date.now() - startTime
    });
  }
});

/**
 * GET /api/webhooks/paypal/health
 * Health check endpoint for webhook receiver
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'paypal-webhook-receiver',
    timestamp: new Date().toISOString()
  });
});

export default router;
