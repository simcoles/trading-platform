import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    // Same result on every machine and in CI, whatever the local timezone
    env: { TZ: "UTC" },
  },
});
