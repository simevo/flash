<template>
  <div class="container" v-if="feeds.length > 0">
    <div class="row my-3">
      <div class="col-md-12">
        <h1>
          Fonti
          <RouterLink
            class="btn btn-success float-end"
            title="Crea una nuova fonte (funzione riservata agli utenti di staff)"
            role="button"
            type="button"
            to="../new_feed/"
            v-if="auth.user?.is_staff"
          >
            <img
              class="icon"
              src="~bootstrap-icons/icons/plus.svg"
              alt="pencil icon"
              width="18"
              height="18"
            />
            Nuova fonte
          </RouterLink>
          <button
            @click="clean()"
            type="button"
            class="btn btn-danger float-end me-2"
            aria-label="Pulisci tutti i campi"
            title="Pulisci tutti i campi"
            :disabled="not_filtering"
          >
            Azzera filtri
          </button>
        </h1>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <label for="language" class="col-2">Lingua</label>
          <select
            v-model="language"
            class="form-select"
            aria-label="Filtra per lingua"
            title="Filtra per lingua"
            id="language"
            name="language"
          >
            <option value="all" selected>Tutte le lingue</option>
            <option v-for="code in Object.keys(languages)" :key="code" :value="code">
              {{ languages[code] }}
            </option>
          </select>
        </div>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <label for="text" class="col-2">Ricerca</label>
          <input
            type="text"
            class="form-control"
            v-model="search"
            placeholder="Cerca per parola..."
            aria-label="Cerca"
            title="Cerca"
            id="text"
            name="text"
          />
          <button
            type="button"
            class="btn-close position-absolute"
            style="right: 0.5em; top: 0.5em"
            aria-label="Cancella"
            :disabled="search == ''"
            @click="resetSearch()"
          ></button>
        </div>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <label class="col-2">Tags</label>
          <span
            v-for="[tag, value] of Object.entries(tags)"
            :key="tag"
            class="badge text-bg-secondary m-1 p-2"
          >
            <input
              type="checkbox"
              :checked="value"
              @input="(event) => (tags[<tag_keys>tag] = !value)"
            />
            {{ tag }}
          </span>
          <button
            type="button"
            class="btn-close float-end me-1 ms-auto"
            aria-label="ripristina"
            title="ripistina selezione dei tag"
            @click="resetTags()"
          ></button>
        </div>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <label for="ordinamento" class="col-2">Ordinamento</label>
          <select
            v-model="sort_by"
            class="form-select"
            aria-label="Ordinamento"
            title="Ordinamento"
            id="ordinamento"
            name="ordinamento"
          >
            <option value="id" selected>Creazione</option>
            <option value="url">Link</option>
            <option value="title">Nome</option>
            <option value="last_polled_epoch">Ultimo aggiornamento</option>
            <option value="article_count">Numero articoli</option>
            <option value="average_time_from_last_post">Frequenza di pubblicazione</option>
            <option value="active">Attivo</option>
            <option value="my_rating">Voto</option>
          </select>
          <img
            v-if="sort_ascending"
            class="icon ms-2"
            src="~bootstrap-icons/icons/sort-up.svg"
            alt="ascending sort icon"
            title="Ordinamento a salire"
            width="30"
            height="30"
            @click="toggle_sort()"
          />
          <img
            v-else
            class="icon ms-2"
            src="~bootstrap-icons/icons/sort-down-alt.svg"
            alt="descending sort icon"
            title="Ordinamento a scendere"
            width="30"
            height="30"
            @click="toggle_sort()"
          />
        </div>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <input
            id="hidden"
            name="hidden"
            type="checkbox"
            class="form-checkbox col-1"
            v-model="hidden"
          />
          <label for="hidden" class="col-5">Nascoste</label>
          <input
            id="hidden"
            name="hidden"
            type="checkbox"
            class="form-checkbox col-1"
            v-model="preferred"
          />
          <label for="preferred" class="col-2">Preferite</label>
        </div>

        <hr />
        <div v-if="filtered_feeds.length == 0">
          <div class="alert alert-warning text-center" role="alert">
            Non ci sono fonti da visualizzare.
          </div>
        </div>
        <FeedCard
          v-else
          v-for="feed in sorted_feeds"
          :key="feed.id"
          :feed="feed"
          :clickable="true"
          @refresh_feed="refresh_feed"
        />
      </div>
    </div>
  </div>
  <div class="container my-3" v-else>
    <div class="row">
      <div class="text-center col-md-8 offset-md-2">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { ref, onMounted, type Ref, computed } from "vue"

import { useAuthStore } from "../stores/auth.store"
const auth = useAuthStore()

import type { components } from "../generated/schema.d.ts"
import FeedCard from "../components/FeedCard.vue"

