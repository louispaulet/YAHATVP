import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "VITE_");
  return {
    base: "./",
    plugins: [react(), tailwindcss()],
    server: mode === "development" && env.VITE_API_PROXY_TARGET
      ? { proxy: { "/api": { target: env.VITE_API_PROXY_TARGET, changeOrigin: true } } }
      : undefined,
  };
});
