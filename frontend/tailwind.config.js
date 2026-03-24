/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:       '#000000',
        surface:  '#0A0A0A',
        surface2: '#121212',
        border:   '#1C1C1C',
        accent:   '#F9C935',
        orange:   '#FF6B35',
        blue:     '#3B82F6',
        warn:     '#FFB800',
        muted:    '#6B7280',
      },
      fontFamily: {
        mono: ['"Space Mono"', 'monospace'],
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
