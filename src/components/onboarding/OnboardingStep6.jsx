import React, { useState } from 'react';
import { CheckCircle, Settings, Phone, Calendar, MessageSquare, FileText } from 'lucide-react';

const OnboardingStep6 = ({ onNext, onBack, initialData = {} }) => {
  const [loading, setLoading] = useState(false);
  const [reviewData, setReviewData] = useState(initialData);

  const sections = [
    {
      icon: <FileText className="w-5 h-5" />,
      title: 'Business Information',
      items: [
        { label: 'Business Name', value: reviewData.businessName },
        { label: 'Industry', value: reviewData.industry },
        { label: 'Phone Number', value: reviewData.businessPhone },
        { label: 'Service Description', value: reviewData.serviceDescription },
        { label: 'Documents Uploaded', value: `${(reviewData.businessDocuments || []).length} files` }
      ]
    },
    {
      icon: <Phone className="w-5 h-5" />,
      title: 'Phone Configuration',
      items: [
        { label: 'Forwarding Number', value: reviewData.forwardingNumber },
        { label: 'SMS Notifications', value: reviewData.smsEnabled ? 'Enabled' : 'Disabled' },
        { label: 'SMS Phone Number', value: reviewData.smsPhoneNumber || 'Not set' }
      ]
    },
    {
      icon: <MessageSquare className="w-5 h-5" />,
      title: 'Caller Responses',
      items: [
        { label: 'Appointment Requests', value: reviewData.callerResponses?.appointment_request ? 'Configured' : 'Default' },
        { label: 'Pricing Inquiries', value: reviewData.callerResponses?.pricing_inquiry ? 'Configured' : 'Default' },
        { label: 'Emergency Calls', value: reviewData.callerResponses?.emergency ? 'Configured' : 'Default' },
        { label: 'General Inquiries', value: reviewData.callerResponses?.other ? 'Configured' : 'Default' }
      ]
    },
    {
      icon: <Calendar className="w-5 h-5" />,
      title: 'Calendar Integration',
      items: [
        { label: 'Provider', value: reviewData.calendarProvider || 'Not configured' },
        { label: 'Connection Status', value: reviewData.calendarConnected ? 'Connected' : 'Not connected' }
      ]
    },
    {
      icon: <Settings className="w-5 h-5" />,
      title: 'Demo Results',
      items: [
        { label: 'Demo Completed', value: reviewData.demoCompleted ? 'Yes' : 'No' },
        { label: 'Conversation Exchanges', value: `${(reviewData.demoTranscripts || []).length} messages` }
      ]
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/onboarding/${initialData.customerId}/step-6`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reviewCompleted: true,
          reviewedAt: new Date().toISOString()
        }),
      });

      if (response.ok) {
        const result = await response.json();
        onNext(result);
      } else {
        throw new Error('Failed to complete review step');
      }
    } catch (error) {
      console.error('Error completing review step:', error);
      alert('Failed to complete review step. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Review Your Setup</h2>
        <p className="text-gray-600">
          Please review your configuration before we activate your AI receptionist
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Configuration Review */}
        <div className="grid gap-6">
          {sections.map((section, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <div className="text-blue-600 mr-3">{section.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {section.items.map((item, itemIndex) => (
                  <div key={itemIndex} className="flex justify-between items-start">
                    <span className="text-sm font-medium text-gray-700">{item.label}:</span>
                    <span className="text-sm text-gray-900 text-right max-w-xs truncate" title={item.value}>
                      {item.value || 'Not set'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Important Notes */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">Before We Go Live</h3>
          <div className="space-y-2 text-sm text-blue-700">
            <p>• Your AI receptionist will be activated immediately after this step</p>
            <p>• You can modify these settings anytime in your customer portal</p>
            <p>• Test calls are recommended before directing real customers</p>
            <p>• You'll receive an email with your portal login details</p>
          </div>
        </div>

        {/* Confirmation Checkbox */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-start">
            <input
              type="checkbox"
              id="confirmReview"
              required
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
            />
            <label htmlFor="confirmReview" className="ml-3 text-sm text-gray-700">
              I have reviewed my configuration and understand that my AI receptionist will be activated.
              I can make changes later through my customer portal.
            </label>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Back to Demo
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Activating...' : 'Activate My AI Receptionist'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OnboardingStep6;