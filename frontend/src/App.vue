<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router"
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
      >
        <span class="navbar-toggler-icon" />
      </button>
      <div id="navbarSupportedContent" class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-md-0">
          <li class="nav-item" v-show="false">
            <a
              class="active btn btn-primary nav-link me-2"
              role="button"
              type="button"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/heart-fill.svg"
                alt="view icon"
                width="18"
                height="18"
              />Salvati
            </a>
          </li>
          <li class="nav-item" v-show="false">
            <a
              class="btn btn-primary nav-link me-2"
              title="Cronologia degli articoli già letti"
              role="button"
              type="button"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/clock-history.svg"
                alt="view icon"
                width="18"
                height="18"
              />Già letti
            </a>
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
                alt="view icon"
                width="18"
                height="18"
              />Nuovo
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink
              class="btn btn-primary nav-link me-2"
              title="Da dove arrivano gli artcoli"
              role="button"
              type="button"
              to="/feeds"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/rss.svg"
                alt="view icon"
                width="18"
                height="18"
              />Fonti
            </RouterLink>
          </li>
          <li class="nav-item" v-show="false">
            <a
              class="btn btn-primary nav-link me-2"
              title="Configura l'aggregatore al meglio"
              role="button"
              type="button"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/gear-fill.svg"
                alt="view icon"
                width="18"
                height="18"
              />Impostazioni
            </a>
          </li>
          <li class="nav-item">
            <a
              href="/about"
              class="btn btn-primary nav-link me-2"
              title="About"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/question.svg"
                alt="view icon"
                width="18"
                height="18"
              />Info
            </a>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto mb-2 mb-md-0">
          <li class="nav-item">
            <a
              href="/accounts/logout/"
              class="btn btn-primary nav-link me-2"
              title="Esci dall'aggregatore"
              role="button"
              type="button"
            >
              <img
                class="inverted-icon icon me-2"
                src="~bootstrap-icons/icons/unlock.svg"
                alt="view icon"
                width="18"
                height="18"
              />Esci
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
