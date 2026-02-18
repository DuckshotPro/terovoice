import React, { useState, useEffect } from 'react';
import { Calendar, CheckCircle, ExternalLink, AlertCircle } from 'lucide-react';

const OnboardingStep4 = ({ onNext, onBack, initialData = {} }) => {
  const [formData, setFormData] = useState({
    calendarProvider: initialData.calendarProvider || '',
    calendarConnected: initialData.calendarConnected || false,
    ...initialData
  });
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('idle'); // idle, connecting, connected, error

  const calendarProviders = [
    {
      id: 'google',
      name: 'Google Calendar',
      description: 'Connect with Google Calendar for appointment scheduling',
      icon: '📅'
    },
    {
      id: 'outlook',
      name: 'Microsoft Outlook',
      description: 'Connect with Outlook Calendar for appointment scheduling',
      icon: '📆'
    },
    {
      id: 'apple',
      name: 'Apple Calendar',
      description: 'Connect with Apple Calendar via CalDAV',
      icon: '🍎'
    },
    {
      id: 'skip',
      name: 'Skip for Now',
      description: 'You can set up calendar integration later in your portal',
      icon: '⏭️'
    }
  ];

  const handleProviderSelect = (providerId) => {
    setFormData(prev => ({
      ...prev,
      calendarProvider: providerId,
      calendarConnected: false
    }));
    setConnectionStatus('idle');
  };

  const connectCalendar = async () => {
    if (!formData.calendarProvider || formData.calendarProvider === 'skip') {
      return;
    }

    setConnectionStatus('connecting');
    setLoading(true);

    try {
      // TODO: Implement OAuth flow for calendar providers
      // For now, simulate the connection process

      if (formData.calendarProvider === 'google') {
        // Simulate Google OAuth flow
        const authUrl = `https://accounts.google.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=${encodeURIComponent(window.location.origin)}/auth/google&scope=https://www.googleapis.com/auth/calendar&response_type=code`;

        // In a real implementation, you would:
        // 1. Open popup window with authUrl
        // 2. Handle the OAuth callback
        // 3. Exchange code for access token
        // 4. Store tokens securely

        // For demo purposes, simulate success after delay
        await new Promise(resolve => setTimeout(resolve, 3000));

        setFormData(prev => ({
          ...prev,
          calendarConnected: true
        }));
        setConnectionStatus('connected');
      } else {
        // Simulate other providers
        await new Promise(resolve => setTimeout(resolve, 2000));
        setFormData(prev => ({
          ...prev,
          calendarConnected: true
        }));
        setConnectionStatus('connected');
      }
    } catch (error) {
      console.error('Calendar connection failed:', error);
      setConnectionStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // For skip option, mark as completed without connection
      const dataToSend = {
        ...formData,
        calendarConnected: formData.calendarProvider === 'skip' ? false : formData.calendarConnected
      };

      const response = await fetch(`/api/onboarding/${initialData.customerId}/step-4`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      });

      if (response.ok) {
        const result = await response.json();
        onNext(result);
      } else {
        throw new Error('Failed to save calendar configuration');
      }
    } catch (error) {
      console.error('Error saving calendar configuration:', error);
      alert('Failed to save calendar configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = formData.calendarProvider === 'skip' ||
                    (formData.calendarProvider && formData.calendarConnected);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <Calendar className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Calendar Integration</h2>
        <p className="text-gray-600">
          Connect your calendar so your AI can schedule appointments automatically
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Calendar Provider Selection */}
        <div className="grid gap-4">
          {calendarProviders.map((provider) => (
            <div
              key={provider.id}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                formData.calendarProvider === provider.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => handleProviderSelect(provider.id)}
            >
              <div className="flex items-center">
                <div className="text-2xl mr-4">{provider.icon}</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{provider.name}</h3>
                  <p className="text-sm text-gray-600">{provider.description}</p>
                </div>
                {formData.calendarProvider === provider.id && (
                  <CheckCircle className="w-6 h-6 text-blue-600" />
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Connection Status */}
        {formData.calendarProvider && formData.calendarProvider !== 'skip' && (
          <div className="border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Connect to {calendarProviders.find(p => p.id === formData.calendarProvider)?.name}
            </h3>

            {connectionStatus === 'idle' && (
              <div>
                <p className="text-sm text-gray-600 mb-4">
                  Click the button below to connect your calendar. You'll be redirected to authorize access.
                </p>
                <button
                  type="button"
                  onClick={connectCalendar}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Connect Calendar
                </button>
              </div>
            )}

            {connectionStatus === 'connecting' && (
              <div className="flex items-center text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span>Connecting to your calendar...</span>
              </div>
            )}

            {connectionStatus === 'connected' && (
              <div className="flex items-center text-green-600">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span>Successfully connected to your calendar!</span>
              </div>
            )}

            {connectionStatus === 'error' && (
              <div className="flex items-center text-red-600">
                <AlertCircle className="w-5 h-5 mr-2" />
                <span>Failed to connect. Please try again.</span>
              </div>
            )}
          </div>
        )}

        {/* Skip Option Info */}
        {formData.calendarProvider === 'skip' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
              <div>
                <h4 className="text-sm font-medium text-yellow-800">Calendar Integration Skipped</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  You can set up calendar integration later in your customer portal.
                  Your AI will still be able to take messages and collect contact information.
                </p>
              </div>
            </div>
          </div>
        )}

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
            disabled={loading || !canProceed}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OnboardingStep4;