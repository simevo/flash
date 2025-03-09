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
          <option
            v-for="code in Object.keys(languages)"
            :key="code"
            :value="code"
          >
            {{ languages[code] }}
          </option>
        </select>
        <div v-if="filtered_feeds.length == 0">
          <div class="alert alert-warning text-center" role="alert">
            Non ci sono fonti da visualizzare.
          </div>
        </div>
        <FeedCard
          v-else
          v-for="feed in filtered_feeds"
          :key="feed.id"
          :feed="feed"
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

const feeds: Ref<Feed[]> = ref([])
const language = ref("all")

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
    const data: Feed[] = await response.json()
    feeds.value = data
  }
}

const filtered_feeds = computed(() => {
  if (language.value === "all") {
    return feeds.value
  } else {
    return feeds.value.filter((feed) => {
      return feed.language === language.value
    })
  }
})

onMounted(() => {
  console.log("FeedsView mounted")
  fetchFeeds()
})
</script>
