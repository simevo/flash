import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import { useProfileStore } from "./stores/profile.store"
import router from "./router"
import Vue3Toastify, { type ToastContainerOptions } from "vue3-toastify"
import "vue3-toastify/dist/index.css"

import "bootstrap/dist/js/bootstrap.min.js"

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(Vue3Toastify, {
  theme: "light",
  position: "top-left",
  transition: "slide",
} as ToastContainerOptions)
app.mount("#app")

app.config.globalProperties.base_language = "it"
app.provide("base_language", app.config.globalProperties["base_language"])

useProfileStore().set_font_size()
