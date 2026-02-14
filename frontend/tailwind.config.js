/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0A66C2",
        secondary: "#0073B1",
        accent: "#F3F4F6",
        dark: "#101820",
      }
    },
  },
  plugins: [],
}


// colors: {
//   primary: "#0A66C2",
//   secondary: "#0073B1",
//   accent: "#F3F4F6",
//   dark: "#101820",
// }