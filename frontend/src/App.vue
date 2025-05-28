<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router"
import { fetch_wrapper } from "./utils"
import type { components } from "./generated/schema.d.ts"
type PatchedUser = components["schemas"]["PatchedUser"]
import { useAuthStore } from "./stores/auth.store"
import { onMounted } from "vue"

const auth = useAuthStore()

async function fetchUser() {
  const url = `/api/users/me/`
  const response = await fetch_wrapper(url)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const user: PatchedUser = await response.json()
    auth.login(user)
  }
}

onMounted(() => {
  console.log("App mounted")
  fetchUser()
})

function logout() {
  auth.logout()
  document.location = "/accounts/logout/"
}
</script>

<template>
  <nav class="navbar navbar-expand-md bg-primary" data-bs-theme="dark">
    <div class="container-fluid">
      <RouterLink to="/" class="navbar-brand ms-3">
        <img alt="Flash logo" src="./assets/logo.svg" width="50" />
      </RouterLink>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
        title="Toggle navigation"
      >
        <span class="navbar-toggler-icon" />
      </button>
      <div id="navbarSupportedContent" class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-md-0">
          <li class="nav-item">
            <RouterLink
              class="btn btn-primary nav-link me-2"
              title="Articoli salvati nelle liste"
              role="button"
              type="button"
              to="/lists"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/heart-fill.svg"
                alt="heart icon"
                width="18"
                height="18"
              />Salvati
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink
              class="btn btn-primary nav-link me-2"
              title="Segnala un articolo"
              role="button"
              type="button"
              to="/new_article"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/plus-circle-fill.svg"
                alt="plus circle fill icon"
                width="18"
                height="18"
              />Nuovo
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink
              class="btn btn-primary nav-link me-2"
              title="Da dove arrivano gli articoli"
              role="button"
              type="button"
              to="/feeds"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/rss.svg"
                alt="rss icon"
                width="18"
                height="18"
              />Fonti
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink
              class="btn btn-primary nav-link me-2"
              title="Configura l'aggregatore al meglio"
              role="button"
              type="button"
              to="/settings"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/sliders.svg"
                alt="settings icon"
                width="18"
                height="18"
              />Impostazioni
            </RouterLink>
          </li>
          <li class="nav-item">
            <a href="/about" class="btn btn-primary nav-link me-2" title="About">
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/question.svg"
                alt="question icon"
                width="18"
                height="18"
              />Info
            </a>
          </li>
          <li class="nav-item" v-if="auth.user?.is_staff">
            <a
              href="/admin"
              class="btn btn-danger nav-link me-2"
              title="Pannello di amministrazione del sito (funzione riservata agli utenti di staff)"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/lock.svg"
                alt="lock icon"
                width="18"
                height="18"
              />Admin
            </a>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto mb-2 mb-md-0">
          <li class="nav-item">
            <a
              href="#"
              class="btn btn-primary nav-link me-2"
              title="Esci dall'aggregatore"
              role="button"
              type="button"
              @click="logout()"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/unlock.svg"
                alt="unlock icon"
                width="18"
                height="18"
              />Disconnetti [{{ auth.user?.username }}]
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  <main>
    <RouterView v-slot="{ Component }">
      <KeepAlive>
        <component :is="Component" />
      </KeepAlive>
    </RouterView>
  </main>
</template>

<style lang="scss">
// https://www.pantone.com/eu/it/color-of-the-year-2022: Very Peri (#6767ab)
// https://www.pantone.com/eu/it/color-of-the-year/2023: Viva Magenta (#bb2649)
// https://www.pantone.com/eu/it/color-of-the-year/2024: Peach Fuzz (#febe98)
// https://www.pantone.com/eu/it/color-of-the-year/2025: Mocha Mousse (#a47764)
$primary: #7b5140; // "dark" Mocha Mousse
$secondary: #febe98; // Peach Fuzz

@import "bootstrap";
@import "quill/dist/quill.snow.css";

.inverted-icon {
  filter: invert(1);
}
</style>
