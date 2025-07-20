<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed, onActivated, onDeactivated, onMounted, onUnmounted, ref, type Ref } from "vue"
import { toast } from "vue3-toastify"

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

const not_filtering = computed(() => true)

function sorting_key(a: ArticleRead) {
  if (not_filtering.value) {
    // client-side deterministically perturbed chronological order, assuming:
    // - 200 feeds and 2000 articles/day (on average 10 articles per day and feed)
    // - average length 4000 chars
    return a.stamp / 3600 / 24 - a.feed - a.length / 20
  } else {
    return a.stamp
  }
}

function sort(articles: ArticleRead[]) {
  return articles.sort((a, b) => {
    const val_a = sorting_key(a)
    const val_b = sorting_key(b)
    return val_b - val_a
  })
}

async function fetchArticles(isLoadMore = false) {
  ready.value = false
  const url = `../../api/articles/favorites/`
  try {
    const response = await fetch_wrapper(url)
    if (response.status == 403) {
      document.location = "/accounts/"
      return
    }
    const data: PaginatedArticleReadList = await response.json()
    if (isLoadMore) {
      articles.value = articles.value.concat(sort(data.results))
    } else {
      articles.value = sort(data.results)
    }
    next.value = data.next ? data.next : ""
  } catch (error) {
    toast("Errore HTTP durante il recupero dei favoriti:" + error, { type: "error" })
    // Potentially set an error state here
  } finally {
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
      articles.value = articles.value.concat(sort(data.results))
      next.value = data.next ? data.next : ""
      fetching.value = false
    }
  }
}

onMounted(async () => {
  console.log("ListFavs mounted")
  fetchArticles()
})

onUnmounted(() => {
  console.log("ListFavs unmounted")
})

onActivated(() => {
  console.log("ListFavs activated")
})

onDeactivated(() => {
  console.log("ListFavs deactivated")
})
</script>

<template>
  <p>
    Gli articoli provenienti dalle tue fonti preferite. Personalizza questo newsfeed scegliendo le
    fonti preferite
    <img
      class="icon"
      src="~bootstrap-icons/icons/heart-fill.svg"
      alt="filled heart icon"
      width="18"
      height="18"
    />
    nella <RouterLink to="/feeds">pagina "Fonti"</RouterLink>.
  </p>
  <div v-if="ready && Object.keys(feed_dict).length > 0">
    <div class="row my-3" v-if="articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non hai ancora definito le tue fonti preferite.
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
        <p class="mb-3">Recupero gli articoli ...</p>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>
