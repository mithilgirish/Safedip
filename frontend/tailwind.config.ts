import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        safe: { DEFAULT: "#10b981", bg: "rgba(16, 185, 129, 0.1)" },
        caution: { DEFAULT: "#f59e0b", bg: "rgba(245, 158, 11, 0.1)" },
        unsafe: { DEFAULT: "#ef4444", bg: "rgba(239, 68, 68, 0.1)" },
      },
    },
  },
  plugins: [],
};
export default config;
