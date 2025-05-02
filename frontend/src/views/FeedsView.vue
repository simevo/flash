<template>
  <div class="container" v-if="feeds.length > 0">
    <div class="row my-3">
      <div class="col-md-12">
        <h1>Fonti</h1>
        <select
          v-model="language"
          class="form-select mb-3"
          aria-label="Filtra per lingua"
          title="Filtra per lingua"
        >
          <option value="all" selected>Tutte le lingue</option>
          <option v-for="code in Object.keys(languages)" :key="code" :value="code">
            {{ languages[code] }}
          </option>
        </select>
        <div class="input-group position-relative d-inline-flex align-items-center">
          <input
            type="text"
            class="form-control mb-3"
            v-model="search"
            placeholder="Cerca per parola..."
            aria-label="Cerca"
            title="Cerca"
          />
          <button
            type="button"
            class="btn-close position-absolute"
            style="right: 0.5em; top: 0.5em"
            data-bs-dismiss="alert"
            aria-label="Cancella"
            :disabled="search == ''"
            @click="resetSearch()"
          ></button>
        </div>
        <div class="mb-3">
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
            class="btn-close"
            style="float: right; margin-right: 8px"
            aria-label="ripristina"
            title="ripistina selezione dei tag"
            @click="resetTags()"
          ></button>
        </div>
        <div class="input-group position-relative d-inline-flex align-items-center mb-3">
          <select
            v-model="sort_by"
            class="form-select"
            aria-label="Ordinamento"
            title="Ordinamento"
          >
            <option value="id" selected>Creazione</option>
            <option value="url">Link</option>
            <option value="title">Nome</option>
            <option value="last_polled_epoch">Ultimo aggiornamento</option>
            <option value="article_count">Numero articoli</option>
            <option value="average_time_from_last_post">Frequenza di pubblicazione</option>
            <option value="active">Attivo</option>
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
import type { components } from "../generated/schema.d.ts"

import FeedCard from "../components/FeedCard.vue"

type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number }
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
  const fff = ff.filter((feed) => {
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
  const search_value = search.value.toLowerCase()
  if (search_value) {
    const regex =
      /[^\p{Alphabetic}\p{Mark}\p{Decimal_Number}\p{Connector_Punctuation}\p{Join_Control} ]/gu
    const sanitized = search_value.replace(regex, "")
    const trimmed = sanitized.replace(/\s/g, "")
    return fff.filter((feed) => {
      const text = feed.title + " " + feed.url
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

const sort_by: Ref<Sortable> = ref("id")
const sort_ascending = ref(true)

function toggle_sort() {
  sort_ascending.value = !sort_ascending.value
}

const sorted_feeds = computed(() => {
  return [...filtered_feeds.value].sort((a: PatchedFeed, b: PatchedFeed) => {
    if (
      ["id", "last_polled_epoch", "article_count", "average_time_from_last_post"].indexOf(
        sort_by.value,
      ) != -1
    ) {
      const av = <number>a[sort_by.value]
      const bv = <number>b[sort_by.value]
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
</script>
