import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy all /v1/* requests to FastAPI on :8000
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/v1": "http://localhost:8000"
    }
  }
});
