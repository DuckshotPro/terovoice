import React, { useState, useEffect } from 'react';
import { CheckCircle, ExternalLink, Phone, Mail, Settings, BarChart3 } from 'lucide-react';

const OnboardingStep7 = ({ initialData = {} }) => {
  const [loading, setLoading] = useState(false);
  const [activationStatus, setActivationStatus] = useState('activating'); // activating, success, error

  useEffect(() => {
    // Simulate activation process
    const activateService = async () => {
      try {
        setLoading(true);
        
        // Call the completion endpoint
        const response = await fetch(`/api/onboarding/${initialData.customerId}/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const result = await response.json();
          setActivationStatus('success');
        } else {
          throw new Error('Activation failed');
        }
      } catch (error) {
        console.error('Activation error:', error);
        setActivationStatus('error');
      } finally {
        setLoading(false);
      }
    };

    // Start activation after a short delay
    const timer = setTimeout(activateService, 2000);
    return () => clearTimeout(timer);
  }, [initialData.customerId]);

  const portalUrl = `/portal/${initialData.customerId}`;
  const testPhoneNumber = initialData.businessPhone || '+1 (555) 123-4567';

  if (activationStatus === 'activating') {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-8">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Activating Your AI Receptionist</h2>
          <p className="text-gray-600">
            Please wait while we set up your service...
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="space-y-3 text-left">
            <div className="flex items-center text-green-600">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>Configuring phone routing</span>
            </div>
            <div className="flex items-center text-green-600">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>Setting up AI voice model</span>
            </div>
            <div className="flex items-center text-blue-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span>Activating customer portal</span>
            </div>
            <div className="flex items-center text-gray-400">
              <div className="w-5 h-5 mr-2"></div>
              <span>Sending welcome email</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (activationStatus === 'error') {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-red-600 text-2xl">⚠️</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Activation Failed</h2>
          <p className="text-gray-600">
            There was an issue activating your AI receptionist. Please contact support.
          </p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-700 mb-4">
            Don't worry - your payment was successful and your account is created. 
            Our team will resolve this issue within 24 hours.
          </p>
          <div className="space-y-2 text-sm text-red-600">
            <p>Support Email: support@tero.com</p>
            <p>Customer ID: {initialData.customerId}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-2">🎉 You're Live!</h2>
        <p className="text-xl text-gray-600">
          Your AI receptionist is now active and ready to handle calls
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Quick Actions */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <a
              href={portalUrl}
              className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="flex items-center">
                <Settings className="w-5 h-5 text-blue-600 mr-3" />
                <span className="font-medium text-blue-900">Access Customer Portal</span>
              </div>
              <ExternalLink className="w-4 h-4 text-blue-600" />
            </a>

            <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <Phone className="w-5 h-5 text-green-600 mr-3" />
                <span className="font-medium text-green-900">Test Your Number</span>
              </div>
              <span className="text-sm text-green-700">{testPhoneNumber}</span>
            </div>

            <a
              href={`${portalUrl}/analytics`}
              className="flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <div className="flex items-center">
                <BarChart3 className="w-5 h-5 text-purple-600 mr-3" />
                <span className="font-medium text-purple-900">View Analytics</span>
              </div>
              <ExternalLink className="w-4 h-4 text-purple-600" />
            </a>
          </div>
        </div>

        {/* What's Next */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What's Next?</h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-bold text-blue-600">1</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Test Your AI</h4>
                <p className="text-sm text-gray-600">Call your business number to test the AI receptionist</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-bold text-blue-600">2</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Check Your Email</h4>
                <p className="text-sm text-gray-600">We've sent portal access details and quick start guide</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-bold text-blue-600">3</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Monitor Performance</h4>
                <p className="text-sm text-gray-600">Use the analytics dashboard to track calls and bookings</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Important Information */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-yellow-800 mb-3">Important Information</h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-yellow-700">
          <div>
            <h4 className="font-medium mb-1">Your AI Phone Number:</h4>
            <p>{testPhoneNumber}</p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Customer Portal:</h4>
            <p className="break-all">{window.location.origin}{portalUrl}</p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Support Email:</h4>
            <p>support@tero.com</p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Customer ID:</h4>
            <p className="font-mono text-xs">{initialData.customerId}</p>
          </div>
        </div>
      </div>

      {/* Success Message */}
      <div className="text-center">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <Mail className="w-8 h-8 text-green-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-green-800 mb-2">Welcome Email Sent!</h3>
          <p className="text-green-700">
            Check your inbox for detailed setup instructions and portal access information.
            If you don't see it, check your spam folder.
          </p>
        </div>
      </div>
    </div>
  );
};

export default OnboardingStep7;