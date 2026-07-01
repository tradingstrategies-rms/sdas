/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // SDAS brand colors — deep Singapore navy + gold
        brand: {
          navy: '#0B1929',
          "navy-light": '#132337',
          gold: '#C9A84C',
          "gold-light": '#E2C06E',
          "gold-muted": '#8B6F2F',
        },
        signal: {
          buy: '#16a34a',
          "buy-bg": '#f0fdf4',
          watch: '#d97706',
          "watch-bg": '#fffbeb',
          over: '#dc2626',
          "over-bg": '#fef2f2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
