import React, { useEffect, useRef, useState } from 'react';
import { X, AlertCircle, Loader } from 'lucide-react';

export const PaymentModal = ({ plan, onSuccess, onClose }) => {
  const paypalContainerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load PayPal script
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${
      import.meta.env.VITE_PAYPAL_CLIENT_ID || 'test'
    }&vault=true&intent=subscription`;
    script.async = true;

    script.onload = () => {
      if (window.paypal) {
        window.paypal
          .Buttons({
            createSubscriptionID: async () => {
              try {
                // Call backend to create subscription plan
                const response = await fetch('/api/billing/create-paypal-subscription', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                  },
                  body: JSON.stringify({
                    plan_id: plan.id,
                    plan_name: plan.name,
                    amount: plan.price,
                  }),
                });

                if (!response.ok) throw new Error('Failed to create subscription');
                const data = await response.json();
                return data.subscription_id;
              } catch (err) {
                setError(err.message);
                throw err;
              }
            },
            onApprove: async (data) => {
              try {
                setIsLoading(true);
                // Verify subscription on backend
                const response = await fetch('/api/billing/verify-paypal-subscription', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                  },
                  body: JSON.stringify({
                    subscription_id: data.subscriptionID,
                  }),
                });

                if (!response.ok) throw new Error('Failed to verify subscription');
                onSuccess(data.subscriptionID);
              } catch (err) {
                setError(err.message);
              } finally {
                setIsLoading(false);
              }
            },
            onError: (err) => {
              setError(err.message || 'Payment failed');
            },
          })
          .render(paypalContainerRef.current);

        setIsLoading(false);
      }
    };

    script.onerror = () => {
      setError('Failed to load PayPal');
      setIsLoading(false);
    };

    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [plan, onSuccess]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Complete Your Purchase</h2>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Plan Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Plan</p>
            <p className="text-lg font-semibold text-gray-900">{plan.name}</p>
            <p className="text-2xl font-bold text-blue-600 mt-2">${plan.price}/month</p>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* PayPal Container */}
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="w-6 h-6 animate-spin text-blue-600" />
            </div>
          ) : (
            <div ref={paypalContainerRef} />
          )}

          {/* Terms */}
          <p className="text-xs text-gray-500 text-center">
            By subscribing, you agree to our Terms of Service and authorize recurring charges to
            your PayPal account.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentModal;
