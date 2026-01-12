import React from 'react';

/**
 * PayPal Subscription Button Component
 * 
 * Handles PayPal subscription integration for AI Receptionist SaaS
 */

const PayPalButton = ({ plan, className, children }) => {
  const handlePayPalSubscription = () => {
    // PayPal Plan IDs (these would be configured in your PayPal dashboard)
    const planIds = {
      'Solo Pro': 'P-299-SOLO-PRO-MONTHLY',
      'Professional': 'P-499-PROFESSIONAL-MONTHLY', 
      'Enterprise': 'P-799-ENTERPRISE-MONTHLY'
    };

    const planId = planIds[plan];
    
    if (planId) {
      // Redirect to PayPal subscription page
      window.open(`https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=${planId}`, '_blank');
    } else {
      // Fallback for enterprise or custom plans
      window.location.href = 'mailto:sales@tero-ai.com?subject=Enterprise Plan Inquiry';
    }
  };

  return (
    <button
      onClick={handlePayPalSubscription}
      className={className}
    >
      {children}
    </button>
  );
};

export default PayPalButton;