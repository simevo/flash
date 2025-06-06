import { fileURLToPath, URL } from "node:url"

import { resolve } from "path"
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import vueDevTools from "vite-plugin-vue-devtools"
import { VitePWA } from "vite-plugin-pwa"
import package_json from "./package.json"

// https://vite.dev/config/
export default defineConfig({
  base: "/res/",
  plugins: [
    vue(),
    vueDevTools(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["src/assets/favicon.ico", "src/assets/logo.svg"],
      manifest: {
        name: "Flash",
        short_name: "Flash",
        description: "The open-source news platform with aggregation and ranking",
        theme_color: "#7b5140", // "dark" Mocha Mousse
        icons: [
          {
            src: "pwa-64x64.png",
            sizes: "64x64",
            type: "image/png",
          },
          {
            src: "pwa-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "maskable-icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
  ],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
      },
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    allowedHosts: ["flash"],
  },
  define: {
      VUE_APP_VERSION: JSON.stringify(package_json.version),
    },
})
