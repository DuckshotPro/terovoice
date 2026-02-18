/**
 * PayPal Subscription Management Service
 * Handles subscription creation, updates, cancellations, and status tracking
 * Uses real PayPal API via PayPalAPIClient
 */

import PayPalAPIClient from './apiClient.js';

// Initialize PayPal API client from environment variables
const paypalClient = new PayPalAPIClient(
  process.env.PAYPAL_CLIENT_ID,
  process.env.PAYPAL_CLIENT_SECRET,
  process.env.PAYPAL_ENVIRONMENT || 'sandbox'
);

// Subscription plan definitions for AI Receptionist SaaS
const SUBSCRIPTION_PLANS = {
  SOLO_PRO: {
    id: process.env.PAYPAL_PLAN_ID_SOLO_PRO || 'plan_solo_pro',
    name: 'Solo Pro',
    price: 299,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'Perfect for solo practitioners',
    features: [
      'Unlimited minutes',
      'Voice cloning',
      'Custom scripts',
      'Basic analytics',
      'Email support'
    ]
  },
  PROFESSIONAL: {
    id: process.env.PAYPAL_PLAN_ID_PROFESSIONAL || 'plan_professional',
    name: 'Professional',
    price: 499,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'For growing businesses',
    features: [
      'Unlimited minutes',
      'Voice cloning',
      'Custom scripts',
      'Advanced analytics',
      'Priority support',
      'Multi-location support'
    ]
  },
  ENTERPRISE: {
    id: process.env.PAYPAL_PLAN_ID_ENTERPRISE || 'plan_enterprise',
    name: 'Enterprise',
    price: 799,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'For large organizations',
    features: [
      'Unlimited minutes',
      'Voice cloning',
      'Custom scripts',
      'Advanced analytics',
      'Dedicated support',
      'Multi-location support',
      'Custom integrations',
      'SLA guarantee'
    ]
  }
};

/**
 * Create a new subscription for a customer
 * @param {string} customerId - PayPal customer ID
 * @param {string} planId - Plan identifier (SOLO_PRO, PROFESSIONAL, ENTERPRISE)
 * @param {object} customerData - Customer information
 * @returns {Promise<object>} Subscription details
 */
export async function createSubscription(customerId, planId, customerData) {
  const plan = SUBSCRIPTION_PLANS[planId];

  if (!plan) {
    throw new Error(`Invalid plan ID: ${planId}`);
  }

  try {
    // Call real PayPal API
    const subscription = await paypalClient.createSubscription({
      planId: plan.id,
      firstName: customerData.firstName,
      lastName: customerData.lastName,
      email: customerData.email,
      payerId: customerId,
      returnUrl: customerData.returnUrl,
      cancelUrl: customerData.cancelUrl
    });

    return {
      subscriptionId: subscription.subscriptionId,
      status: subscription.status,
      planId: planId,
      customerId: customerId,
      createdAt: subscription.createdAt,
      approvalUrl: subscription.links?.find(l => l.rel === 'approve')?.href
    };
  } catch (error) {
    console.error('Error creating subscription:', error);
    throw error;
  }
}

/**
 * Get subscription details
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<object>} Subscription details
 */
export async function getSubscription(subscriptionId) {
  try {
    // Call real PayPal API
    const subscription = await paypalClient.getSubscription(subscriptionId);

    return {
      subscriptionId: subscription.subscriptionId,
      status: subscription.status,
      planId: subscription.planId,
      subscriber: subscription.subscriber,
      billingInfo: subscription.billingInfo,
      startTime: subscription.startTime,
      nextBillingTime: subscription.nextBillingTime,
      createdAt: subscription.createdAt,
      updatedAt: subscription.updatedAt
    };
  } catch (error) {
    console.error('Error getting subscription:', error);
    throw error;
  }
}

/**
 * Cancel a subscription
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} reason - Cancellation reason
 * @returns {Promise<object>} Cancellation confirmation
 */
export async function cancelSubscription(subscriptionId, reason = 'Customer requested') {
  try {
    // Call real PayPal API
    const result = await paypalClient.cancelSubscription(subscriptionId, reason);

    return {
      subscriptionId: result.subscriptionId,
      status: result.status,
      cancelledAt: result.cancelledAt,
      reason: result.reason
    };
  } catch (error) {
    console.error('Error cancelling subscription:', error);
    throw error;
  }
}

