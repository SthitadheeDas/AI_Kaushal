/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        upgov: {
          blue: "#1e3a8a",
          emerald: "#059669",
          amber: "#d97706",
          purple: "#7c3aed",
          dark: "#0f172a",
        },
      },
    },
  },
  plugins: [],
};
