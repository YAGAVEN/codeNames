// /media/yagaven_25/coding/Projects/codeNames/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        saffron: '#FF9933',
        indiaBlue: '#003580',
        emerald: '#10B981',
        gold: '#F59E0B',
        night: '#0A0A14',
        navy: '#0F0F2D',
        cream: '#FFF7E6',
        danger: '#EF4444',
        teamRed: '#EF4444',
        teamBlue: '#2563EB'
      },
      fontFamily: {
        heading: ['Rajdhani', 'Teko', 'system-ui', 'sans-serif'],
        body: ['Inter', 'DM Sans', 'system-ui', 'sans-serif'],
        label: ['"Baloo 2"', 'Inter', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        saffron: '0 0 36px rgba(255,153,51,0.35)',
        blueGlow: '0 0 36px rgba(37,99,235,0.35)',
        emeraldGlow: '0 0 32px rgba(16,185,129,0.28)',
        card: '0 18px 60px rgba(0,0,0,0.38)'
      },
      backgroundImage: {
        'festival-radial':
          'radial-gradient(circle at top left, rgba(255,153,51,0.22), transparent 32%), radial-gradient(circle at bottom right, rgba(16,185,129,0.18), transparent 34%)',
        'rangoli-lines':
          'linear-gradient(135deg, rgba(255,153,51,0.12) 25%, transparent 25%), linear-gradient(225deg, rgba(16,185,129,0.10) 25%, transparent 25%)'
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 rgba(255,153,51,0)' },
          '50%': { boxShadow: '0 0 34px rgba(255,153,51,0.45)' }
        },
        floatUp: {
          '0%': { opacity: 0, transform: 'translateY(14px) scale(0.9)' },
          '18%': { opacity: 1 },
          '100%': { opacity: 0, transform: 'translateY(-92px) scale(1.2)' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.8s infinite',
        pulseGlow: 'pulseGlow 1.5s ease-in-out infinite',
        floatUp: 'floatUp 1.8s ease-out forwards'
      }
    }
  },
  plugins: [
    ({ addVariant }) => {
      addVariant('light', '.light &');
    }
  ]
};
