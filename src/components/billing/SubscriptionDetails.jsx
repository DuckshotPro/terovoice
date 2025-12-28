import React, { useState } from 'react';
import { useBilling } from '../../contexts/BillingContext';
import { AlertCircle, Loader, Calendar, DollarSign, CheckCircle } from 'lucide-react';

export const SubscriptionDetails = ({ subscription }) => {
  const { cancelSubscription, isLoading, error } = useBilling();
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  const handleCancelSubscription = async () => {
    try {
      await cancelSubscription();
      setShowCancelConfirm(false);
    } catch (err) {
      console.error('Failed to cancel subscription:', err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Current Plan Card */}
      <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-600">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {subscription.plan_name}
            </h3>
            <p className="text-gray-600">Active subscription</p>
          </div>
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Monthly Price</p>
            <p className="text-2xl font-bold text-gray-900">${subscription.amount}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="w-4 h-4 text-gray-600" />
              <p className="text-sm text-gray-600">Renewal Date</p>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {formatDate(subscription.next_billing_date)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="w-4 h-4 text-gray-600" />
              <p className="text-sm text-gray-600">Status</p>
            </div>
            <p className="text-lg font-semibold text-green-600 capitalize">
              {subscription.status}
            </p>
          </div>
        </div>

        {/* Subscription Details */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Subscription ID</span>
            <span className="font-mono text-sm text-gray-900">{subscription.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Started</span>
            <span className="text-gray-900">{formatDate(subscription.created_at)}</span>
          </div>
          {subscription.canceled_at && (
            <div className="flex justify-between">
              <span className="text-gray-600">Canceled</span>
              <span className="text-gray-900">{formatDate(subscription.canceled_at)}</span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
            Upgrade Plan
          </button>
          <button
            onClick={() => setShowCancelConfirm(true)}
            className="flex-1 border border-red-300 text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Cancel Subscription
          </button>
        </div>
      </div>

      {/* Cancel Confirmation Modal */}
      {showCancelConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Cancel Subscription?</h3>
            <p className="text-gray-600 mb-6">
              Your subscription will be canceled at the end of the current billing period. You'll
              lose access to all features.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCancelConfirm(false)}
                className="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg font-medium"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleCancelSubscription}
                disabled={isLoading}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Canceling...
                  </>
                ) : (
                  'Cancel'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionDetails;
