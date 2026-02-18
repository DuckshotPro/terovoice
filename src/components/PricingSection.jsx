import React, { useState } from 'react';
import { Check, Star, Zap, Crown } from 'lucide-react';

const PricingSection = () => {
  const [loading, setLoading] = useState({});

  const plans = [
    {
      id: 'monthly_299',
      name: 'Solo Pro',
      price: 299,
      description: 'Perfect for individual professionals',
      icon: <Star className="w-6 h-6" />,
      features: [
        '1 AI Receptionist',
        '1,000 minutes/month',
        'Voice cloning included',
        'Basic analytics',
        'Email support',
        'Calendar integration',
        'SMS notifications'
      ],
      popular: false,
      color: 'blue'
    },
    {
      id: 'monthly_499',
      name: 'Pro',
      price: 499,
      description: 'Most popular for growing businesses',
      icon: <Zap className="w-6 h-6" />,
      features: [
        '3 AI Receptionists',
        '2,500 minutes/month',
        'Voice cloning included',
        'Advanced analytics',
        'Priority support',
        'Calendar integration',
        'SMS notifications',
        'Custom responses',
        'Call recordings'
      ],
      popular: true,
      color: 'green'
    },
    {
      id: 'monthly_799',
      name: 'White-Label',
      price: 799,
      description: 'For agencies and multi-location businesses',
      icon: <Crown className="w-6 h-6" />,
      features: [
        '10 AI Receptionists',
        '5,000 minutes/month',
        'Voice cloning included',
        'White-label dashboard',
        'Dedicated support',
        'API access',
        'Custom integrations',
        'Multi-location support',
        'Advanced reporting',
        'Priority phone support'
      ],
      popular: false,
      color: 'purple'
    }
  ];

  const handlePayPalPayment = async (planId) => {
    setLoading(prev => ({ ...prev, [planId]: true }));

    try {
      // Create PayPal order
      const response = await fetch('/api/paypal/create-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planId,
          returnUrl: `${window.location.origin}/onboarding`,
          cancelUrl: `${window.location.origin}/#pricing`
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to PayPal for payment
        window.location.href = data.approvalUrl;
      } else {
        throw new Error('Failed to create PayPal order');
      }
    } catch (error) {
      console.error('PayPal payment error:', error);
      alert('Payment failed. Please try again.');
    } finally {
      setLoading(prev => ({ ...prev, [planId]: false }));
    }
  };

  const getColorClasses = (color, popular = false) => {
    const colors = {
      blue: {
        border: popular ? 'border-blue-500' : 'border-gray-200',
        button: 'bg-blue-600 hover:bg-blue-700',
        icon: 'text-blue-600',
        badge: 'bg-blue-100 text-blue-800'
      },
      green: {
        border: popular ? 'border-green-500' : 'border-gray-200',
        button: 'bg-green-600 hover:bg-green-700',
        icon: 'text-green-600',
        badge: 'bg-green-100 text-green-800'
      },
      purple: {
        border: popular ? 'border-purple-500' : 'border-gray-200',
        button: 'bg-purple-600 hover:bg-purple-700',
        icon: 'text-purple-600',
        badge: 'bg-purple-100 text-purple-800'
      }
    };
    return colors[color];
  };

  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Choose the perfect plan for your business. All plans include voice cloning,
            24/7 AI receptionist, and comprehensive analytics.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => {
            const colorClasses = getColorClasses(plan.color, plan.popular);

            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-2xl shadow-lg border-2 ${colorClasses.border} ${
                  plan.popular ? 'scale-105 shadow-2xl' : ''
                }`}
              >
                {plan.popular && (
                  <div className={`absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 ${colorClasses.badge} rounded-full text-sm font-semibold`}>
                    Most Popular
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Header */}
                  <div className="text-center mb-8">
                    <div className={`inline-flex items-center justify-center w-12 h-12 ${colorClasses.icon} bg-gray-50 rounded-lg mb-4`}>
                      {plan.icon}
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <p className="text-gray-600 mb-4">{plan.description}</p>
                    <div className="flex items-baseline justify-center">
                      <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                      <span className="text-xl text-gray-500 ml-2">/month</span>
                    </div>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center">
                        <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* PayPal Button */}
                  <button
                    onClick={() => handlePayPalPayment(plan.id)}
                    disabled={loading[plan.id]}
                    className={`w-full py-4 px-6 rounded-lg text-white font-semibold transition-colors ${colorClasses.button} disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {loading[plan.id] ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Processing...
                      </div>
                    ) : (
                      `Get Started - $${plan.price}/mo`
                    )}
                  </button>

                  <p className="text-center text-sm text-gray-500 mt-4">
                    Secure payment via PayPal • Cancel anytime
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Additional Info */}
        <div className="text-center mt-16">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              What's Included in Every Plan
            </h3>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">🎯 AI Technology</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Voice cloning (sounds like you)</li>
                  <li>• Natural conversation AI</li>
                  <li>• Multi-language support</li>
                  <li>• Continuous learning</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">📞 Phone Features</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• 24/7 call answering</li>
                  <li>• Appointment scheduling</li>
                  <li>• Call forwarding</li>
                  <li>• SMS notifications</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">📊 Business Tools</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Real-time analytics</li>
                  <li>• Call transcripts</li>
                  <li>• Customer portal</li>
                  <li>• Integration support</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Money Back Guarantee */}
        <div className="text-center mt-12">
          <div className="inline-flex items-center bg-green-50 border border-green-200 rounded-lg px-6 py-3">
            <Check className="w-5 h-5 text-green-600 mr-2" />
            <span className="text-green-800 font-medium">
              30-day money-back guarantee • No setup fees • Cancel anytime
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PricingSection;