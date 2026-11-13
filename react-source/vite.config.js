import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "./" lets the built site live at any sub-path (e.g. GitHub Pages /TCH30/)
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: { port: 5173 },
});
