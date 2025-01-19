<template>
  <div class="container-fluid my-3" v-if="count_fetch == 0">
    <div class="row">
      <h1>Fonte: {{ feed_dict[Number(id)].title }}</h1>
      <div>
        <span class="float-start">
          <a :href="feed_dict[Number(id)].url" target="_blank">{{
            feed_dict[Number(id)].url
          }}</a>
        </span>
        <span class="float-end">
          {{ feed_dict[Number(id)].tags }}
        </span>
      </div>
    </div>
    <hr />
    <div class="row">
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
            :feed_dict="feed_dict"
            :index="1"
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
import { computed, watch } from "vue"
import { useRoute } from "vue-router"
import { ref, onMounted, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"
import ArticleCard from "../components/ArticleCard.vue"

type ArticleRead = components["schemas"]["ArticleRead"]
type Feed = components["schemas"]["Feed"]
type PaginatedArticleReadList =
  components["schemas"]["PaginatedArticleReadList"]

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<Feed[]> = ref([])
const count_fetch = ref(2)

const route = useRoute()

export interface Props {
  id: string
}

const props = withDefaults(defineProps<Props>(), {
  id: "",
})

watch(
  () => route.params.id,
  async (newId) => {
    alert(newId)
  },
)

async function fetchArticles() {
  const response = await fetch_wrapper(
    `../../api/articles/?feed_id=${props.id}`,
  )
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
    const data: Feed[] = await response.json()
    feeds.value = data
    count_fetch.value -= 1
  }
}

const feed_dict = computed(() => {
  const feed_dict: { [key: number]: Feed } = {}
  feeds.value.forEach((feed) => {
    feed_dict[feed.id] = feed
  })
  return feed_dict
})

onMounted(() => {
  console.log("FeedView mounted")
  fetchArticles()
  fetchFeeds()
})
</script>
