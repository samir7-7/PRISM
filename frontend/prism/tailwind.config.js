/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'prism-bg': '#0d1117',
        'prism-surface': '#161b22',
        'prism-border': '#21262d',
        'prism-orange': '#f97316',
        'prism-green': '#22c55e',
        'prism-red': '#ef4444',
        'prism-yellow': '#eab308',
        'prism-blue': '#3b82f6',
        'prism-text': '#e6edf3',
        'prism-text-muted': '#8b949e',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

// Made with Bob
