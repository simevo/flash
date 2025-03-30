<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed, onActivated, onDeactivated, onMounted, onUnmounted, ref, type Ref } from "vue"
import ArticleCard from "../components/ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<FeedSerializerSimple[]> = ref([])
const count_fetch = ref(2)

async function fetchArticles() {
  const response = await fetch_wrapper(`../../api/articles/?read=true`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: PaginatedArticleReadList = await response.json()
    articles.value = data.results
    count_fetch.value -= 1
  }
}

async function fetchFeeds() {
  const response = await fetch_wrapper(`../../api/feeds/simple/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: FeedSerializerSimple[] = await response.json()
    feeds.value = data
    count_fetch.value -= 1
  }
}

const feed_dict = computed(() => {
  const feed_dict: { [key: number]: FeedSerializerSimple } = {}
  feeds.value.forEach((feed) => {
    feed_dict[feed.id] = feed
  })
  return feed_dict
})

onMounted(() => {
  console.log("ReadView mounted")
  fetchArticles()
  fetchFeeds()
})

onUnmounted(() => {
  console.log("ReadView unmounted")
})

onActivated(() => {
  console.log("ReadView activated")
})

onDeactivated(() => {
  console.log("ReadView deactivated")
})
</script>

<template>
  <div class="container-fluid" v-if="count_fetch == 0">
    <div class="row my-3" v-if="articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare.
        </div>
      </div>
    </div>
    <div class="row my-3" v-else>
      <div class="col-md-12">
        <h1 class="text-center">Cronologia degli articoli già letti da altri e/o da te</h1>
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

<style>
.wrapper {
  display: grid;
  margin: 0 auto;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-auto-rows: minmax(150px, auto);
}
</style>
