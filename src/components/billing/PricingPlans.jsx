import React, { useState } from 'react';
import { useBilling } from '../../contexts/BillingContext';
import { Check, Loader } from 'lucide-react';
import PaymentModal from './PaymentModal';

export const PricingPlans = ({ plans, currentPlan }) => {
  const { createSubscription, isLoading } = useBilling();
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = async (paymentMethodId) => {
    try {
      await createSubscription(selectedPlan.id, paymentMethodId);
      setShowPaymentModal(false);
      setSelectedPlan(null);
    } catch (err) {
      console.error('Subscription creation failed:', err);
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`rounded-lg border-2 transition-all ${
              plan.popular
                ? 'border-blue-600 shadow-lg scale-105'
                : 'border-gray-200 hover:border-gray-300'
            } p-6 bg-white`}
          >
            {plan.popular && (
              <div className="mb-4">
                <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                  MOST POPULAR
                </span>
              </div>
            )}

            <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
            <p className="text-gray-600 text-sm mb-4">{plan.description}</p>

            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
              <span className="text-gray-600">/month</span>
            </div>

            <button
              onClick={() => handleSelectPlan(plan)}
              disabled={isLoading || currentPlan === plan.id}
              className={`w-full py-2 rounded-lg font-medium transition-colors mb-6 ${
                currentPlan === plan.id
                  ? 'bg-gray-100 text-gray-600 cursor-not-allowed'
                  : plan.popular
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
              }`}
            >
              {isLoading ? (
                <Loader className="w-4 h-4 animate-spin inline mr-2" />
              ) : currentPlan === plan.id ? (
                'Current Plan'
              ) : (
                'Choose Plan'
              )}
            </button>

            <div className="space-y-3">
              {plan.features.map((feature, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {showPaymentModal && selectedPlan && (
        <PaymentModal
          plan={selectedPlan}
          onSuccess={handlePaymentSuccess}
          onClose={() => {
            setShowPaymentModal(false);
            setSelectedPlan(null);
          }}
        />
      )}
    </>
  );
};

export default PricingPlans;
