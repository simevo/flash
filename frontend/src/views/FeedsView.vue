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
            placeholder="Cerca..."
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
        <div v-if="filtered_feeds.length == 0">
          <div class="alert alert-warning text-center" role="alert">
            Non ci sono fonti da visualizzare.
          </div>
        </div>
        <FeedCard v-else v-for="feed in filtered_feeds" :key="feed.id" :feed="feed" />
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
  const search_value = search.value.toLowerCase()
  if (search_value) {
    const regex =
      /[^\p{Alphabetic}\p{Mark}\p{Decimal_Number}\p{Connector_Punctuation}\p{Join_Control} ]/gu
    const sanitized = search_value.replace(regex, "")
    const trimmed = sanitized.replace(/\s/g, "")
    return ff.filter((feed) => {
      const text = feed.title + " " + feed.url
      return text.toLowerCase().includes(trimmed)
    })
  } else {
    return ff
  }
})

function resetSearch() {
  search.value = ""
}

onMounted(() => {
  console.log("FeedsView mounted")
  fetchFeeds()
})
</script>
