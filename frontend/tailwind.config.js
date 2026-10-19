/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#07090e',
          900: '#0b0f17',
          850: '#101520',
          800: '#151c2b',
          750: '#1a2233',
          700: '#222b40',
          600: '#2f3b54',
          500: '#465675',
        },
        border: {
          subtle: '#1f2738',
          default: '#2a354c',
          active: '#3b4968',
        },
        accent: {
          violet: '#8b5cf6',
          'violet-hover': '#7c3aed',
          cyan: '#06b6d4',
          'cyan-hover': '#0891b2',
          glow: 'rgba(139, 92, 246, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
}
