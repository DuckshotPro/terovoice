import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CreditCard, 
  Shield, 
  CheckCircle, 
  ArrowRight, 
  Lock,
  Zap
} from 'lucide-react';

/**
 * Premium PayPal Subscription Button Component
 * 
 * Enterprise-grade checkout experience for AI Receptionist SaaS
 * Maintains PayPal security while looking premium
 */

const PayPalButton = ({ plan, className, children, variant = 'primary' }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSecurityBadge, setShowSecurityBadge] = useState(false);

  const handlePayPalSubscription = async () => {
    setIsProcessing(true);
    
    // Real PayPal Plan IDs from environment variables
    const planIds = {
      'Solo Pro': import.meta.env.VITE_PAYPAL_SOLO_PRO_PLAN_ID,
      'Professional': import.meta.env.VITE_PAYPAL_PROFESSIONAL_PLAN_ID,
      'Enterprise': import.meta.env.VITE_PAYPAL_ENTERPRISE_PLAN_ID
    };

    const planId = planIds[plan];
    const clientId = import.meta.env.VITE_PAYPAL_CLIENT_ID;
    const environment = import.meta.env.VITE_PAYPAL_ENVIRONMENT || 'sandbox';
    
    // Simulate processing delay for premium feel
    await new Promise(resolve => setTimeout(resolve, 800));
    
    if (planId && clientId) {
      // Real PayPal subscription URL with return URL to member portal
      const returnUrl = encodeURIComponent(`${window.location.origin}/member-portal?plan=${encodeURIComponent(plan)}&status=success`);
      const cancelUrl = encodeURIComponent(`${window.location.origin}/?status=cancelled`);
      
      const paypalUrl = environment === 'production' 
        ? `https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=${planId}&return_url=${returnUrl}&cancel_url=${cancelUrl}`
        : `https://www.sandbox.paypal.com/webapps/billing/plans/subscribe?plan_id=${planId}&return_url=${returnUrl}&cancel_url=${cancelUrl}`;
      
      window.open(paypalUrl, '_blank');
    } else if (plan === 'Enterprise') {
      // Enterprise plans go to sales contact
      window.location.href = 'mailto:sales@tero-ai.com?subject=Enterprise Plan Inquiry';
    } else {
      // Fallback - show setup instructions
      alert(`⚙️ PayPal Setup Required\n\nTo enable ${plan} subscriptions:\n1. Add your PayPal Client ID to .env file\n2. Create subscription plans in PayPal dashboard\n3. Add Plan IDs to .env file\n\nSee PAYPAL_INTEGRATION_OPTIONS.md for detailed setup instructions.`);
    }
    
    setIsProcessing(false);
  };

  // Premium button variants
  const variants = {
    primary: {
      base: "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-xl hover:shadow-2xl",
      icon: "text-blue-100",
      processing: "from-blue-500 to-blue-600"
    },
    success: {
      base: "bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-xl hover:shadow-2xl",
      icon: "text-green-100", 
      processing: "from-green-500 to-green-600"
    },
    premium: {
      base: "bg-gradient-to-r from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 text-white shadow-xl hover:shadow-2xl",
      icon: "text-purple-100",
      processing: "from-purple-500 to-indigo-600"
    }
  };

  const currentVariant = variants[variant] || variants.primary;

  return (
    <div className="relative group">
      <motion.button
        onClick={handlePayPalSubscription}
        disabled={isProcessing}
        className={`
          relative overflow-hidden px-8 py-4 rounded-xl font-bold text-lg
          transition-all duration-300 transform
          ${currentVariant.base}
          ${isProcessing ? `bg-gradient-to-r ${currentVariant.processing} cursor-not-allowed` : 'hover:scale-105'}
          ${className}
        `}
        whileHover={{ scale: isProcessing ? 1 : 1.02 }}
        whileTap={{ scale: isProcessing ? 1 : 0.98 }}
        onHoverStart={() => setShowSecurityBadge(true)}
        onHoverEnd={() => setShowSecurityBadge(false)}
      >
        {/* Animated background gradient */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent"
          animate={{
            x: isProcessing ? ['-100%', '100%'] : '0%',
          }}
          transition={{
            duration: isProcessing ? 1.5 : 0,
            repeat: isProcessing ? Infinity : 0,
            ease: "linear"
          }}
        />

        {/* Button content */}
        <div className="relative flex items-center justify-center space-x-3">
          <AnimatePresence mode="wait">
            {isProcessing ? (
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex items-center space-x-3"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Zap className={`w-5 h-5 ${currentVariant.icon}`} />
                </motion.div>
                <span>Securing Your Subscription...</span>
              </motion.div>
            ) : (
              <motion.div
                key="ready"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex items-center space-x-3"
              >
                <CreditCard className={`w-5 h-5 ${currentVariant.icon}`} />
                <span>{children}</span>
                <ArrowRight className={`w-5 h-5 ${currentVariant.icon} group-hover:translate-x-1 transition-transform`} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Premium shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12"
          animate={{
            x: ['-200%', '200%'],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            repeatDelay: 3,
            ease: "easeInOut"
          }}
        />
      </motion.button>

      {/* Security badge tooltip */}
      <AnimatePresence>
        {showSecurityBadge && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            className="absolute -top-16 left-1/2 transform -translate-x-1/2 z-50"
          >
            <div className="bg-gray-900 text-white px-4 py-2 rounded-lg shadow-xl border border-gray-700">
              <div className="flex items-center space-x-2 text-sm">
                <Shield className="w-4 h-4 text-green-400" />
                <span>256-bit SSL Encrypted</span>
                <Lock className="w-4 h-4 text-blue-400" />
              </div>
              <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45 border-r border-b border-gray-700"></div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Trust indicators */}
      <motion.div 
        className="flex items-center justify-center space-x-4 mt-3 text-xs opacity-75"
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.75 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-center space-x-1">
          <CheckCircle className="w-3 h-3 text-green-400" />
          <span>Instant Setup</span>
        </div>
        <div className="flex items-center space-x-1">
          <Shield className="w-3 h-3 text-blue-400" />
          <span>PayPal Protected</span>
        </div>
        <div className="flex items-center space-x-1">
          <Lock className="w-3 h-3 text-purple-400" />
          <span>Cancel Anytime</span>
        </div>
      </motion.div>
    </div>
  );
};

export default PayPalButton;