type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number | undefined }
type UserFeed = components["schemas"]["UserFeed"]

const feeds: Ref<PatchedFeed[]> = ref([])
const language = ref("all")
const search = ref("")

type tag_keys =
  | "cultura"
  | "società"
  | "italia"
  | "estero"
  | "scienza_tecnica"
  | "sport"
  | "economia"
  | "blog"
  | "notiziario"
  | "rivista"

const tags = ref({
  cultura: true,
  società: true,
  italia: true,
  estero: true,
  scienza_tecnica: true,
  sport: true,
  economia: true,
  blog: true,
  notiziario: true,
  rivista: true,
})

function resetTags() {
  Object.keys(tags.value).forEach((tag) => {
    tags.value[<tag_keys>tag] = true
  })
}

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

const hidden = ref(false)
const preferred = ref(false)

async function fetchFeeds() {
  const response = await fetch_wrapper(`../../api/feeds/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const response2 = await fetch_wrapper(`../../api/user-feeds/`)
    const ufs: UserFeed[] = await response2.json()
    const ufd: { [key: number]: number | undefined } = {}
    ufs.forEach((element) => {
      ufd[element.feed_id] = element.rating
    })
    const data: Feed[] = await response.json()
    feeds.value = data.map((value) => <PatchedFeed>{ ...value, my_rating: ufd[value.id] })
  }
}

const filtered_feeds = computed(() => {
  const ff =
    language.value === "all"
      ? feeds.value
      : feeds.value.filter((feed) => {
          return feed.language === language.value
        })
  const fff = ff
    .filter((feed) => {
      if (feed.tags) {
        return !feed.tags.some((tag) => {
          if (!tags.value[<tag_keys>tag]) {
            return true
          }
        })
      } else {
        return true
      }
    })
    .filter((feed) => {
      if (preferred.value && feed.my_rating == 5) return true
      if (hidden.value && feed.my_rating == -5) return true
      if (preferred.value || hidden.value) return false
      return true
    })
  const search_value = search.value.toLowerCase()
  if (search_value) {
    const regex =
      /[^\p{Alphabetic}\p{Mark}\p{Decimal_Number}\p{Connector_Punctuation}\p{Join_Control} ]/gu
    const sanitized = search_value.replace(regex, "")
    const trimmed = sanitized.replace(/\s/g, "")
    return fff.filter((feed) => {
      const text = feed.title + " " + feed.url + " " + feed.license
      return text.toLowerCase().includes(trimmed)
    })
  } else {
    return fff
  }
})

type Sortable =
  | "active"
  | "id"
  | "article_count"
  | "average_time_from_last_post"
  | "last_polled_epoch"
  | "title"
  | "url"
  | "my_rating"

const sort_by: Ref<Sortable> = ref("id")
const sort_ascending = ref(true)

function toggle_sort() {
  sort_ascending.value = !sort_ascending.value
}

const sorted_feeds = computed(() => {
  return [...filtered_feeds.value].sort((a: PatchedFeed, b: PatchedFeed) => {
    if (
      [
        "id",
        "last_polled_epoch",
        "article_count",
        "average_time_from_last_post",
        "my_rating",
      ].indexOf(sort_by.value) != -1
    ) {
      const av = <number>(a[sort_by.value] || 0)
      const bv = <number>(b[sort_by.value] || 0)
      return (sort_ascending.value ? 1 : -1) * (av - bv)
    } else if (sort_by.value === "active") {
      const av = <boolean>a[sort_by.value]
      const bv = <boolean>b[sort_by.value]
      return (sort_ascending.value ? 1 : -1) * (av === bv ? 0 : av ? -1 : 1)
    } else {
      const av = <string>a[sort_by.value]
      const bv = <string>b[sort_by.value]
      return (sort_ascending.value ? 1 : -1) * av.localeCompare(bv)
    }
  })
})

function resetSearch() {
  search.value = ""
}

onMounted(() => {
  console.log("FeedsView mounted")
  fetchFeeds()
})

async function refresh_feed(feed_id: number) {
  feeds.value = []
  const response = await fetch_wrapper(`../../api/feeds/${feed_id}/refresh/`, {
    method: "POST",
  })
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data = await response.json()
    alert(`Fonte aggiornata: ${JSON.stringify(data)}`)
    fetchFeeds()
  }
}

function clean() {
  language.value = "all"
  Object.keys(tags.value).forEach((x) => (tags.value[<tag_keys>x] = true))
  sort_by.value = "id"
  search.value = ""
}

const not_filtering = computed(
  () =>
    language.value == "all" &&
    Object.values(tags.value).every((x) => x === true) &&
    sort_by.value == "id" &&
    search.value == "",
)
</script>
