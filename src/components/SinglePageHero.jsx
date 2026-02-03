import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import {
  Phone,
  Clock,
  DollarSign,
  CheckCircle,
  Star,
  BarChart3,
  Users,
  AlertCircle,
  Calendar,
  Menu,
  X,
} from 'lucide-react';

// Import components
import AnimatedBackground from './AnimatedBackground';
import PayPalButton from './PayPalButton';
import backgroundImage from '../assets/backgroundImage.jpg';

// Import animation utilities
import {
  scrollAnimations,
  buttonAnimations,
  performanceUtils
} from '../utils/animationUtils';

/**
 * SinglePageHero Component
 * 
 * Animated single-page landing experience for AI Receptionist SaaS
 * Features smooth scroll animations, dynamic content, and conversion optimization
 */

const SinglePageHero = () => {
  const navigate = useNavigate();
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [selectedProfession, setSelectedProfession] = useState('dentist');
  const [missedCalls, setMissedCalls] = useState(10);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');

  // Performance optimization
  const optimizedConfig = performanceUtils.getOptimizedConfig();
  const isMobile = window.innerWidth < 768;

  // Mobile-optimized animation config
  const mobileConfig = {
    ...optimizedConfig,
    enableComplexAnimations: optimizedConfig.enableComplexAnimations && !isMobile,
    duration: isMobile ? optimizedConfig.duration * 0.7 : optimizedConfig.duration,
    staggerDelay: isMobile ? optimizedConfig.staggerDelay * 0.5 : optimizedConfig.staggerDelay,
  };

  // Intersection observers for sections
  const [heroRef, heroInView] = useInView({ threshold: 0.5 });
  const [metricsRef, metricsInView] = useInView({ threshold: 0.3 });
  const [calculatorRef, calculatorInView] = useInView({ threshold: 0.3 });
  const [professionsRef, professionsInView] = useInView({ threshold: 0.3 });
  const [featuresRef, featuresInView] = useInView({ threshold: 0.3 });
  const [pricingRef, pricingInView] = useInView({ threshold: 0.3 });
  const [testimonialsRef, testimonialsInView] = useInView({ threshold: 0.3 });
  const [ctaRef, ctaInView] = useInView({ threshold: 0.3 });

  // Update active section based on scroll
  useEffect(() => {
    if (ctaInView) setActiveSection('cta');
    else if (testimonialsInView) setActiveSection('testimonials');
    else if (pricingInView) setActiveSection('pricing');
    else if (featuresInView) setActiveSection('features');
    else if (professionsInView) setActiveSection('professions');
    else if (calculatorInView) setActiveSection('calculator');
    else if (metricsInView) setActiveSection('metrics');
    else if (heroInView) setActiveSection('hero');
  }, [heroInView, metricsInView, calculatorInView, professionsInView, featuresInView, pricingInView, testimonialsInView, ctaInView]);

  // Handle URL hash changes
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && navigationSections.find(section => section.id === hash)) {
        scrollToSection(hash);
      }
    };

    window.addEventListener('hashchange', handleHashChange);

    // Check initial hash
    if (window.location.hash) {
      handleHashChange();
    }

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) return; // Don't interfere with browser shortcuts

      const currentIndex = navigationSections.findIndex(section => section.id === activeSection);

      switch (e.key) {
        case 'ArrowUp':
        case 'ArrowLeft':
          e.preventDefault();
          if (currentIndex > 0) {
            scrollToSection(navigationSections[currentIndex - 1].id);
          }
          break;
        case 'ArrowDown':
        case 'ArrowRight':
          e.preventDefault();
          if (currentIndex < navigationSections.length - 1) {
            scrollToSection(navigationSections[currentIndex + 1].id);
          }
          break;
        case 'Home':
          e.preventDefault();
          scrollToSection('hero');
          break;
        case 'End':
          e.preventDefault();
          scrollToSection('cta');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeSection]);

  // ROI Calculator data by profession
  const professionData = {
    dentist: { avgJobValue: 800, yearlyLTV: 15000, missedCallCost: 50000 },
    plumber: { avgJobValue: 500, yearlyLTV: 8000, missedCallCost: 40000 },
    mechanic: { avgJobValue: 400, yearlyLTV: 6000, missedCallCost: 35000 },
    locksmith: { avgJobValue: 200, yearlyLTV: 3000, missedCallCost: 80000 },
    contractor: { avgJobValue: 2000, yearlyLTV: 25000, missedCallCost: 100000 },
    photographer: { avgJobValue: 3000, yearlyLTV: 15000, missedCallCost: 60000 },
    realtor: { avgJobValue: 12000, yearlyLTV: 50000, missedCallCost: 150000 },
    tattoo: { avgJobValue: 300, yearlyLTV: 4000, missedCallCost: 30000 },
    inspector: { avgJobValue: 500, yearlyLTV: 6000, missedCallCost: 40000 },
  };

  const calculateROI = () => {
    const data = professionData[selectedProfession];
    const weeklyMissedCalls = missedCalls;
    const yearlyMissedCalls = weeklyMissedCalls * 52;
    const potentialRevenue = yearlyMissedCalls * data.avgJobValue * 0.3; // 30% conversion
    const serviceCost = 499 * 12; // Professional plan yearly
    const roi = ((potentialRevenue - serviceCost) / serviceCost) * 100;

    return {
      potentialRevenue: Math.round(potentialRevenue),
      serviceCost,
      roi: Math.round(roi),
      paybackDays: Math.round((serviceCost / (potentialRevenue / 365)) || 0),
    };
  };

  const roiData = calculateROI();

  // Pricing plans
  const plans = [
    {
      name: 'Solo Pro',
      price: billingCycle === 'monthly' ? 299 : 2990,
      description: 'Perfect for solo practitioners',
      features: [
        'Unlimited customer calls',
        'Your voice cloned perfectly',
        'Custom profession prompts',
        'Appointment booking & scheduling',
        'Lead qualification & notes',
        'Real-time call analytics',
        'Email & SMS notifications',
        '24/7 uptime guarantee',
      ],
      cta: 'Start Free Trial',
      highlighted: false,
      roi: 'Avg ROI: 1,500%+',
      savings: 'Saves $5k-$15k/month in missed calls',
    },
    {
      name: 'Professional',
      price: billingCycle === 'monthly' ? 499 : 4990,
      description: 'Most popular for growing businesses',
      features: [
        'Everything in Solo Pro',
        'Multi-location support',
        'Advanced call routing',
        'Custom integrations (CRM, calendar)',
        'Priority voice cloning',
        'Dedicated account manager',
        'Advanced analytics dashboard',
        'White-label option available',
      ],
      cta: 'Start Free Trial',
      highlighted: true,
      roi: 'Avg ROI: 3,000%+',
      savings: 'Saves $10k-$30k/month in missed calls',
    },
    {
      name: 'Enterprise',
      price: billingCycle === 'monthly' ? 799 : 7990,
      description: 'For large service networks',
      features: [
        'Everything in Professional',
        'Unlimited locations & numbers',
        'Custom AI model training',
        'API access & webhooks',
        'SLA guarantees (99.9% uptime)',
        '24/7 dedicated support',
        'Custom reporting & exports',
        'Full white-label solution',
      ],
      cta: 'Contact Sales',
      highlighted: false,
      roi: 'Avg ROI: 5,000%+',
      savings: 'Saves $25k-$100k/month in missed calls',
    },
  ];

  // Testimonials
  const testimonials = [
    {
      name: 'Dr. Sarah Chen',
      role: 'Dental Practice Owner',
      image: '🦷',
      text: 'Booked 47 new patients in the first month. The AI handles insurance questions perfectly. ROI was 2,800% in 90 days.',
      revenue: '+$18,400/month',
    },
    {
      name: 'Mike Rodriguez',
      role: 'Emergency Plumber',
      image: '🔧',
      text: 'No more 2 AM voicemails. AI books emergency calls instantly and collects payment info. Doubled my after-hours revenue.',
      revenue: '+$12,600/month',
    },
    {
      name: 'Jennifer Walsh',
      role: 'Wedding Photographer',
      image: '📸',
      text: 'Booked 8 weddings during golden hour shoots. AI asks all the right questions and sends my pricing automatically.',
      revenue: '+$24,000/month',
    },
  ];

  // Navigation sections
  const navigationSections = [
    { id: 'hero', label: 'Home' },
    { id: 'metrics', label: 'Metrics' },
    { id: 'calculator', label: 'ROI Calculator' },
    { id: 'professions', label: 'Professions' },
    { id: 'features', label: 'Features' },
    { id: 'pricing', label: 'Pricing' },
    { id: 'testimonials', label: 'Testimonials' },
  ];

  // Smooth scroll to section
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });

      // Update URL hash without triggering hashchange event
      if (window.location.hash !== `#${sectionId}`) {
        window.history.pushState(null, null, `#${sectionId}`);
      }
    }
    setIsMenuOpen(false);
  };

  return (
    <div
      className="min-h-screen bg-transparent text-white overflow-x-hidden"
      role="main"
      aria-label="AI Receptionist Service Landing Page"
    >
      {/* Skip to content link for screen readers */}
      <a
        href="#hero"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50"
      >
        Skip to main content
      </a>
      {/* Animated Background - DISABLED to use Global Wave Background
      <AnimatedBackground
        variant="particles"
        intensity={mobileConfig.enableParticles ? "medium" : "subtle"}
        colorScheme="gradient"
        backgroundImage={backgroundImage}
      />
      */}

      {/* Floating Navigation */}
      <motion.nav
        className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1, duration: 0.6 }}
        role="navigation"
        aria-label="Page sections navigation"
      >
        <div className="bg-white/10 backdrop-blur-md rounded-full px-6 py-3 border border-white/20">
          <div className="hidden md:flex items-center space-x-6">
            {navigationSections.map((section) => (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`text-sm font-medium transition-colors duration-200 ${activeSection === section.id
                  ? 'text-blue-400'
                  : 'text-gray-300 hover:text-white'
                  }`}
                aria-current={activeSection === section.id ? 'page' : undefined}
                aria-label={`Navigate to ${section.label} section`}
              >
                {section.label}
              </button>
            ))}
            <button
              onClick={() => navigate('/auth/login')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200 ml-4"
            >
              Member Login
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white p-2"
              aria-expanded={isMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              className="absolute top-full left-0 right-0 mt-2 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-4 md:hidden"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              role="menu"
            >
              {navigationSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className={`block w-full text-left py-2 text-sm font-medium transition-colors duration-200 ${activeSection === section.id
                    ? 'text-blue-400'
                    : 'text-gray-300 hover:text-white'
                    }`}
                  role="menuitem"
                  aria-current={activeSection === section.id ? 'page' : undefined}
                >
                  {section.label}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* Hero Section */}
      <section
        id="hero"
        ref={heroRef}
        className="min-h-screen flex items-center justify-center relative"
        aria-labelledby="hero-heading"
      >
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial="hidden"
            animate={heroInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            {/* Animated Headline */}
            <motion.h1
              id="hero-heading"
              className="text-6xl md:text-8xl font-bold mb-6"
              variants={scrollAnimations.staggerChild}
            >
              Your AI Receptionist{' '}
              <motion.span
                className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400"
                animate={{
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "linear"
                }}
                style={{ backgroundSize: '200% 200%' }}
              >
                That Never Sleeps
              </motion.span>
            </motion.h1>

            <motion.p
              className="text-2xl mb-8 opacity-95 max-w-3xl mx-auto"
              variants={scrollAnimations.staggerChild}
            >
              Stop losing $10k-$50k/month to missed calls. Your AI answers instantly, books appointments,
              and qualifies leads while you work—24/7, sounds exactly like you.
            </motion.p>

            <motion.p
              className="text-xl mb-8 opacity-90 max-w-2xl mx-auto"
              variants={scrollAnimations.staggerChild}
            >
              Perfect for dentists, plumbers, mechanics, locksmiths, contractors, and any service
              business drowning in calls.
            </motion.p>

            {/* ROI Badge */}
            <motion.div
              className="bg-yellow-400 text-black px-6 py-3 rounded-lg font-bold text-lg mb-8 inline-block"
              variants={scrollAnimations.scaleIn}
              animate={{
                scale: [1, 1.05, 1],
                boxShadow: [
                  "0 0 0 0 rgba(250, 204, 21, 0.4)",
                  "0 0 0 10px rgba(250, 204, 21, 0)",
                  "0 0 0 0 rgba(250, 204, 21, 0)"
                ]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3
              }}
            >
              🚀 Average ROI: 1,500% - 8,000% in Year 1
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col md:flex-row gap-4 justify-center"
              variants={scrollAnimations.staggerChild}
            >
              <motion.div
                variants={buttonAnimations.primary}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
              >
                <PayPalButton
                  plan="Professional"
                  variant="primary"
                  className="w-full md:w-auto"
                >
                  Get Your AI Clone (Free Trial)
                </PayPalButton>
              </motion.div>

              <motion.button
                onClick={() => scrollToSection('calculator')}
                className="border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg transition-all duration-300"
                variants={buttonAnimations.secondary}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
              >
                Calculate Your ROI
              </motion.button>
            </motion.div>

            <motion.p
              className="text-sm opacity-75 mt-6"
              variants={scrollAnimations.staggerChild}
            >
              ✅ 30-day free trial • ✅ No setup fees • ✅ Cancel anytime
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Metrics Section */}
      <section id="metrics" ref={metricsRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={metricsInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center"
          >
            {[
              { number: '2,847', label: 'Service Businesses Served', icon: Users },
              { number: '$47M+', label: 'Revenue Generated for Clients', icon: DollarSign },
              { number: '99.7%', label: 'Uptime Guarantee', icon: CheckCircle },
              { number: '< 800ms', label: 'Average Response Time', icon: Clock },
            ].map((metric, index) => (
              <motion.div
                key={index}
                variants={scrollAnimations.staggerChild}
                className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10"
              >
                <metric.icon className="w-8 h-8 mx-auto mb-4 text-blue-400" />
                <motion.div
                  className="text-3xl font-bold mb-2"
                  initial={{ opacity: 0 }}
                  animate={metricsInView ? { opacity: 1 } : { opacity: 0 }}
                  transition={{ delay: index * 0.2 + 0.5, duration: 0.6 }}
                >
                  {metric.number}
                </motion.div>
                <div className="text-sm opacity-75">{metric.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section id="calculator" ref={calculatorRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={calculatorInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
            className="max-w-4xl mx-auto"
          >
            <motion.h2
              className="text-5xl font-bold text-center mb-4"
              variants={scrollAnimations.staggerChild}
            >
              Calculate Your ROI
            </motion.h2>
            <motion.p
              className="text-xl text-center mb-12 opacity-90"
              variants={scrollAnimations.staggerChild}
            >
              See exactly how much money you're losing to missed calls
            </motion.p>

            <motion.div
              className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20"
              variants={scrollAnimations.scaleIn}
            >
              <div className="grid md:grid-cols-2 gap-8">
                {/* Calculator Inputs */}
                <div>
                  <div className="mb-6">
                    <label className="block text-sm font-medium mb-2">Your Profession</label>
                    <select
                      value={selectedProfession}
                      onChange={(e) => setSelectedProfession(e.target.value)}
                      className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-blue-400 focus:outline-none"
                    >
                      <option value="dentist" className="bg-gray-800 text-white">Dentist</option>
                      <option value="plumber" className="bg-gray-800 text-white">Plumber</option>
                      <option value="mechanic" className="bg-gray-800 text-white">Mobile Mechanic</option>
                      <option value="locksmith" className="bg-gray-800 text-white">Locksmith</option>
                      <option value="contractor" className="bg-gray-800 text-white">Contractor</option>
                      <option value="photographer" className="bg-gray-800 text-white">Photographer</option>
                      <option value="realtor" className="bg-gray-800 text-white">Real Estate Agent</option>
                      <option value="tattoo" className="bg-gray-800 text-white">Tattoo Artist</option>
                      <option value="inspector" className="bg-gray-800 text-white">Home Inspector</option>
                    </select>
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium mb-2">
                      Missed Calls Per Week: {missedCalls}
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="50"
                      value={missedCalls}
                      onChange={(e) => setMissedCalls(parseInt(e.target.value))}
                      className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs opacity-75 mt-1">
                      <span>1</span>
                      <span>25</span>
                      <span>50+</span>
                    </div>
                  </div>
                </div>

                {/* Results */}
                <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-xl p-6">
                  <h3 className="text-xl font-bold mb-4 text-center">Your Potential ROI</h3>

                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span>Lost Revenue/Year:</span>
                      <motion.span
                        className="font-bold text-red-400"
                        key={roiData.potentialRevenue}
                        initial={{ scale: 1.2, color: '#ef4444' }}
                        animate={{ scale: 1, color: '#f87171' }}
                        transition={{ duration: 0.3 }}
                      >
                        ${roiData.potentialRevenue.toLocaleString()}
                      </motion.span>
                    </div>

                    <div className="flex justify-between">
                      <span>Service Cost/Year:</span>
                      <span className="font-bold">${roiData.serviceCost.toLocaleString()}</span>
                    </div>

                    <div className="border-t border-white/20 pt-4">
                      <div className="flex justify-between text-lg">
                        <span>Net Profit:</span>
                        <motion.span
                          className="font-bold text-green-400"
                          key={roiData.potentialRevenue - roiData.serviceCost}
                          initial={{ scale: 1.2 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.3 }}
                        >
                          ${(roiData.potentialRevenue - roiData.serviceCost).toLocaleString()}
                        </motion.span>
                      </div>

                      <div className="flex justify-between text-lg mt-2">
                        <span>ROI:</span>
                        <motion.span
                          className="font-bold text-yellow-400"
                          key={roiData.roi}
                          initial={{ scale: 1.2 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.3 }}
                        >
                          {roiData.roi}%
                        </motion.span>
                      </div>

                      <div className="text-center mt-4 p-3 bg-green-500/20 rounded-lg">
                        <div className="text-sm opacity-90">Payback Period</div>
                        <div className="text-2xl font-bold text-green-400">
                          {roiData.paybackDays} days
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <motion.div
                className="text-center mt-8"
                variants={scrollAnimations.staggerChild}
              >
                <PayPalButton
                  plan="Professional"
                  variant="success"
                  className="w-full"
                >
                  Start Capturing This Revenue Today
                </PayPalButton>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Professions Section */}
      <section id="professions" ref={professionsRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={professionsInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            <motion.h2
              className="text-5xl font-bold text-center mb-4"
              variants={scrollAnimations.staggerChild}
            >
              Built for Service Professionals
            </motion.h2>
            <motion.p
              className="text-xl text-center mb-12 opacity-90 max-w-3xl mx-auto"
              variants={scrollAnimations.staggerChild}
            >
              When your hands are busy, your phone shouldn't be silent.
              Perfect for any profession where you can't answer calls while working.
            </motion.p>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  icon: '🦷',
                  title: 'Dentists & Hygienists',
                  description: 'Books cleanings, consultations, and emergency appointments while you\'re drilling.',
                  painPoint: 'Gloves + suction = missed $1,200 patients',
                  result: '+8-15 new patients/month'
                },
                {
                  icon: '🔧',
                  title: 'Plumbers & Contractors',
                  description: 'Handles emergency calls, quotes repairs, and schedules jobs while you\'re under sinks.',
                  painPoint: 'Crawl spaces don\'t have cell service',
                  result: '+6-12 emergency jobs/month'
                },
                {
                  icon: '🚗',
                  title: 'Mobile Mechanics',
                  description: 'Books brake jobs and diagnostics while you\'re elbow-deep in engines.',
                  painPoint: 'Greasy hands + $400 brake jobs don\'t mix',
                  result: '+10-20 service calls/month'
                },
                {
                  icon: '🔒',
                  title: 'Locksmiths',
                  description: 'Takes emergency lockout calls 24/7 while you\'re picking locks.',
                  painPoint: 'Ladders + lock picks = dropped calls',
                  result: '+15-30 emergency calls/month'
                },
                {
                  icon: '💆',
                  title: 'Massage Therapists',
                  description: 'Books sessions and handles cancellations during your quiet treatment time.',
                  painPoint: 'Silent rooms can\'t have ringing phones',
                  result: '+20-40 sessions/month'
                },
                {
                  icon: '📸',
                  title: 'Wedding Photographers',
                  description: 'Books consultations during golden hour shoots and wedding ceremonies.',
                  painPoint: 'Can\'t interrupt the "I do" moment',
                  result: '+3-6 weddings/year'
                }
              ].map((profession, index) => (
                <motion.div
                  key={index}
                  variants={scrollAnimations.staggerChild}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300"
                  whileHover={{ scale: 1.02, y: -5 }}
                >
                  <div className="text-4xl mb-4 text-center">{profession.icon}</div>
                  <h3 className="text-xl font-bold mb-3 text-center">{profession.title}</h3>
                  <p className="text-sm opacity-90 mb-4">{profession.description}</p>

                  <div className="bg-red-500/20 rounded-lg p-3 mb-4">
                    <div className="text-xs font-medium text-red-300 mb-1">The Problem:</div>
                    <div className="text-sm">{profession.painPoint}</div>
                  </div>

                  <div className="bg-green-500/20 rounded-lg p-3">
                    <div className="text-xs font-medium text-green-300 mb-1">The Result:</div>
                    <div className="text-sm font-bold">{profession.result}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" ref={featuresRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={featuresInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            <motion.h2
              className="text-5xl font-bold text-center mb-4"
              variants={scrollAnimations.staggerChild}
            >
              Everything You Need to Never Miss a Call
            </motion.h2>
            <motion.p
              className="text-xl text-center mb-12 opacity-90"
              variants={scrollAnimations.staggerChild}
            >
              Your AI receptionist handles everything a human would—but better, faster, and 24/7
            </motion.p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: Phone,
                  title: 'Perfect Voice Cloning',
                  description: 'Sounds exactly like you. Customers can\'t tell the difference.',
                  highlight: 'Indistinguishable from human'
                },
                {
                  icon: Clock,
                  title: '24/7 Availability',
                  description: 'Never miss another call. Works nights, weekends, and holidays.',
                  highlight: '99.7% uptime guarantee'
                },
                {
                  icon: Calendar,
                  title: 'Smart Scheduling',
                  description: 'Books appointments directly into your calendar with all details.',
                  highlight: 'Integrates with Google, Outlook'
                },
                {
                  icon: DollarSign,
                  title: 'Lead Qualification',
                  description: 'Asks the right questions and prioritizes high-value prospects.',
                  highlight: 'Increases conversion by 40%'
                },
                {
                  icon: BarChart3,
                  title: 'Real-Time Analytics',
                  description: 'See exactly how much revenue your AI is generating.',
                  highlight: 'Live ROI tracking'
                },
                {
                  icon: AlertCircle,
                  title: 'Emergency Detection',
                  description: 'Recognizes urgent situations and escalates immediately.',
                  highlight: 'Smart priority routing'
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  variants={scrollAnimations.staggerChild}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
                  whileHover={{ scale: 1.05, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                >
                  <feature.icon className="w-12 h-12 text-blue-400 mb-4" />
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-sm opacity-90 mb-4">{feature.description}</p>
                  <div className="bg-blue-500/20 rounded-lg px-3 py-2 text-xs font-medium text-blue-300">
                    {feature.highlight}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" ref={pricingRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={pricingInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            <motion.h2
              className="text-5xl font-bold text-center mb-4"
              variants={scrollAnimations.staggerChild}
            >
              Simple, Transparent Pricing
            </motion.h2>
            <motion.p
              className="text-xl text-center mb-8 opacity-90"
              variants={scrollAnimations.staggerChild}
            >
              No per-minute fees. No hidden costs. Just unlimited calls for one flat rate.
            </motion.p>

            {/* Billing Toggle */}
            <motion.div
              className="flex justify-center mb-12"
              variants={scrollAnimations.staggerChild}
            >
              <div className="bg-white/10 rounded-lg p-1 flex">
                <button
                  onClick={() => setBillingCycle('monthly')}
                  className={`px-6 py-2 rounded-md font-medium transition-all duration-300 ${billingCycle === 'monthly'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                    }`}
                >
                  Monthly
                </button>
                <button
                  onClick={() => setBillingCycle('yearly')}
                  className={`px-6 py-2 rounded-md font-medium transition-all duration-300 ${billingCycle === 'yearly'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white'
                    }`}
                >
                  Yearly <span className="text-green-400 text-sm ml-1">(Save 17%)</span>
                </button>
              </div>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {plans.map((plan, index) => (
                <motion.div
                  key={index}
                  variants={scrollAnimations.staggerChild}
                  className={`relative bg-white/5 backdrop-blur-sm rounded-2xl p-8 border transition-all duration-300 ${plan.highlighted
                    ? 'border-blue-400 bg-white/10 scale-105'
                    : 'border-white/10 hover:border-white/20'
                    }`}
                  whileHover={{ scale: plan.highlighted ? 1.05 : 1.02 }}
                >
                  {plan.highlighted && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <div className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-bold">
                        Most Popular
                      </div>
                    </div>
                  )}

                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                    <p className="text-sm opacity-75 mb-4">{plan.description}</p>

                    <div className="mb-4">
                      <span className="text-5xl font-bold">${plan.price}</span>
                      <span className="text-lg opacity-75">
                        /{billingCycle === 'monthly' ? 'month' : 'year'}
                      </span>
                    </div>

                    <div className="bg-green-500/20 rounded-lg p-3 mb-4">
                      <div className="text-sm font-bold text-green-400">{plan.roi}</div>
                      <div className="text-xs opacity-90">{plan.savings}</div>
                    </div>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <PayPalButton
                    plan={plan.name}
                    variant={plan.highlighted ? "premium" : "primary"}
                    className="w-full"
                  >
                    {plan.cta}
                  </PayPalButton>
                </motion.div>
              ))}
            </div>

            <motion.p
              className="text-center text-sm opacity-75 mt-8"
              variants={scrollAnimations.staggerChild}
            >
              ✅ 30-day free trial • ✅ No setup fees • ✅ Cancel anytime • ✅ 99.7% uptime SLA
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" ref={testimonialsRef} className="py-20 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            animate={testimonialsInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            <motion.h2
              className="text-5xl font-bold text-center mb-4"
              variants={scrollAnimations.staggerChild}
            >
              Real Results from Real Businesses
            </motion.h2>
            <motion.p
              className="text-xl text-center mb-12 opacity-90"
              variants={scrollAnimations.staggerChild}
            >
              See how service professionals are transforming their businesses with AI
            </motion.p>

            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={index}
                  variants={scrollAnimations.staggerChild}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
                  whileHover={{ scale: 1.02, y: -5 }}
                >
                  <div className="flex items-center mb-4">
                    <div className="text-3xl mr-4">{testimonial.image}</div>
                    <div>
                      <div className="font-bold">{testimonial.name}</div>
                      <div className="text-sm opacity-75">{testimonial.role}</div>
                    </div>
                  </div>

                  <div className="flex mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>

                  <p className="text-sm mb-4 italic">"{testimonial.text}"</p>

                  <div className="bg-green-500/20 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-green-400">{testimonial.revenue}</div>
                    <div className="text-xs opacity-90">Additional Monthly Revenue</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="cta" ref={ctaRef} className="py-20 relative">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial="hidden"
            animate={ctaInView ? "visible" : "hidden"}
            variants={scrollAnimations.staggerContainer}
          >
            <motion.h2
              className="text-6xl font-bold mb-6"
              variants={scrollAnimations.staggerChild}
            >
              Stop Losing Money to Missed Calls
            </motion.h2>
            <motion.p
              className="text-2xl mb-8 opacity-95 max-w-3xl mx-auto"
              variants={scrollAnimations.staggerChild}
            >
              Your AI receptionist is ready to start booking appointments and capturing revenue
              while you focus on what you do best.
            </motion.p>

            <motion.div
              className="bg-red-500/20 rounded-xl p-6 mb-8 max-w-2xl mx-auto"
              variants={scrollAnimations.scaleIn}
            >
              <h3 className="text-xl font-bold mb-2 text-red-300">Every minute you wait:</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>• Another call goes to voicemail</div>
                <div>• A competitor answers instead</div>
                <div>• Potential revenue walks away</div>
                <div>• Your business growth stalls</div>
              </div>
            </motion.div>

            <motion.div
              className="flex flex-col md:flex-row gap-4 justify-center mb-8"
              variants={scrollAnimations.staggerChild}
            >
              <PayPalButton
                plan="Professional"
                variant="success"
                className="w-full md:w-auto"
              >
                Start Your Free Trial Now
              </PayPalButton>

              <motion.button
                onClick={() => scrollToSection('calculator')}
                className="border-2 border-white text-white px-12 py-6 rounded-lg font-bold text-xl transition-all duration-300"
                whileHover={{ scale: 1.05, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
                whileTap={{ scale: 0.95 }}
              >
                See Your ROI Again
              </motion.button>
            </motion.div>

            <motion.div
              className="text-sm opacity-75"
              variants={scrollAnimations.staggerChild}
            >
              <p>✅ Setup in under 10 minutes • ✅ Voice cloned in 24 hours • ✅ Start booking calls immediately</p>
              <p className="mt-2">Join 2,847+ service professionals already using AI to grow their business</p>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default SinglePageHero;