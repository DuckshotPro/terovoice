import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

/**
 * AnimatedBackground Component
 *
 * Creates a particle system background with floating elements
 * Integrates with existing backgroundImage.jpg for layered effect
 */

// Particle configuration based on intensity
const PARTICLE_CONFIGS = {
  subtle: { count: 30, speed: 0.5, size: 2 },
  medium: { count: 50, speed: 1, size: 3 },
  dynamic: { count: 80, speed: 1.5, size: 4 },
};

// Color schemes
const COLOR_SCHEMES = {
  blue: ['rgba(59, 130, 246, 0.1)', 'rgba(147, 197, 253, 0.1)', 'rgba(219, 234, 254, 0.1)'],
  purple: ['rgba(147, 51, 234, 0.1)', 'rgba(196, 181, 253, 0.1)', 'rgba(233, 213, 255, 0.1)'],
  gradient: ['rgba(59, 130, 246, 0.1)', 'rgba(147, 51, 234, 0.1)', 'rgba(236, 72, 153, 0.1)'],
};

// Particle class
class Particle {
  constructor(canvas, config, colors) {
    this.canvas = canvas;
    this.config = config;
    this.colors = colors;
    this.reset();
    this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
  }

  reset() {
    this.x = Math.random() * this.canvas.width;
    this.y = Math.random() * this.canvas.height;
    this.vx = (Math.random() - 0.5) * this.config.speed;
    this.vy = (Math.random() - 0.5) * this.config.speed;
    this.size = Math.random() * this.config.size + 1;
    this.opacity = Math.random() * 0.5 + 0.1;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // Wrap around edges
    if (this.x < 0) this.x = this.canvas.width;
    if (this.x > this.canvas.width) this.x = 0;
    if (this.y < 0) this.y = this.canvas.height;
    if (this.y > this.canvas.height) this.y = 0;

    // Subtle floating motion
    this.y += Math.sin(Date.now() * 0.001 + this.x * 0.01) * 0.1;
  }

  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.opacity;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

const AnimatedBackground = ({
  variant = 'particles',
  intensity = 'medium',
  colorScheme = 'blue',
  backgroundImage,
}) => {
  const canvasRef = useRef(null);
  const particlesRef = useRef([]);
  const animationRef = useRef(null);

  // Initialize particles
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const config = PARTICLE_CONFIGS[intensity];
    const colors = COLOR_SCHEMES[colorScheme];

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create particles
    particlesRef.current = [];
    for (let i = 0; i < config.count; i++) {
      particlesRef.current.push(new Particle(canvas, config, colors));
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach((particle) => {
        particle.update();
        particle.draw(ctx);
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [variant, intensity, colorScheme]);

  return (
    <div className="fixed inset-0 -z-10">
      {/* Background Image Layer */}
      {backgroundImage && (
        <motion.div
          className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${backgroundImage})` }}
          initial={{ scale: 1.1, opacity: 0 }}
          animate={{ scale: 1, opacity: 0.3 }}
          transition={{ duration: 2, ease: 'easeOut' }}
        />
      )}

      {/* Gradient Overlay */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/10 to-blue-900/20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.5 }}
      />

      {/* Particle Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ mixBlendMode: 'screen' }}
      />

      {/* Animated Geometric Shapes */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-64 h-64 rounded-full border border-white/5"
            style={{
              left: `${20 + i * 15}%`,
              top: `${10 + i * 12}%`,
            }}
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 180, 360],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: 20 + i * 5,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default AnimatedBackground;
