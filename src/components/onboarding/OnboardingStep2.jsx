import React, { useState } from 'react';
import { Phone, MessageSquare, CheckCircle } from 'lucide-react';

const OnboardingStep2 = ({ onNext, onBack, initialData = {} }) => {
  const [formData, setFormData] = useState({
    forwardingNumber: initialData.forwardingNumber || '',
    smsEnabled: initialData.smsEnabled || false,
    smsPhoneNumber: initialData.smsPhoneNumber || '',
    ...initialData
  });
  const [loading, setLoading] = useState(false);
  const [testSmsStatus, setTestSmsStatus] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const sendTestSms = async () => {
    if (!formData.smsPhoneNumber) return;
    
    setTestSmsStatus('sending');
    try {
      // TODO: Implement SMS test endpoint
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      setTestSmsStatus('success');
    } catch (error) {
      setTestSmsStatus('error');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/onboarding/${initialData.customerId}/step-2`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        onNext(result);
      } else {
        throw new Error('Failed to save phone configuration');
      }
    } catch (error) {
      console.error('Error saving phone configuration:', error);
      alert('Failed to save phone configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <Phone className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Phone Configuration</h2>
        <p className="text-gray-600">
          Set up call forwarding and SMS notifications for your AI receptionist
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Forwarding Number */}
        <div>
          <label htmlFor="forwardingNumber" className="block text-sm font-medium text-gray-700 mb-2">
            Forwarding Phone Number *
          </label>
          <input
            type="tel"
            id="forwardingNumber"
            name="forwardingNumber"
            value={formData.forwardingNumber}
            onChange={handleInputChange}
            placeholder="+1 (555) 123-4567"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <p className="text-sm text-gray-500 mt-1">
            This number will receive calls when the AI can't handle a request
          </p>
        </div>

        {/* SMS Configuration */}
        <div className="border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <MessageSquare className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">SMS Notifications</h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="smsEnabled"
                name="smsEnabled"
                checked={formData.smsEnabled}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="smsEnabled" className="ml-2 text-sm text-gray-700">
                Enable SMS notifications for new appointments and important calls
              </label>
            </div>

            {formData.smsEnabled && (
              <div>
                <label htmlFor="smsPhoneNumber" className="block text-sm font-medium text-gray-700 mb-2">
                  SMS Phone Number
                </label>
                <div className="flex space-x-2">
                  <input
                    type="tel"
                    id="smsPhoneNumber"
                    name="smsPhoneNumber"
                    value={formData.smsPhoneNumber}
                    onChange={handleInputChange}
                    placeholder="+1 (555) 123-4567"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={sendTestSms}
                    disabled={!formData.smsPhoneNumber || testSmsStatus === 'sending'}
                    className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {testSmsStatus === 'sending' ? 'Sending...' : 'Test SMS'}
                  </button>
                </div>
                
                {testSmsStatus === 'success' && (
                  <div className="flex items-center mt-2 text-green-600">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    <span className="text-sm">Test SMS sent successfully!</span>
                  </div>
                )}
                
                {testSmsStatus === 'error' && (
                  <p className="text-sm text-red-600 mt-2">
                    Failed to send test SMS. Please check the number and try again.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Back
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OnboardingStep2;