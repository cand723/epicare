/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.html"],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-body": "linear-gradient(to bottom, #003539 0%, #00885C 100%)",
      },
      fontFamily: {
        jakarta: ['"Plus Jakarta Sans"', "sans-serif"],
      },
    },
  },
  plugins: [typography],
};