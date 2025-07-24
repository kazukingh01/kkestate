import type { Config } from 'tailwindcss'

export default {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{html,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config