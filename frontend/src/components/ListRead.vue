<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { onActivated, onDeactivated, onMounted, onUnmounted, ref, type Ref } from "vue"

import ArticleCard from "./ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

const ready = ref(false)
const fetching = ref<boolean>(false)
const articles: Ref<ArticleRead[]> = ref([])
const next = ref<string>("")

defineProps<{
  feeds: FeedSerializerSimple[]
  feed_dict: { [key: number]: FeedSerializerSimple }
}>()

async function fetchArticles() {
  ready.value = false
  const response = await fetch_wrapper(`../../api/articles/?read=true`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: PaginatedArticleReadList = await response.json()
    articles.value = data.results
    next.value = data.next ? data.next : ""
    ready.value = true
  }
}

async function fetchMoreArticles() {
  if (next.value) {
    fetching.value = true
    const response = await fetch_wrapper(next.value)
    if (response.status == 403) {
      document.location = "/accounts/"
    } else {
      const data: PaginatedArticleReadList = await response.json()
      articles.value = articles.value.concat(data.results)
      next.value = data.next ? data.next : ""
      fetching.value = false
    }
  }
}

onMounted(async () => {
  console.log("ListRead mounted")
  fetchArticles()
})

onUnmounted(() => {
  console.log("ListRead unmounted")
})

onActivated(() => {
  console.log("ListRead activated")
})

onDeactivated(() => {
  console.log("ListRead deactivated")
})
</script>

<template>
  <div v-if="ready">
    <p>Gli articoli più recenti già letti da altri e/o da te</p>
    <div class="row my-3" v-if="articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare qui.
        </div>
      </div>
    </div>
    <div class="row my-3" v-else>
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
            :feed_dict="feed_dict"
            :index="1"
            :list_id="null"
          />
        </div>
      </div>
    </div>
    <div class="row my-3">
      <div class="col-md-12 text-center mt-3">
        <div class="spinner-border text-primary" role="status" v-if="fetching">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div class="col-md-12 text-center" v-if="articles.length > 0">
        <button
          class="btn btn-primary"
          @click="fetchMoreArticles"
          :disabled="fetching"
          v-if="next != ''"
        >
          Carica altri articoli
        </button>
        <p v-else>Fine.</p>
      </div>
    </div>
  </div>
  <div class="container my-3" v-else>
    <div class="row">
      <div class="text-center col-md-8 offset-md-2">
        <p class="mb-3">Recupero la lista di tutti gli articoli letti ...</p>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>
