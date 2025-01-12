<template>
  <div class="container-fluid" v-if="feeds.length > 0">
    <div class="row my-3">
      <div class="col-md-12">
        <ul>
          <li v-for="feed in feeds" :key="feed.id">
            <router-link
              :to="'/feed/' + feed.id"
              :title="'vai a tutti gli articoli di ' + feed.title"
              ><span>{{ feed.title }}</span>
            </router-link>
          </li>
        </ul>
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

type Feed = components["schemas"]["Feed"]

const feeds: Ref<Feed[]> = ref([])

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