/**
 * Update subscription (e.g., plan upgrade/downgrade)
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} newPlanId - New plan identifier
 * @returns {Promise<object>} Updated subscription details
 */
export async function updateSubscription(subscriptionId, newPlanId) {
  const newPlan = SUBSCRIPTION_PLANS[newPlanId];

  if (!newPlan) {
    throw new Error(`Invalid plan ID: ${newPlanId}`);
  }

  try {
    // Call real PayPal API
    const subscription = await paypalClient.updateSubscription(subscriptionId, {
      planId: newPlan.id
    });

    return {
      subscriptionId: subscription.subscriptionId,
      status: subscription.status,
      newPlanId: newPlanId,
      newPrice: newPlan.price,
      updatedAt: subscription.updatedAt
    };
  } catch (error) {
    console.error('Error updating subscription:', error);
    throw error;
  }
}

/**
 * List all subscriptions
 * @param {object} filters - Filter options
 * @returns {Promise<array>} Array of subscriptions
 */
export async function listSubscriptions(filters = {}) {
  try {
    // Call real PayPal API
    const result = await paypalClient.listSubscriptions(filters);

    return {
      subscriptions: result.subscriptions.map(sub => ({
        subscriptionId: sub.id,
        status: sub.status,
        planId: sub.plan_id,
        createdAt: sub.create_time,
        updatedAt: sub.update_time
      })),
      total: result.total,
      pages: result.pages,
      links: result.links
    };
  } catch (error) {
    console.error('Error listing subscriptions:', error);
    throw error;
  }
}

/**
 * Get plan details
 * @param {string} planId - Plan identifier
 * @returns {object} Plan details
 */
export function getPlanDetails(planId) {
  return SUBSCRIPTION_PLANS[planId] || null;
}

/**
 * Get all available plans
 * @returns {object} All subscription plans
 */
export function getAllPlans() {
  return SUBSCRIPTION_PLANS;
}

/**
 * Create a billing plan in PayPal
 * @param {string} planId - Plan identifier (SOLO_PRO, PROFESSIONAL, ENTERPRISE)
 * @returns {Promise<object>} Created plan
 */
export async function createBillingPlan(planId) {
  const plan = SUBSCRIPTION_PLANS[planId];

  if (!plan) {
    throw new Error(`Invalid plan ID: ${planId}`);
  }

  try {
    // Call real PayPal API
    const createdPlan = await paypalClient.createPlan({
      productId: process.env.PAYPAL_PRODUCT_ID || 'PROD_TERO_VOICE',
      name: plan.name,
      description: plan.description,
      price: plan.price,
      currency: plan.currency,
      interval: plan.interval,
      intervalCount: plan.intervalCount
    });

    return {
      planId: createdPlan.planId,
      status: createdPlan.status,
      createdAt: createdPlan.createdAt
    };
  } catch (error) {
    console.error('Error creating billing plan:', error);
    throw error;
  }
}

/**
 * Get billing plan details from PayPal
 * @param {string} paypalPlanId - PayPal plan ID
 * @returns {Promise<object>} Plan details
 */
export async function getBillingPlan(paypalPlanId) {
  try {
    // Call real PayPal API
    const plan = await paypalClient.getPlan(paypalPlanId);

    return {
      planId: plan.planId,
      productId: plan.productId,
      name: plan.name,
      description: plan.description,
      status: plan.status,
      billingCycles: plan.billingCycles,
      paymentPreferences: plan.paymentPreferences,
      createdAt: plan.createdAt,
      updatedAt: plan.updatedAt
    };
  } catch (error) {
    console.error('Error getting billing plan:', error);
    throw error;
  }
}

export default {
  createSubscription,
  getSubscription,
  cancelSubscription,
  updateSubscription,
  listSubscriptions,
  getPlanDetails,
  getAllPlans,
  createBillingPlan,
  getBillingPlan,
  SUBSCRIPTION_PLANS,
  paypalClient
};
