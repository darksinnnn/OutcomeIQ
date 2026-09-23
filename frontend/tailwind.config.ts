import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        base: '#14171A',
        panel: '#1B1F23',
        elevated: '#22272C',
        hairline: '#2C3238',
        text: {
          primary: '#EDEFF1',
          secondary: '#9AA3AC',
          muted: '#6B747C',
        },
        accent: {
          DEFAULT: '#F2A93B',
          muted: '#8A6425',
        },
        status: {
          green: '#4CAF7D',
          amber: '#E0A63C',
          red: '#E5484D',
        },
        data: {
          blue: '#5B8DEF',
          blueMuted: '#3A5A99',
        },
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '10px',
      },
      boxShadow: {
        elevated: '0 8px 24px rgba(0, 0, 0, 0.35)',
      },
      screens: {
        'tablet': '768px',
        'desktop': '1024px',
        'wide': '1440px',
      },
    },
  },
  plugins: [],
};

export default config;
