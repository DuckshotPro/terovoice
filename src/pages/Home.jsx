import React, { useState } from 'react';
import { Phone, Clock, DollarSign, CheckCircle, Star, BarChart3, Users, AlertCircle } from 'lucide-react';
import backgroundImage from '../assets/backgroundImage.jpg';

function Home() {
  const [billingCycle, setBillingCycle] = useState('monthly');

  const plans = [
    {
      name: 'Small Business',
      price: billingCycle === 'monthly' ? 49 : 490,
      description: 'Solo operators & small teams',
      features: [
        'Unlimited customer calls',
        'AI answers service questions',
        'Appointment scheduling info',
        'After-hours call handling',
        'Email alerts for urgent calls',
        'Call transcripts & summaries'
      ],
      cta: 'Start Free Trial',
      highlighted: false
    },
    {
      name: 'Growing Business',
      price: billingCycle === 'monthly' ? 129 : 1290,
      description: 'Multi-location services',
      features: [
        'Unlimited customer calls',
        'Custom business training',
        'Lead qualification',
        'Payment info collection',
        'Advanced analytics dashboard',
        'Priority phone support',
        'Up to 3 locations'
      ],
      cta: 'Start Free Trial',
      highlighted: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      description: 'Large service networks',
      features: [
        'Unlimited everything',
        'Fully custom AI training',
        '24/7 dedicated support',
        'Unlimited locations',
        'White-label option',
        'Advanced integrations',
        'SLA guarantees'
      ],
      cta: 'Contact Sales',
      highlighted: false
    }
  ];

  const testimonials = [
    {
      name: 'John Martinez',
      role: 'Plumbing Business Owner',
      image: '🔧',
      text: 'No more missed calls. My customers get instant answers about pricing and availability 24/7. Increased bookings by 35%!'
    },
    {
      name: 'Dr. Lisa Wong',
      role: 'Dental Practice Owner',
      image: '🦷',
      text: 'The AI handles appointment questions perfectly. My staff can focus on patients instead of phones. Best investment ever.'
    },
    {
      name: 'Tom Anderson',
      role: 'Carpentry & Renovation',
      image: '🪛',
      text: 'Customers get callbacks instead of voicemail. The AI quals leads before I even call back. Saves me hours every week.'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section with Background Image */}
      <div className="relative h-screen flex items-center overflow-hidden">
        <img
          src={backgroundImage}
          alt="Background"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="relative z-10 container mx-auto px-4 text-center text-white">
          <h1 className="text-6xl font-bold mb-6">
            Never Miss a Customer Call Again
          </h1>
          <p className="text-2xl mb-8 opacity-95 max-w-3xl mx-auto">
            Your AI receptionist answers calls 24/7, schedules appointments, answers questions, and qualifies leads—while you focus on the work.
          </p>
          <p className="text-xl mb-12 opacity-90 max-w-2xl mx-auto">
            Perfect for plumbers, dentists, carpenters, electricians, contractors, and any service business that gets too many calls.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-bold transition">
              Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-bold hover:bg-white hover:text-blue-600 transition">
              See It In Action
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="bg-blue-600 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold">5M+</div>
              <p className="opacity-90">Customer Calls Handled</p>
            </div>
            <div>
              <div className="text-4xl font-bold">35%</div>
              <p className="opacity-90">Avg Booking Increase</p>
            </div>
            <div>
              <div className="text-4xl font-bold">24/7</div>
              <p className="opacity-90">Never Miss a Call</p>
            </div>
            <div>
              <div className="text-4xl font-bold">2K+</div>
              <p className="opacity-90">Service Businesses Served</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pain Points & Solutions */}
      <div className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">The Problem With Too Many Calls</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-md border-l-4 border-red-500">
              <AlertCircle className="h-8 w-8 text-red-500 mb-4" />
              <h3 className="text-xl font-bold mb-3">You're Losing Customers Right Now</h3>
              <p className="text-gray-700">For every missed call, customers call your competitors. Studies show 70% of callers who get voicemail will call someone else.</p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-md border-l-4 border-blue-500">
              <Phone className="h-8 w-8 text-blue-500 mb-4" />
              <h3 className="text-xl font-bold mb-3">Our Solution: AI That Actually Works</h3>
              <p className="text-gray-700">Your customers get instant answers. Appointments get booked. Leads get qualified. All while you focus on the actual work.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">What Your AI Receptionist Does</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <Phone className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Answers Every Call</h3>
              <p className="text-gray-600">Never let a call go to voicemail again. Your customers get a real conversation instantly, 24/7.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <Clock className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Books Appointments</h3>
              <p className="text-gray-600">Customers can schedule appointments with their availability. No back-and-forth. No double booking.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <DollarSign className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Qualifies Leads</h3>
              <p className="text-gray-600">Get info before you call back. Location, job scope, timeline, budget. You know what to expect.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <Users className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Sounds Like You</h3>
              <p className="text-gray-600">Customizable AI personality. Talks your way. Your customers don't know they're not talking to a human.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <BarChart3 className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Call Analytics</h3>
              <p className="text-gray-600">See every call, transcripts, and summaries. Know what customers are asking. Make data-driven decisions.</p>
            </div>
            <div className="p-8 border border-gray-200 rounded-lg hover:shadow-lg transition">
              <CheckCircle className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-bold mb-3">Easy Setup</h3>
              <p className="text-gray-600">Connect your phone number in minutes. No complex integrations. AI starts working immediately.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-4">Simple Pricing for Service Businesses</h2>
          <p className="text-center text-gray-600 mb-8">No hidden fees. No contracts. Cancel anytime.</p>

          {/* Billing Toggle */}
          <div className="flex justify-center mb-12">
            <div className="bg-white rounded-lg p-2 shadow-md">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-md font-bold transition ${
                  billingCycle === 'monthly'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-6 py-2 rounded-md font-bold transition ${
                  billingCycle === 'annual'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Annual (Save 17%)
              </button>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, idx) => (
              <div
                key={idx}
                className={`rounded-lg overflow-hidden transition transform hover:scale-105 ${
                  plan.highlighted
                    ? 'bg-blue-600 text-white shadow-2xl'
                    : 'bg-white border border-gray-200 shadow-md'
                }`}
              >
                {plan.highlighted && (
                  <div className="bg-yellow-400 text-blue-600 text-center py-2 font-bold">
                    Most Popular
                  </div>
                )}
                <div className="p-8">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <p className={`mb-4 ${plan.highlighted ? 'opacity-90' : 'text-gray-600'}`}>
                    {plan.description}
                  </p>
                  <div className="mb-6">
                    <span className="text-4xl font-bold">${plan.price}</span>
                    {typeof plan.price === 'number' && (
                      <span className={plan.highlighted ? 'opacity-75' : 'text-gray-600'}>
                        {billingCycle === 'monthly' ? '/month' : '/year'}
                      </span>
                    )}
                  </div>
                  <button
                    className={`w-full py-3 rounded-lg font-bold mb-8 transition ${
                      plan.highlighted
                        ? 'bg-white text-blue-600 hover:bg-gray-100'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {plan.cta}
                  </button>
                  <ul className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-12">Trusted by Industry Leaders</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <div key={idx} className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">"{testimonial.text}"</p>
                <div className="flex items-center gap-4">
                  <div className="text-4xl">{testimonial.image}</div>
                  <div>
                    <p className="font-bold">{testimonial.name}</p>
                    <p className="text-gray-600 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Stop Losing Customers to Voicemail</h2>
          <p className="text-xl mb-8 opacity-90">Try it free for 30 days. No credit card required.</p>
          <button className="bg-white text-blue-600 px-10 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition">
            Start Your Free Trial Now
          </button>
          <p className="text-sm opacity-75 mt-4">Plumbers, dentists, carpenters, electricians, contractors—get instant customer answers 24/7</p>
        </div>
      </div>
    </div>
  );
}

export default Home;
