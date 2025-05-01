<template>
  <div class="container">
    <h1>
      Impostazioni
      <span class="btn-group" role="group" aria-label="Font size">
        <button
          class="btn btn-outline-primary"
          @click="useProfileStore().reduce_font_size()"
          title="Riduci dimensione carattere"
        >
          A-
        </button>
        <button
          class="btn btn-outline-primary"
          @click="useProfileStore().reset_font_size()"
          title="Ripristina dimensione carattere"
        >
          A=
        </button>
        <button
          class="btn btn-outline-primary"
          @click="useProfileStore().enlarge_font_size()"
          title="Aumenta dimensione carattere"
        >
          A+
        </button>
      </span>
    </h1>
    <p>
      Personalizza il tuo newsfeed! Queste impostazioni controllano quali articoli verranno mostrati
      nel
      <img
        class="icon"
        src="~bootstrap-icons/icons/robot.svg"
        alt="rss icon"
        width="18"
        height="18"
        title="Lista automatica"
      />
      <b> newsfeed</b> alla pagina
      <RouterLink to="/lists"
        ><img
          class="icon me-2"
          src="~bootstrap-icons/icons/heart-fill.svg"
          alt="filled heart icon"
          width="18"
          height="18"
        /><b>Salvati</b></RouterLink
      >, in che ordine e per quanto tempo rimarranno visibili.
    </p>
    <p class="text-muted">
      Nota: il newsfeed viene aggiornato ogni ora circa quindi c'è un ritardo nell'aggiornamento!
    </p>
    <ul class="nav nav-tabs" id="myTab" role="tablist">
      <li class="nav-item" role="presentation">
        <button
          class="nav-link active"
          id="whitelist-tab"
          data-bs-toggle="tab"
          data-bs-target="#whitelist-tab-pane"
          type="button"
          role="tab"
          aria-controls="whitelist-tab-pane"
          aria-selected="true"
        >
          Lista parole prioritarie
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          id="blacklist-tab"
          data-bs-toggle="tab"
          data-bs-target="#blacklist-tab-pane"
          type="button"
          role="tab"
          aria-controls="blacklist-tab-pane"
          aria-selected="false"
        >
          Lista parole vietate
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          id="languages-tab"
          data-bs-toggle="tab"
          data-bs-target="#languages-tab-pane"
          type="button"
          role="tab"
          aria-controls="languages-tab-pane"
          aria-selected="false"
        >
          Lingue
        </button>
      </li>
    </ul>
    <div class="tab-content py-3 bg-light" id="myTabContent">
      <div
        class="tab-pane fade show active"
        id="whitelist-tab-pane"
        role="tabpanel"
        aria-labelledby="whitelist-tab"
        tabindex="0"
      >
        <div class="container">
          <p>
            Scegli le parole che vuoi che vengano messe in risalto nel tuo newsfeed personalizzato.
          </p>
          <div v-if="profile?.whitelist?.length ?? 0 > 0">
            <span
              v-for="word in profile?.whitelist"
              :key="word"
              class="badge text-bg-success m-1 p-2"
            >
              {{ word }}
              <button
                type="button"
                class="btn-close btn-close-white"
                aria-label="Elimina parola"
                title="Elimina parola"
                data-bs-theme="dark"
                @click="removeItem('whitelist', word)"
              ></button>
            </span>
          </div>
          <div v-else>
            <p class="text-muted">Nessuna parola prioritaria selezionata.</p>
          </div>
          <button
            type="button"
            class="btn btn-danger mt-3"
            @click="clearList('whitelist')"
            :disabled="profile?.whitelist?.length === 0"
          >
            Rimuovi tutte le parole prioritarie
          </button>
          <button type="button" class="btn btn-success mt-3 ms-3" @click="promptItem('whitelist')">
            Aggiungi una parola prioritaria
          </button>
        </div>
      </div>
      <div
        class="tab-pane fade"
        id="blacklist-tab-pane"
        role="tabpanel"
        aria-labelledby="blacklist-tab"
        tabindex="0"
      >
        <div class="container">
          <p>Scegli le parole che non vuoi che compaiano nel tuo newsfeed personalizzato.</p>
          <div v-if="profile?.blacklist?.length ?? 0 > 0">
            <span
              v-for="word in profile?.blacklist"
              :key="word"
              class="badge text-bg-danger m-1 p-2"
            >
              {{ word }}
              <button
                type="button"
                class="btn-close btn-close-white"
                aria-label="Elimina parola"
                title="Elimina parola"
                data-bs-theme="dark"
                @click="removeItem('blacklist', word)"
              ></button>
            </span>
          </div>
          <div v-else>
            <p class="text-muted">Nessuna parola vietata selezionata.</p>
          </div>
          <button
            type="button"
            class="btn btn-success mt-3"
            @click="clearList('blacklist')"
            :disabled="profile?.blacklist?.length === 0"
          >
            Rimuovi tutte le parole vietate
          </button>
          <button type="button" class="btn btn-danger mt-3 ms-3" @click="promptItem('blacklist')">
            Aggiungi una parola vietata
          </button>
        </div>
      </div>
      <div
        class="tab-pane fade"
        id="languages-tab-pane"
        role="tabpanel"
        aria-labelledby="languages-tab"
        tabindex="0"
      >
        <div class="container">
          <p>Seleziona le lingue.</p>
          <div v-if="profile?.languages?.length ?? 0 > 0">
            <span
              v-for="code in profile?.languages"
              :key="code"
              class="badge text-bg-secondary m-1 p-2"
            >
              {{ languages[code] }}
              <button
                type="button"
                class="btn-close"
                aria-label="Elimina parola"
                title="Elimina parola"
                @click="removeItem('languages', code)"
              ></button>
            </span>
          </div>
          <div v-else>
            <p class="text-muted">
              Nessuna lingua selezionata (nel tuo newsfeed appariranno articoli in qualsiasi lingua)
            </p>
          </div>
          <button
            type="button"
            class="btn btn-danger mt-3"
            @click="clearList('languages')"
            :disabled="profile?.languages?.length === 0"
          >
            Rimuovi tutte le lingue
          </button>
          <span class="dropdown">
            <button
              class="btn btn-secondary dropdown-toggle mt-3 ms-3"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              :disabled="availableLanguages.length === 0"
            >
              Aggiungi una lingua
            </button>
            <ul class="dropdown-menu text-bg-secondary">
              <li v-for="code in availableLanguages" :key="code">
                <a class="dropdown-item" href="#" @click="addItem('languages', code)">{{
                  languages[code]
                }}</a>
              </li>
            </ul>
          </span>
        </div>
      </div>
    </div>
    <div class="text-center mt-3">
      <button type="button" class="btn btn-primary" :disabled="!dirty" @click="save">
        Salva le modifiche
      </button>
      <button type="button" class="btn btn-danger ms-3" @click="clearAll" :disabled="!dirty">
        Annulla le modifiche
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"
import { fetch_wrapper } from "@/utils.js"
import { useProfileStore } from "../stores/profile.store"

