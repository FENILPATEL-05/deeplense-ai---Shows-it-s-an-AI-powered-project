import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        accent: {
          light: "#1a73e8",
          dark: "#8ab4f8",
        },
        surface: {
          light: "#f8f9fa",
          dark: "#2d2d2d",
        },
      },
    },
  },
  plugins: [],
};

export default config;
