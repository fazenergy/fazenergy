/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Se quiser customizar fontes, cores ou breakpoints aqui
      colors: {
        emerald: {
          500: '#5cb85c',
          600: '#53a353',
          700: '#4a934a',
        },
        green: {
          500: '#5cb85c',
          600: '#53a353',
          700: '#4a934a',
        }
      }
    },
  },
  plugins: [],
}
