/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",   // wherever your components live
  ],
  theme: {
    extend: {
      fontFamily: {
        // redefine the `sans` key that Tailwind’s `font-sans` uses
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'Oxygen',
          'Ubuntu',
          'Cantarell',
          '"Open Sans"',
          '"Helvetica Neue"',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
};
