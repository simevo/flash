<template>
  <div class="container-fluid" v-if="articles.length > 0">
    <div class="row my-3">
      <h1>Feed: {{ id }}</h1>
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
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
import { watch } from "vue"
import { useRoute } from "vue-router"
import { ref, onMounted, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"
import ArticleCard from "../components/ArticleCard.vue"

type Article = components["schemas"]["Article"]
type PaginatedArticleList = components["schemas"]["PaginatedArticleList"]

const articles: Ref<Article[]> = ref([])

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
    const data: PaginatedArticleList = await response.json()
    articles.value = data.results
  }
}

onMounted(() => {
  console.log("HomePage mounted")
  fetchArticles()
})
</script>
