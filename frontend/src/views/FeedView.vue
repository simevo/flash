<template>
  <div class="container-fluid my-3" v-if="count_fetch == 0">
    <FeedCard v-if="feed" :feed="feed" />
    <hr />
    <div class="row" v-if="articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare.
        </div>
      </div>
    </div>
    <div class="row" v-else>
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
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { onActivated, watch } from "vue"
import { useRoute } from "vue-router"
import { ref, onMounted, type Ref } from "vue"

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type Feed = components["schemas"]["Feed"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type PatchedFeed = Feed & { my_rating: number }
type UserFeed = components["schemas"]["UserFeed"]

import ArticleCard from "../components/ArticleCard.vue"
import FeedCard from "../components/FeedCard.vue"

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<Feed[]> = ref([])
const feed_dict: Ref<{ [key: number]: Feed }> = ref({})
const feed: Ref<PatchedFeed | null> = ref(null)
const count_fetch = ref(2)

const route = useRoute()

export interface Props {
  feed_id: string
}

const props = withDefaults(defineProps<Props>(), {
  feed_id: "",
})

async function fetchArticles() {
  const response = await fetch_wrapper(`../../api/articles/?feed_id=${props.feed_id}`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: PaginatedArticleReadList = await response.json()
    articles.value = data.results
    count_fetch.value -= 1
  }
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
    feeds.value = data
    feeds.value.forEach((feed) => {
      feed_dict.value[feed.id] = feed
    })
    feed.value = <PatchedFeed>{
      ...feed_dict.value[Number(props.feed_id)],
      my_rating: ufd[Number(props.feed_id)],
    }
    count_fetch.value -= 1
  }
}

onMounted(() => {
  console.log("FeedView mounted")
  fetchArticles()
  fetchFeeds()
})

onActivated(() => {
  console.log("FeedView activated")
})

watch(
  () => route.params.feed_id,
  async (newId, oldId) => {
    console.log(`FeedView watch id, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId != oldId) {
      count_fetch.value += 1
      await fetchArticles()
    }
  },
)
</script>
