<template>
  <div class="container" v-if="feeds.length > 0">
    <div class="row my-3">
      <div class="col-md-12">
        <h1>Fonti</h1>
        <select
          :value="language"
          class="form-select mb-3"
          aria-label="Filtra per lingua"
        >
          <option value="" selected>Tutte le lingue</option>
          <option value="it">Italiano</option>
          <option value="en">Inglese</option>
        </select>
        <FeedCard v-for="feed in feeds" :key="feed.id" :feed="feed" />
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
import { ref, onMounted, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"

import FeedCard from "../components/FeedCard.vue"

type Feed = components["schemas"]["Feed"]

const feeds: Ref<Feed[]> = ref([])
const language = ref("")

async function fetchFeeds() {
  const response = await fetch_wrapper(`../../api/feeds/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Feed[] = await response.json()
    feeds.value = data
  }
}

onMounted(() => {
  console.log("HomePage mounted")
  fetchFeeds()
})
</script>
