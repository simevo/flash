<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import {
  computed,
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  watch,
  type Ref,
} from "vue"
import type { Filters, FeedCounts } from "../types/Filters"
import ArticleCard from "../components/ArticleCard.vue"
import FormFilter from "../components/FormFilter.vue"

import type { components } from "../generated/schema.d.ts"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<FeedSerializerSimple[]> = ref([])
const count_fetch = ref(2)
const next = ref<string>("")
const fetching = ref<boolean>(false)

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
    filters.feed_ids.every((value, index) => value === no_filters.feed_ids[index]),
)

const filters_summary = computed(() => {
  if (not_filtering.value) {
    return "Filtra gli articoli"
  } else {
    let summary = "Articoli filtrati"
    if (filters.what.trim()) {
      summary += ` - per parole chiave [${filters.what.trim()}]`
    }
    if (filters.when !== "all") {
      summary += ` - per data: [${filters.when}]`
    }
    if (filters.language !== "all") {
      summary += ` - per lingua: [${filters.language}]`
    }
    if (filters.length !== "all") {
      summary += ` - per lunghezza: [${filters.length}]`
    }
    if (filters.feed_ids.length > 0 && filters.feed_ids.indexOf(-1) === -1) {
      summary += ` - per fonti: [${filters.feed_ids}]`
    }
    return summary
  }
})

const filtered_articles = computed(() => {
  if (not_filtering.value) {
    return articles.value
  } else {
    return articles.value.filter((article) => {
      let found = true
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
        found = found && article.length > parseInt(min) && article.length <= parseInt(max)
      }
      if (filters.feed_ids.indexOf(-1) === -1) {
        found = found && filters.feed_ids.some((value) => article.feed === value)
      }
      return found
    })
  }
})

async function fetchArticles() {
  let url = `../../api/articles/`
  if (filters.what.trim()) {
    // sanitize the what parameter, allowing only alphanumeric characters, using Unicode character class escapes
    const regex =
      /[^\p{Alphabetic}\p{Mark}\p{Decimal_Number}\p{Connector_Punctuation}\p{Join_Control} ]/gu
    const sanitizedWhat = filters.what.replace(regex, "")
    // remove multiple consecutive spaces and any leading / trailing spaces
    const trimmed = sanitizedWhat.replace(/\s+/g, " ").trim()
    const words = trimmed.split(" ")
    if (words.length > 0) {
      const query = words.join("&")
      const encodedQuery = encodeURIComponent(query)
      url += `?query=${encodedQuery}`
    }
  }
  const response = await fetch_wrapper(url)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: PaginatedArticleReadList = await response.json()
    articles.value = data.results
    next.value = data.next ? data.next : ""
    count_fetch.value -= 1
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

watch(
  () => filters.what,
  async (newWhat, oldWhat) => {
    console.log(`HomeView what watch, newWhat = [${newWhat}] oldWhat = [${oldWhat}]`)
    if (newWhat !== oldWhat) {
      articles.value = []
      count_fetch.value = 1
      await fetchArticles()
    }
  },
)
</script>

<template>
  <button
    class="btn btn-primary ms-2 btn-lg"
    :class="{ active: !not_filtering }"
    :title="filters_summary"
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
    <div class="row my-3">
      <div class="col-md-12 text-center mt-3">
        <div class="spinner-border text-primary" role="status" v-if="fetching">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div class="col-md-12 text-center" v-if="filtered_articles.length > 0">
        <button
          class="btn btn-primary"
          @click="fetchMoreArticles"
          :disabled="fetching"
          v-if="next != ''"
        >
          Carica altri articoli
        </button>
        <p v-else>Non ci sono altri articoli da visualizzare.</p>
      </div>
    </div>
  </div>
  <div class="container my-3" v-else>
    <div class="row">
      <div class="text-center col-md-8 offset-md-2">
        <h1 class="mb-3" v-if="!not_filtering">{{ filters_summary }}...</h1>
        <h1 class="mb-3" v-else>Tutti gli articoli in ordine cronologico ...</h1>
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
      <h5 id="offcanvasFiltersLabel" class="offcanvas-title">Filtra gli articoli</h5>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="offcanvas"
        aria-label="Chiudi"
        title="Chiudi"
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
