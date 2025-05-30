<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { onActivated, onDeactivated, onMounted, onUnmounted, ref, type Ref } from "vue"

import ArticleCard from "./ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type UserArticleListsSerializerFull = components["schemas"]["UserArticleListsSerializerFull"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

const ready = ref(false)
const articles: Ref<ArticleRead[]> = ref([])
const allLists: Ref<UserArticleListsSerializerFull[]> = ref([])

defineProps<{
  feeds: FeedSerializerSimple[]
  feed_dict: { [key: number]: FeedSerializerSimple }
}>()

async function fetchArticles() {
  ready.value = false
  const listsResponse = await fetch_wrapper(`../../api/lists/me/`)
  if (listsResponse.status == 403) {
    document.location = "/accounts/"
    return
  }
  const listsData: UserArticleListsSerializerFull[] = await listsResponse.json()
  allLists.value = listsData
  const newsfeedList = allLists.value.find((list) => list.name === "newsfeed")

  if (newsfeedList && newsfeedList.articles.length > 0) {
    const articlesResponse = await fetch_wrapper(
      `../../api/articles/?ids=${newsfeedList.articles.join(",")}`,
    )
    if (articlesResponse.status == 403) {
      document.location = "/accounts/"
    } else {
      const articlesData: PaginatedArticleReadList = await articlesResponse.json()
      articles.value = articlesData.results
    }
  } else {
    articles.value = [] // Clear if no newsfeed or it's empty
  }
  ready.value = true
}

onMounted(async () => {
  console.log("ListForyou mounted")
  fetchArticles()
})

onUnmounted(() => {
  console.log("ListForyou unmounted")
})

onActivated(() => {
  console.log("ListForyou activated")
})

onDeactivated(() => {
  console.log("ListForyou deactivated")
})
</script>

<template>
  <div v-if="ready">
    <p>
      Gli articoli scelti per te. Personalizza questo newsfeed scegliendo le parole (prioritarie o
      vietate) e le lingue preferite nella
      <RouterLink to="/settings">pagina "Impostazioni"</RouterLink>.
    </p>
    <div class="row my-3" v-if="articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli per te da visualizzare.
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
  </div>
  <div class="container my-3" v-else>
    <div class="row">
      <div class="text-center col-md-8 offset-md-2">
        <p class="mb-3">Recupero la lista degli articoli scelti per te ...</p>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>
