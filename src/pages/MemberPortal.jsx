import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Settings,
  Phone,
  Mic,
  BarChart3,
  HelpCircle,
  Book,
  CheckCircle,
  AlertCircle,
  Play,
  ExternalLink,
  ChevronRight,
  Search
} from 'lucide-react';

/**
 * Member Portal Component
 * 
 * Complete customer dashboard with setup guides, FAQ, and account management
 * Accessible after PayPal subscription signup
 */

const MemberPortal = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Mock user data (replace with real API calls)
  const userData = {
    name: 'Dr. Sarah Chen',
    email: 'sarah@dentalcare.com',
    plan: 'Professional',
    status: 'Active',
    setupProgress: 75,
    callsThisMonth: 247,
    appointmentsBooked: 43,
    revenue: 18400
  };

  // Setup steps with progress tracking
  const setupSteps = [
    {
      id: 'account',
      title: 'Account Setup',
      description: 'Basic account information and preferences',
      completed: true,
      icon: User,
      estimatedTime: '2 minutes'
    },
    {
      id: 'voice',
      title: 'Voice Cloning',
      description: 'Record your voice sample for AI training',
      completed: true,
      icon: Mic,
      estimatedTime: '5 minutes'
    },
    {
      id: 'phone',
      title: 'Phone Integration',
      description: 'Connect your business phone number',
      completed: false,
      icon: Phone,
      estimatedTime: '10 minutes'
    },
    {
      id: 'prompts',
      title: 'Customize Prompts',
      description: 'Tailor AI responses for your business',
      completed: false,
      icon: Settings,
      estimatedTime: '15 minutes'
    }
  ];

  // FAQ categories and questions
  const faqCategories = [
    { id: 'all', label: 'All Topics', count: 24 },
    { id: 'setup', label: 'Setup & Installation', count: 8 },
    { id: 'voice', label: 'Voice Cloning', count: 6 },
    { id: 'phone', label: 'Phone Integration', count: 5 },
    { id: 'billing', label: 'Billing & Plans', count: 3 },
    { id: 'troubleshooting', label: 'Troubleshooting', count: 2 }
  ];

  const faqItems = [
    {
      category: 'setup',
      question: 'How long does it take to set up my AI receptionist?',
      answer: 'Complete setup typically takes 15-30 minutes. Voice cloning requires 24-48 hours for processing, but you can start taking calls immediately with our default voice.',
      popular: true
    },
    {
      category: 'voice',
      question: 'How do I record my voice sample for cloning?',
      answer: 'Use our built-in voice recorder to read the provided script (about 2-3 minutes of speech). Ensure you\'re in a quiet environment with good audio quality. Our AI will process your voice within 24-48 hours.',
      popular: true
    },
    {
      category: 'phone',
      question: 'Can I use my existing business phone number?',
      answer: 'Yes! We support number porting and call forwarding. You can keep your existing number and route calls through our AI system. Setup takes 5-10 minutes.',
      popular: true
    },
    {
      category: 'setup',
      question: 'What information does the AI need about my business?',
      answer: 'The AI needs your business hours, services offered, pricing (optional), booking calendar integration, and any specific scripts or responses you want it to use.',
      popular: false
    },
    {
      category: 'voice',
      question: 'How accurate is the voice cloning?',
      answer: 'Our voice cloning achieves 95%+ accuracy. Most customers report that callers cannot tell the difference between the AI and the real person.',
      popular: false
    },
    {
      category: 'phone',
      question: 'Do I need special phone equipment?',
      answer: 'No special equipment needed! Our system works with your existing phone setup through cloud-based call routing.',
      popular: false
    },
    {
      category: 'billing',
      question: 'Can I change my plan anytime?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and billing is prorated.',
      popular: false
    },
    {
      category: 'troubleshooting',
      question: 'What if the AI doesn\'t understand a caller?',
      answer: 'The AI will politely ask for clarification or transfer the call to you. You can also train it on specific scenarios through our prompt customization.',
      popular: false
    }
  ];

  // Filter FAQ items based on search and category
  const filteredFAQ = faqItems.filter(item => {
    const matchesSearch = item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Tab navigation
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'setup', label: 'Setup Guide', icon: Settings },
    { id: 'faq', label: 'FAQ & Help', icon: HelpCircle },
    { id: 'documentation', label: 'Documentation', icon: Book }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Receptionist Portal</h1>
                <p className="text-sm text-gray-500">Welcome back, {userData.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">{userData.plan} Plan</div>
                <div className="text-xs text-green-600">{userData.status}</div>
              </div>
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex space-x-8">
          {/* Sidebar Navigation */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <AnimatePresence mode="wait">
              {activeTab === 'dashboard' && (
                <motion.div
                  key="dashboard"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
                  
                  {/* Setup Progress */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Setup Progress</h3>
                      <span className="text-sm text-gray-500">{userData.setupProgress}% Complete</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${userData.setupProgress}%` }}
                      ></div>
                    </div>
                    <button 
                      onClick={() => setActiveTab('setup')}
                      className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
                    >
                      <span>Continue Setup</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-500">Calls This Month</p>
                          <p className="text-2xl font-bold text-gray-900">{userData.callsThisMonth}</p>
                        </div>
                        <Phone className="w-8 h-8 text-blue-600" />
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-500">Appointments Booked</p>
                          <p className="text-2xl font-bold text-gray-900">{userData.appointmentsBooked}</p>
                        </div>
                        <CheckCircle className="w-8 h-8 text-green-600" />
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-500">Revenue Generated</p>
                          <p className="text-2xl font-bold text-gray-900">${userData.revenue.toLocaleString()}</p>
                        </div>
                        <BarChart3 className="w-8 h-8 text-purple-600" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 'setup' && (
                <motion.div
                  key="setup"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  <h2 className="text-2xl font-bold text-gray-900">Setup Guide</h2>
                  
                  <div className="space-y-4">
                    {setupSteps.map((step, index) => (
                      <div key={step.id} className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-start space-x-4">
                          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                            step.completed ? 'bg-green-100' : 'bg-gray-100'
                          }`}>
                            {step.completed ? (
                              <CheckCircle className="w-6 h-6 text-green-600" />
                            ) : (
                              <step.icon className="w-6 h-6 text-gray-400" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
                              <span className="text-sm text-gray-500">{step.estimatedTime}</span>
                            </div>
                            <p className="text-gray-600 mt-1">{step.description}</p>
                            {!step.completed && (
                              <button className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                                Start Setup
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {activeTab === 'faq' && (
                <motion.div
                  key="faq"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  <h2 className="text-2xl font-bold text-gray-900">FAQ & Help</h2>
                  
                  {/* Search and Filter */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                      <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          placeholder="Search FAQ..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        {faqCategories.map((category) => (
                          <option key={category.id} value={category.id}>
                            {category.label} ({category.count})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* FAQ Items */}
                  <div className="space-y-4">
                    {filteredFAQ.map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-white rounded-lg shadow"
                      >
                        <details className="group">
                          <summary className="flex items-center justify-between p-6 cursor-pointer">
                            <div className="flex items-start space-x-3">
                              {item.popular && (
                                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                                  Popular
                                </span>
                              )}
                              <h3 className="font-semibold text-gray-900">{item.question}</h3>
                            </div>
                            <ChevronRight className="w-5 h-5 text-gray-400 group-open:rotate-90 transition-transform" />
                          </summary>
                          <div className="px-6 pb-6">
                            <p className="text-gray-600 leading-relaxed">{item.answer}</p>
                          </div>
                        </details>
                      </motion.div>
                    ))}
                  </div>

                  {filteredFAQ.length === 0 && (
                    <div className="text-center py-12">
                      <HelpCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                      <p className="text-gray-500">Try adjusting your search or category filter.</p>
                    </div>
                  )}
                </motion.div>
              )}

              {activeTab === 'documentation' && (
                <motion.div
                  key="documentation"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  <h2 className="text-2xl font-bold text-gray-900">Documentation</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      {
                        title: 'Quick Start Guide',
                        description: 'Get your AI receptionist up and running in 15 minutes',
                        icon: Play,
                        link: '#'
                      },
                      {
                        title: 'Voice Cloning Best Practices',
                        description: 'Tips for recording the perfect voice sample',
                        icon: Mic,
                        link: '#'
                      },
                      {
                        title: 'Phone Integration Manual',
                        description: 'Complete guide to connecting your phone system',
                        icon: Phone,
                        link: '#'
                      },
                      {
                        title: 'API Documentation',
                        description: 'Technical documentation for developers',
                        icon: Book,
                        link: '#'
                      },
                      {
                        title: 'Troubleshooting Guide',
                        description: 'Solutions to common issues and problems',
                        icon: AlertCircle,
                        link: '#'
                      },
                      {
                        title: 'Video Tutorials',
                        description: 'Step-by-step video walkthroughs',
                        icon: Play,
                        link: '#'
                      }
                    ].map((doc, index) => (
                      <div key={index} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <doc.icon className="w-6 h-6 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 mb-2">{doc.title}</h3>
                            <p className="text-gray-600 text-sm mb-4">{doc.description}</p>
                            <a
                              href={doc.link}
                              className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
                            >
                              <span>Read More</span>
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemberPortal;