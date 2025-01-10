<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed, onMounted, ref, type Ref } from "vue"
import type { Filters, FeedCounts } from "../types/Filters"
import ArticleCard from "../components/ArticleCard.vue"
import FormFilter from "../components/FormFilter.vue"

import type { components } from "../generated/schema.d.ts"

type Article = components["schemas"]["Article"]
type PaginatedArticleList = components["schemas"]["PaginatedArticleList"]

const articles: Ref<Article[]> = ref([])

const no_filters: Filters = {
  what: "",
  when: "all",
  language: "all",
  length: "all",
  feed_ids: [-1],
}

import { useFiltersStore } from "../stores/filters.store"

const filters = useFiltersStore().filters
const filterActions = useFiltersStore()

const feed_counts = computed(() => {
  const feed_counts: FeedCounts = {}
  for (const article of articles.value) {
    if (article.feed.id in feed_counts) {
      feed_counts[article.feed.id].count += 1
    } else {
      feed_counts[article.feed.id] = {
        feed: article.feed.title,
        icon: article.feed.icon,
        count: 1,
        feed_id: article.feed.id,
      }
    }
  }
  const feeds = Object.values(feed_counts).sort((a, b) => b.count - a.count)
  return feeds
})

const not_filtering = computed(
  () =>
    filters.what === no_filters.what &&
    filters.when === no_filters.when &&
    filters.language === no_filters.language &&
    filters.length === no_filters.length &&
    filters.feed_ids.length === no_filters.feed_ids.length &&
    filters.feed_ids.every(
      (value, index) => value === no_filters.feed_ids[index],
    ),
)

const filtered_articles = computed(() => {
  if (not_filtering.value) {
    return articles
  } else {
    return articles.value.filter((article) => {
      let found = true
      return found
      if (filters.what) {
        const text =
          article.excerpt +
          (article.title ? article.title : " ") +
          (article.title_original ? article.title_original : " ") +
          article.author
        found = found && text.toLowerCase().includes(filters.what.toLowerCase())
      }
      if (filters.when !== "all") {
        const [max, min] = filters.when.split("-")
        const age = (new Date().getTime() / 1000 - article.stamp) / 3600
        found = found && age > parseInt(min) && age <= parseInt(max)
      }
      if (filters.language !== "all") {
        found = found && article.language === filters.language
      }
      if (filters.length !== "all") {
        const [min, max] = filters.length.split("-")
        found =
          found &&
          article.length > parseInt(min) &&
          article.length <= parseInt(max)
      }
      if (filters.feed_ids.indexOf(-1) === -1) {
        found =
          found && filters.feed_ids.some((value) => article.feed.id === value)
      }
      return found
    })
  }
})

async function fetchArticles() {
  const response = await fetch_wrapper(`../../api/articles/`)
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

<template>
  <button
    class="btn btn-primary ms-2"
    :class="{ active: !not_filtering }"
    title="Filtra gli articoli"
    data-bs-toggle="offcanvas"
    data-bs-target="#offcanvasFilters"
    type="button"
    style="position: absolute; z-index: 1000"
  >
    <img
      v-if="not_filtering"
      class="icon"
      src="~bootstrap-icons/icons/funnel.svg"
      alt="view icon"
      width="18"
      height="18"
    />
    <img
      v-else
      class="icon"
      src="~bootstrap-icons/icons/funnel-fill.svg"
      alt="view icon"
      width="18"
      height="18"
    />
  </button>
  <div class="container-fluid" v-if="articles.length > 0">
    <div class="row my-3">
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in filtered_articles"
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
  <div
    id="offcanvasFilters"
    class="offcanvas offcanvas-start"
    tabindex="-1"
    aria-labelledby="offcanvasFiltersLabel"
  >
    <div class="offcanvas-header">
      <h5 id="offcanvasFiltersLabel" class="offcanvas-title">
        Filtra gli articoli
      </h5>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="offcanvas"
        aria-label="Close"
      ></button>
    </div>
    <div class="offcanvas-body">
      <FormFilter
        :articles="articles"
        :filters="filters"
        :feed-counts="feed_counts"
        :not-filtering="not_filtering"
        @clear="filterActions.clear"
        @toggle_all_feeds="filterActions.toggle_all_feeds"
        @toggle_feed="filterActions.toggle_feed"
        @update_what="(value) => (filters.what = value)"
        @update_language="(value) => (filters.language = value)"
        @update_when="(value) => (filters.when = value)"
        @update_length="(value) => (filters.length = value)"
      />
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
