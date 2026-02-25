/**
 * PayPal API Client
 * Handles OAuth token management and all PayPal API calls
 * Replaces mock implementations with real PayPal API integration
 */

import axios from 'axios';

// PayPal API endpoints
const SANDBOX_BASE_URL = 'https://api.sandbox.paypal.com';
const PRODUCTION_BASE_URL = 'https://api.paypal.com';

/**
 * PayPal API Client
 * Manages authentication and API calls to PayPal
 */
class PayPalAPIClient {
  constructor(clientId, clientSecret, environment = 'sandbox') {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.environment = environment;
    this.baseUrl = environment === 'sandbox' ? SANDBOX_BASE_URL : PRODUCTION_BASE_URL;

    // Token management
    this.accessToken = null;
    this.tokenExpiry = null;

    // Create axios instance with base configuration
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await this.getAccessToken();
        config.headers.Authorization = `Bearer ${token}`;
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleAPIError(error)
    );
  }

  /**
   * Get or refresh access token
   * @returns {Promise<string>} Access token
   */
  async getAccessToken() {
    // Return existing token if still valid
    if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }

    try {
      const response = await axios.post(
        `${this.baseUrl}/v1/oauth2/token`,
        'grant_type=client_credentials',
        {
          auth: {
            username: this.clientId,
            password: this.clientSecret
          },
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      this.accessToken = response.data.access_token;
      // Set expiry to 5 minutes before actual expiry for safety margin
      this.tokenExpiry = Date.now() + (response.data.expires_in - 300) * 1000;

      return this.accessToken;
    } catch (error) {
      console.error('Failed to get PayPal access token:', error.message);
      throw new Error('PayPal authentication failed');
    }
  }

  /**
   * Create a subscription
   * @param {object} subscriptionData - Subscription details
   * @returns {Promise<object>} Created subscription
   */
  async createSubscription(subscriptionData) {
    try {
      const response = await this.client.post('/v1/billing/subscriptions', {
        plan_id: subscriptionData.planId,
        subscriber: {
          name: {
            given_name: subscriptionData.firstName,
            surname: subscriptionData.lastName
          },
          email_address: subscriptionData.email,
          payer_id: subscriptionData.payerId
        },
        application_context: {
          brand_name: 'Tero Voice',
          locale: 'en-US',
          user_action: 'SUBSCRIBE_NOW',
          return_url: subscriptionData.returnUrl || 'https://terovoice.com/success',
          cancel_url: subscriptionData.cancelUrl || 'https://terovoice.com/cancel'
        }
      });

      return {
        subscriptionId: response.data.id,
        status: response.data.status,
        links: response.data.links,
        createdAt: new Date().toISOString()
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to create subscription');
    }
  }

  /**
   * Get subscription details
   * @param {string} subscriptionId - PayPal subscription ID
   * @returns {Promise<object>} Subscription details
   */
  async getSubscription(subscriptionId) {
    try {
      const response = await this.client.get(`/v1/billing/subscriptions/${subscriptionId}`);

      return {
        subscriptionId: response.data.id,
        status: response.data.status,
        planId: response.data.plan_id,
        subscriber: response.data.subscriber,
        billingInfo: response.data.billing_info,
        startTime: response.data.start_time,
        nextBillingTime: response.data.next_billing_time,
        createdAt: response.data.create_time,
        updatedAt: response.data.update_time
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to get subscription');
    }
  }

  /**
   * Cancel a subscription
   * @param {string} subscriptionId - PayPal subscription ID
   * @param {string} reason - Cancellation reason
   * @returns {Promise<void>}
   */
  async cancelSubscription(subscriptionId, reason = 'Customer requested') {
    try {
      await this.client.post(
        `/v1/billing/subscriptions/${subscriptionId}/cancel`,
        { reason: reason }
      );

      return {
        subscriptionId: subscriptionId,
        status: 'CANCELLED',
        cancelledAt: new Date().toISOString(),
        reason: reason
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to cancel subscription');
    }
  }

  /**
   * Update subscription (e.g., plan change)
   * @param {string} subscriptionId - PayPal subscription ID
   * @param {object} updates - Updates to apply
   * @returns {Promise<object>} Updated subscription
   */
  async updateSubscription(subscriptionId, updates) {
    try {
      const patchOps = [];

      if (updates.planId) {
        patchOps.push({
          op: 'replace',
          path: '/plan_id',
          value: updates.planId
        });
      }

      if (updates.status) {
        patchOps.push({
          op: 'replace',
          path: '/status',
          value: updates.status
        });
      }

      if (patchOps.length === 0) {
        throw new Error('No updates provided');
      }

      await this.client.patch(
        `/v1/billing/subscriptions/${subscriptionId}`,
        patchOps
      );

      // Return updated subscription
      return this.getSubscription(subscriptionId);
    } catch (error) {
      throw this.handleError(error, 'Failed to update subscription');
    }
  }

  /**
   * List subscriptions
   * @param {object} filters - Filter options
   * @returns {Promise<array>} Array of subscriptions
   */
  async listSubscriptions(filters = {}) {
    try {
      const params = new URLSearchParams();

      if (filters.planId) params.append('plan_id', filters.planId);
      if (filters.status) params.append('status', filters.status);
      if (filters.pageSize) params.append('page_size', filters.pageSize);
      if (filters.page) params.append('page', filters.page);

      const response = await this.client.get('/v1/billing/subscriptions', { params });

      return {
        subscriptions: response.data.subscriptions || [],
        total: response.data.total_items,
        pages: response.data.total_pages,
        links: response.data.links
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to list subscriptions');
    }
  }

  /**
   * Create a billing plan
   * @param {object} planData - Plan details
   * @returns {Promise<object>} Created plan
   */
  async createPlan(planData) {
    try {
      const response = await this.client.post('/v1/billing/plans', {
        product_id: planData.productId,
        name: planData.name,
        description: planData.description,
        status: 'ACTIVE',
        billing_cycles: [
          {
            frequency: {
              interval_unit: planData.interval || 'MONTH',
              interval_count: planData.intervalCount || 1
            },
            tenure_type: 'REGULAR',
            sequence: 1,
            total_cycles: 0, // Infinite
            pricing_scheme: {
              fixed_price: {
                value: planData.price.toString(),
                currency_code: planData.currency || 'USD'
              }
            }
          }
        ],
        payment_preferences: {
          auto_bill_outstanding: true,
          setup_fee_failure_action: 'CONTINUE',
          payment_failure_threshold: 3
        }
      });

      return {
        planId: response.data.id,
        status: response.data.status,
        createdAt: response.data.create_time,
        updatedAt: response.data.update_time
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to create plan');
    }
  }

  /**
   * Get plan details
   * @param {string} planId - PayPal plan ID
   * @returns {Promise<object>} Plan details
   */
  async getPlan(planId) {
    try {
      const response = await this.client.get(`/v1/billing/plans/${planId}`);

      return {
        planId: response.data.id,
        productId: response.data.product_id,
        name: response.data.name,
        description: response.data.description,
        status: response.data.status,
        billingCycles: response.data.billing_cycles,
        paymentPreferences: response.data.payment_preferences,
        createdAt: response.data.create_time,
        updatedAt: response.data.update_time
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to get plan');
    }
  }

  /**
   * Update a plan
   * @param {string} planId - PayPal plan ID
   * @param {object} updates - Updates to apply
   * @returns {Promise<object>} Updated plan
   */
  async updatePlan(planId, updates) {
    try {
      const patchOps = [];

      if (updates.name) {
        patchOps.push({
          op: 'replace',
          path: '/name',
          value: updates.name
        });
      }

      if (updates.description) {
        patchOps.push({
          op: 'replace',
          path: '/description',
          value: updates.description
        });
      }

      if (updates.status) {
        patchOps.push({
          op: 'replace',
          path: '/status',
          value: updates.status
        });
      }

      if (patchOps.length === 0) {
        throw new Error('No updates provided');
      }

      await this.client.patch(`/v1/billing/plans/${planId}`, patchOps);

      // Return updated plan
      return this.getPlan(planId);
    } catch (error) {
      throw this.handleError(error, 'Failed to update plan');
    }
  }

  /**
   * Verify webhook signature
   * @param {string} webhookId - PayPal webhook ID
   * @param {object} webhookEvent - Webhook event data
   * @param {string} transmissionId - Transmission ID from header
   * @param {string} transmissionTime - Transmission time from header
   * @param {string} certUrl - Certificate URL from header
   * @param {string} authAlgo - Auth algorithm from header
   * @param {string} transmissionSig - Transmission signature from header
   * @returns {Promise<boolean>} Is signature valid
   */
  async verifyWebhookSignature(
    webhookId,
    webhookEvent,
    transmissionId,
    transmissionTime,
    certUrl,
    authAlgo,
    transmissionSig
  ) {
    try {
      const response = await this.client.post(
        '/v1/notifications/verify-webhook-signature',
        {
          transmission_id: transmissionId,
          transmission_time: transmissionTime,
          cert_url: certUrl,
          auth_algo: authAlgo,
          transmission_sig: transmissionSig,
          webhook_id: webhookId,
          webhook_event: webhookEvent
        }
      );

      return response.data.verification_status === 'SUCCESS';
    } catch (error) {
      console.error('Webhook signature verification failed:', error.message);
      return false;
    }
  }

  /**
   * Get webhook events
   * @param {string} webhookId - PayPal webhook ID
   * @param {object} filters - Filter options
   * @returns {Promise<array>} Array of webhook events
   */
  async getWebhookEvents(webhookId, filters = {}) {
    try {
      const params = new URLSearchParams();

      if (filters.eventType) params.append('event_type', filters.eventType);
      if (filters.startTime) params.append('start_time', filters.startTime);
      if (filters.endTime) params.append('end_time', filters.endTime);
      if (filters.pageSize) params.append('page_size', filters.pageSize);
      if (filters.page) params.append('page', filters.page);

      const response = await this.client.get(
        `/v1/notifications/webhooks/${webhookId}/events`,
        { params }
      );

      return {
        events: response.data.events || [],
        total: response.data.total_items,
        pages: response.data.total_pages,
        links: response.data.links
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to get webhook events');
    }
  }

  /**
   * Create a webhook
   * @param {object} webhookData - Webhook configuration
   * @returns {Promise<object>} Created webhook
   */
  async createWebhook(webhookData) {
    try {
      const response = await this.client.post('/v1/notifications/webhooks', {
        url: webhookData.url,
        event_types: webhookData.eventTypes || [
          { name: 'BILLING.SUBSCRIPTION.CREATED' },
          { name: 'BILLING.SUBSCRIPTION.ACTIVATED' },
          { name: 'BILLING.SUBSCRIPTION.CANCELLED' },
          { name: 'BILLING.SUBSCRIPTION.UPDATED' },
          { name: 'PAYMENT.CAPTURE.COMPLETED' },
          { name: 'PAYMENT.CAPTURE.DENIED' },
          { name: 'PAYMENT.CAPTURE.REFUNDED' },
          { name: 'PAYMENT.CAPTURE.REVERSED' }
        ]
      });

      return {
        webhookId: response.data.id,
        url: response.data.url,
        eventTypes: response.data.event_types,
        createdAt: response.data.create_time,
        updatedAt: response.data.update_time
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to create webhook');
    }
  }

  /**
   * Get webhook details
   * @param {string} webhookId - PayPal webhook ID
   * @returns {Promise<object>} Webhook details
   */
  async getWebhook(webhookId) {
    try {
      const response = await this.client.get(`/v1/notifications/webhooks/${webhookId}`);

      return {
        webhookId: response.data.id,
        url: response.data.url,
        eventTypes: response.data.event_types,
        createdAt: response.data.create_time,
        updatedAt: response.data.update_time
      };
    } catch (error) {
      throw this.handleError(error, 'Failed to get webhook');
    }
  }

  /**
   * Update webhook
   * @param {string} webhookId - PayPal webhook ID
   * @param {object} updates - Updates to apply
   * @returns {Promise<object>} Updated webhook
   */
  async updateWebhook(webhookId, updates) {
    try {
      const patchOps = [];

      if (updates.url) {
        patchOps.push({
          op: 'replace',
          path: '/url',
          value: updates.url
        });
      }

      if (updates.eventTypes) {
        patchOps.push({
          op: 'replace',
          path: '/event_types',
          value: updates.eventTypes
        });
      }

      if (patchOps.length === 0) {
        throw new Error('No updates provided');
      }

      await this.client.patch(`/v1/notifications/webhooks/${webhookId}`, patchOps);

      // Return updated webhook
      return this.getWebhook(webhookId);
    } catch (error) {
      throw this.handleError(error, 'Failed to update webhook');
    }
  }

  /**
   * Handle API errors
   * @param {Error} error - Axios error
   * @param {string} context - Error context
   * @returns {Error} Formatted error
   */
  handleError(error, context) {
    if (error.response) {
      // PayPal API error response
      const status = error.response.status;
      const data = error.response.data;

      const message = data.message || data.error_description || 'Unknown error';
      const details = data.details || [];

      const err = new Error(`${context}: ${message}`);
      err.status = status;
      err.details = details;
      err.paypalError = data;

      return err;
    } else if (error.request) {
      // Request made but no response
      const err = new Error(`${context}: No response from PayPal`);
      err.status = 503;
      return err;
    } else {
      // Error in request setup
      const err = new Error(`${context}: ${error.message}`);
      err.status = 500;
      return err;
    }
  }

  /**
   * Handle API errors from interceptor
   * @param {Error} error - Axios error
   * @returns {Promise} Rejected promise
   */
  handleAPIError(error) {
    if (error.response?.status === 401) {
      // Token expired, clear it so next request will refresh
      this.accessToken = null;
      this.tokenExpiry = null;
    }

    return Promise.reject(error);
  }
}

export default PayPalAPIClient;
