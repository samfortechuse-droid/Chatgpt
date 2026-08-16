export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}'
  ],

  theme: {
    extend: {
      colors: {
        bg: {
          pure: '#030303',
          panel: 'rgba(255, 255, 255, 0.02)'
        },

        glass: {
          border: 'rgba(255, 255, 255, 0.08)'
        }
      },

      fontFamily: {
        sans: [
          'var(--font-geist-sans)',
          'system-ui',
          'sans-serif'
        ]
      },

      animation: {
        'pulse-slow':
          'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite'
      }
    }
  }
}
