import { useInView } from 'react-intersection-observer';

/**
 * Animation Utilities
 * 
 * Centralized animation configurations and utilities for consistent
 * performance and timing across the single-page hero experience
 */

// Animation configurations
export const animationConfig = {
  // Easing functions
  easing: {
    smooth: [0.25, 0.1, 0.25, 1],
    bounce: [0.68, -0.55, 0.265, 1.55],
    sharp: [0.4, 0, 0.2, 1],
    gentle: [0.25, 0.46, 0.45, 0.94],
  },

  // Duration presets
  duration: {
    fast: 0.3,
    normal: 0.6,
    slow: 1.2,
    verySlow: 2.0,
  },

  // Stagger delays
  stagger: {
    fast: 0.1,
    normal: 0.2,
    slow: 0.3,
  },
};

// Scroll animation variants
export const scrollAnimations = {
  // Fade in from bottom
  fadeInUp: {
    hidden: { 
      opacity: 0, 
      y: 60,
      transition: { duration: animationConfig.duration.normal }
    },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.smooth
      }
    }
  },

  // Fade in from left
  fadeInLeft: {
    hidden: { 
      opacity: 0, 
      x: -60,
      transition: { duration: animationConfig.duration.normal }
    },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.smooth
      }
    }
  },

  // Fade in from right
  fadeInRight: {
    hidden: { 
      opacity: 0, 
      x: 60,
      transition: { duration: animationConfig.duration.normal }
    },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.smooth
      }
    }
  },

  // Scale in
  scaleIn: {
    hidden: { 
      opacity: 0, 
      scale: 0.8,
      transition: { duration: animationConfig.duration.fast }
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.bounce
      }
    }
  },

  // Staggered container
  staggerContainer: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: animationConfig.stagger.normal,
        delayChildren: 0.1,
      }
    }
  },

  // Staggered child
  staggerChild: {
    hidden: { 
      opacity: 0, 
      y: 30,
    },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: animationConfig.duration.normal,
        ease: animationConfig.easing.smooth
      }
    }
  }
};

// Button hover animations
export const buttonAnimations = {
  primary: {
    rest: { 
      scale: 1,
      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    },
    hover: { 
      scale: 1.05,
      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
      transition: { 
        duration: animationConfig.duration.fast,
        ease: animationConfig.easing.smooth
      }
    },
    tap: { 
      scale: 0.95,
      transition: { 
        duration: 0.1,
        ease: animationConfig.easing.sharp
      }
    }
  },

  secondary: {
    rest: { 
      scale: 1,
      borderColor: "rgba(255, 255, 255, 0.5)"
    },
    hover: { 
      scale: 1.02,
      borderColor: "rgba(255, 255, 255, 1)",
      backgroundColor: "rgba(255, 255, 255, 0.1)",
      transition: { 
        duration: animationConfig.duration.fast,
        ease: animationConfig.easing.smooth
      }
    },
    tap: { 
      scale: 0.98,
      transition: { 
        duration: 0.1,
        ease: animationConfig.easing.sharp
      }
    }
  }
};

// Number counting animation
export const createCountingAnimation = (from, to, duration = 2) => {
  return {
    from,
    to,
    config: {
      duration: duration * 1000, // Convert to milliseconds
      easing: animationConfig.easing.smooth,
    }
  };
};

// Performance utilities
export const performanceUtils = {
  // Check if user prefers reduced motion
  prefersReducedMotion: () => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  // Get device performance tier
  getPerformanceTier: () => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const memory = navigator.deviceMemory || 4;
    
    // High performance: Good connection + high memory
    if (memory >= 8 && (!connection || connection.effectiveType === '4g')) {
      return 'high';
    }
    
    // Medium performance: Decent specs
    if (memory >= 4) {
      return 'medium';
    }
    
    // Low performance: Limited specs
    return 'low';
  },

  // Adjust animation complexity based on performance
  getOptimizedConfig: () => {
    const tier = performanceUtils.getPerformanceTier();
    const reducedMotion = performanceUtils.prefersReducedMotion();
    
    if (reducedMotion) {
      return {
        enableParticles: false,
        enableComplexAnimations: false,
        staggerDelay: 0,
        duration: 0.1,
      };
    }
    
    switch (tier) {
      case 'high':
        return {
          enableParticles: true,
          enableComplexAnimations: true,
          particleCount: 80,
          staggerDelay: animationConfig.stagger.normal,
          duration: animationConfig.duration.normal,
        };
      case 'medium':
        return {
          enableParticles: true,
          enableComplexAnimations: true,
          particleCount: 50,
          staggerDelay: animationConfig.stagger.fast,
          duration: animationConfig.duration.fast,
        };
      case 'low':
        return {
          enableParticles: false,
          enableComplexAnimations: false,
          particleCount: 20,
          staggerDelay: 0,
          duration: animationConfig.duration.fast,
        };
      default:
        return {
          enableParticles: true,
          enableComplexAnimations: true,
          particleCount: 50,
          staggerDelay: animationConfig.stagger.normal,
          duration: animationConfig.duration.normal,
        };
    }
  }
};

// Intersection observer hook for scroll animations
export const useScrollAnimation = (threshold = 0.1) => {
  const [ref, inView] = useInView({
    threshold,
    triggerOnce: true,
    rootMargin: '-50px 0px',
  });

  return [ref, inView];
};

// Export default configuration
export default {
  animationConfig,
  scrollAnimations,
  buttonAnimations,
  createCountingAnimation,
  performanceUtils,
};