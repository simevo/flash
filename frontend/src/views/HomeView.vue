<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import {
  computed,
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  type Ref,
} from "vue"
import type { Filters, FeedCounts } from "../types/Filters"
import ArticleCard from "../components/ArticleCard.vue"
import FormFilter from "../components/FormFilter.vue"

import type { components } from "../generated/schema.d.ts"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type PaginatedArticleReadList =
  components["schemas"]["PaginatedArticleReadList"]

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<FeedSerializerSimple[]> = ref([])
const count_fetch = ref(2)

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
  if (articles.value.length === 0 || feeds.value.length === 0) {
    return feed_counts
  }
  for (const article of articles.value) {
    if (article.feed in feed_counts) {
      feed_counts[article.feed].count += 1
    } else {
      feed_counts[article.feed] = {
        feed: feed_dict.value[article.feed].title,
        icon: feed_dict.value[article.feed].icon,
        count: 1,
        feed_id: article.feed,
      }
    }
  }
  return feed_counts
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
    return articles.value
  } else {
    return articles.value.filter((article) => {
      let found = true
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
          found && filters.feed_ids.some((value) => article.feed === value)
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
  console.log("HomeView mounted")
  fetchArticles()
  fetchFeeds()
})

onUnmounted(() => {
  console.log("HomeView unmounted")
})

onActivated(() => {
  console.log("HomeView activated")
})

onDeactivated(() => {
  console.log("HomeView deactivated")
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
  <div class="container-fluid" v-if="count_fetch == 0">
    <div class="row my-3" v-if="filtered_articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare.
        </div>
      </div>
    </div>
    <div class="row my-3" v-else>
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in filtered_articles"
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
        :feeds="feeds"
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