type Profile = components["schemas"]["Profile"]

const profile: Ref<Profile | null> = ref(null)

const original_profile = ref<Profile | null>(null)

const languages: { [key: string]: string } = {
  ar: "Arabo",
  ca: "Catalano",
  fr: "Francese",
  en: "Inglese",
  it: "Italiano",
  nl: "Olandese",
  pt: "Portoghese",
  ru: "Russo",
  es: "Spagnolo",
  de: "Tedesco",
}

// define a computed that returns an array of languages not in profile.languages
const availableLanguages = computed(() => {
  return Object.keys(languages).filter((code) => !profile.value?.languages?.includes(code))
})

// Fetch the profile data
async function fetchProfile() {
  const response = await fetch_wrapper(`../../api/profile/me/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Profile = await response.json()
    profile.value = data
    original_profile.value = JSON.parse(JSON.stringify(data))
  }
}

const dirty = computed(() => {
  return JSON.stringify(profile.value) !== JSON.stringify(original_profile.value)
})

type ProfileKeys = "whitelist" | "blacklist" | "languages"

function promptItem(list: ProfileKeys) {
  const item = window.prompt("Inserisci la parola da aggiungere:")
  if (item) {
    if (profile.value && profile.value[list] && !profile.value[list].includes(item)) {
      profile.value[list].push(item)
    }
  }
}

function clearList(list: ProfileKeys) {
  if (window.confirm("Le vuoi davvero rimuovere tutte?")) {
    if (profile.value && profile.value[list]) {
      profile.value[list] = []
    }
  }
}

function addItem(list: ProfileKeys, item: string) {
  if (profile.value && profile.value[list] && !profile.value[list].includes(item)) {
    profile.value[list].push(item)
  }
}

function removeItem(list: ProfileKeys, item: string) {
  if (profile.value && profile.value[list]) {
    profile.value[list] = profile.value[list].filter((item2) => item2 !== item)
  }
}

// Fetch the profile data when the component is mounted
onMounted(() => {
  console.log("SettingsView mounted")
  fetchProfile()
})

async function save() {
  const response = await fetch_wrapper(`../../api/profile/me/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profile.value),
  })
  if (response.ok) {
    original_profile.value = JSON.parse(JSON.stringify(profile.value))
  } else {
    console.error("Failed to save profile")
  }
}

function clearAll() {
  if (window.confirm("Sei sicuro di voler annullare tutte le modifiche?")) {
    fetchProfile()
  }
}
</script>

<style scoped>
button.nav-link.active {
  background-color: #f8f9fa;
  border-bottom-color: #f8f9fa;
}
#myTabContent {
  border-left-color: #dee2e6;
  border-left-style: solid;
  border-left-width: 0.8px;
  border-bottom-left-radius: 6px;
  border-bottom-color: #dee2e6;
  border-bottom-style: solid;
  border-bottom-width: 0.8px;
  border-bottom-right-radius: 6px;
  border-right-color: #dee2e6;
  border-right-style: solid;
  border-right-width: 0.8px;
}
</style>
