import { defineConfig } from "vite";

export default defineConfig({
  base: "/rag/",
  esbuild: { jsx: "transform", jsxFactory: "h", jsxFragment: "Fragment" },
  server: { host: "127.0.0.1", port: 4173, strictPort: true },
});
