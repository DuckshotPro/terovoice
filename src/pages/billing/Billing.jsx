import React, { useEffect, useState } from 'react';
import { useBilling } from '../../contexts/BillingContext';
import { Check, AlertCircle, Loader } from 'lucide-react';
import PricingPlans from '../../components/billing/PricingPlans';
import SubscriptionDetails from '../../components/billing/SubscriptionDetails';
import InvoiceHistory from '../../components/billing/InvoiceHistory';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 299,
    description: 'Perfect for solo practitioners',
    features: [
      'Unlimited minutes',
      '1 AI receptionist',
      'Basic analytics',
      'Email support',
      'Up to 100 calls/month',
    ],
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 499,
    description: 'For growing businesses',
    features: [
      'Unlimited minutes',
      '3 AI receptionists',
      'Advanced analytics',
      'Priority support',
      'Up to 500 calls/month',
      'Custom voice cloning',
    ],
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 999,
    description: 'For large operations',
    features: [
      'Unlimited minutes',
      'Unlimited AI receptionists',
      'Full analytics suite',
      '24/7 phone support',
      'Unlimited calls',
      'Custom integrations',
      'Dedicated account manager',
    ],
  },
];

export const Billing = () => {
  const { subscription, invoices, isLoading, error, fetchSubscription, fetchInvoices } =
    useBilling();
  const [activeTab, setActiveTab] = useState('plans');

  useEffect(() => {
    fetchSubscription();
    fetchInvoices();
  }, [fetchSubscription, fetchInvoices]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
        <p className="text-gray-600 mt-2">Manage your subscription and view invoices</p>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('plans')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'plans'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Plans
        </button>
        <button
          onClick={() => setActiveTab('subscription')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'subscription'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Current Subscription
        </button>
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'invoices'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Invoices
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-6 h-6 animate-spin text-blue-600" />
        </div>
      ) : (
        <>
          {activeTab === 'plans' && <PricingPlans plans={PLANS} currentPlan={subscription?.plan_id} />}
          {activeTab === 'subscription' && subscription && (
            <SubscriptionDetails subscription={subscription} />
          )}
          {activeTab === 'subscription' && !subscription && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <p className="text-blue-900 mb-4">You don't have an active subscription yet.</p>
              <button
                onClick={() => setActiveTab('plans')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
              >
                Choose a Plan
              </button>
            </div>
          )}
          {activeTab === 'invoices' && <InvoiceHistory invoices={invoices} />}
        </>
      )}
    </div>
  );
};

export default Billing;
