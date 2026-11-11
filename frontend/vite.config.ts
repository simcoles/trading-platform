import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // @highcharts/react's lazy series imports break Vite's dev pre-bundling
  // ("Class extends value undefined"), so serve it unbundled
  optimizeDeps: { exclude: ["@highcharts/react"] },
  test: {
    // Same result on every machine and in CI, whatever the local timezone
    env: { TZ: "UTC" },
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
  },
});
