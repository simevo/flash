<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed, onActivated, onDeactivated, onMounted, onUnmounted, ref, type Ref } from "vue"

import ArticleCard from "./ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type UserFeed = components["schemas"]["UserFeed"]

import type { Filters, FeedCounts, Ufd } from "../types/Filters"
import FormFilter from "./FormFilter.vue"

const ready = ref(false)
const fetching = ref<boolean>(false)
const articles: Ref<ArticleRead[]> = ref([])
const ufd: Ref<Ufd> = ref({})
const next = ref<string>("")

const props = defineProps<{
  feeds: FeedSerializerSimple[]
  feed_dict: { [key: number]: FeedSerializerSimple }
}>()

const no_filters: Filters = {
  what: "",
  when: "all",
  language: "all",
  length: "all",
}

import { useFiltersStore } from "../stores/filters.store"

const filters = useFiltersStore().filters
const filterActions = useFiltersStore()

const feed_counts = computed(() => {
  const feed_counts: FeedCounts = {}
  if (articles.value.length === 0 || props.feeds.length === 0) {
    return feed_counts
  }
  for (const article of articles.value) {
    if (article.feed in feed_counts) {
      feed_counts[article.feed].count += 1
    } else {
      feed_counts[article.feed] = {
        feed: props.feed_dict[article.feed].title,
        image: props.feed_dict[article.feed].image,
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
    filters.length === no_filters.length,
)

const filters_summary = computed(() => {
  if (not_filtering.value) {
    return "Filtra gli articoli"
  } else {
    let summary = " Filtro articoli attivo"
    if (filters.what.trim()) {
      summary += ` - per parole chiave [${filters.what.trim()}]`
    }
    if (filters.when !== "all") {
      summary += ` - per data: [${filters.when}] giorni`
    }
    if (filters.language !== "all") {
      summary += ` - per lingua: [${filters.language}]`
    }
    if (filters.length !== "all") {
      summary += ` - per lunghezza: [${filters.length}]`
    }
    return summary
  }
})

const filtered_articles = computed(() => {
  const articles_without_hidden_feeds = articles.value.filter((article) => {
    return !(article.feed in ufd.value && ufd.value[article.feed] == -5)
  })
  if (not_filtering.value) {
    return articles_without_hidden_feeds
  } else {
    return articles_without_hidden_feeds.filter((article) => {
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
      return found
    })
  }
})

// client-side deterministically perturbed chronological order, assuming:
// - 200 feeds and 2000 articles/day (on average 10 articles per day and feed)
// - average length 4000 chars
function sorting_key(a: ArticleRead) {
  return a.stamp / 3600 / 24 - a.feed - a.length / 20
}

function sort(articles: ArticleRead[]) {
  return articles.sort((a, b) => {
    const val_a = sorting_key(a)
    const val_b = sorting_key(b)
    return val_a - val_b
  })
}

async function fetchArticles() {
  ready.value = false
  let url = `../../api/articles/`
  if (filters.what.trim()) {
    const regex =
      /[^\p{Alphabetic}\p{Mark}\p{Decimal_Number}\p{Connector_Punctuation}\p{Join_Control} ]/gu
    const sanitizedWhat = filters.what.replace(regex, "")
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
    articles.value = sort(data.results)
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
      articles.value = articles.value.concat(sort(data.results))
      next.value = data.next ? data.next : ""
      fetching.value = false
    }
  }
}

async function fetchMyFeeds() {
  const response = await fetch_wrapper(`../../api/user-feeds/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const ufs: UserFeed[] = await response.json()
    ufs.forEach((element) => {
      ufd.value[element.feed_id] = element.rating
    })
  }
}

onMounted(async () => {
  console.log("ListAll mounted")
  await fetchMyFeeds()
  await fetchArticles()
})

onUnmounted(() => {
  console.log("ListAll unmounted")
})

onActivated(() => {
  console.log("ListAll activated")
})

onDeactivated(() => {
  console.log("ListAll deactivated")
})
</script>

<template>
  <button
    class="btn btn-primary ms-2 btn-lg"
    :class="{ active: !not_filtering }"
    :title="filters_summary"
    data-bs-toggle="offcanvas"
    data-bs-target="#offcanvasFilters"
    type="button"
    style="position: absolute; top: 5rem; right: 0.5em; z-index: 1030"
  >
    <img
      v-if="not_filtering"
      class="icon"
      src="~bootstrap-icons/icons/funnel.svg"
      alt="funnel icon"
      width="18"
      height="18"
    />
    <img
      v-else
      class="icon"
      src="~bootstrap-icons/icons/funnel-fill.svg"
      alt="filled funnel icon"
      width="18"
      height="18"
    />
  </button>
  <div v-if="ready">
    <p>
      Gli articoli più recenti.<span v-if="!not_filtering">{{ filters_summary }}</span>
    </p>
    <div class="row my-3" v-if="filtered_articles.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare qui.
          <span v-if="!not_filtering"
            >Forse i tuoi criteri di ricerca sono troppo restrittivi? Controlla il
            <b>bottone filtro articoli</b>
            <img
              class="icon"
              src="~bootstrap-icons/icons/funnel-fill.svg"
              alt="filled funnel icon"
              width="18"
              height="18"
            />
            a destra!</span
          >
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
        <p class="mb-3">
          Recupero la lista di tutti gli articoli recenti ...
          <span v-if="!not_filtering">{{ filters_summary }}</span>
        </p>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
  <div
    id="offcanvasFilters"
    class="offcanvas offcanvas-end"
    tabindex="-1"
    aria-labelledby="offcanvasFiltersLabel"
  >
    <div class="offcanvas-header">
      <h5 id="offcanvasFiltersLabel" class="offcanvas-title">Filtra tutti gli articoli)</h5>
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
        :ufd="ufd"
        @clear="filterActions.clear"
        @update_what="(value) => (filters.what = value)"
        @update_language="(value) => (filters.language = value)"
        @update_when="(value) => (filters.when = value)"
        @update_length="(value) => (filters.length = value)"
      />
    </div>
  </div>

  <div
    id="offcanvasFilters"
    class="offcanvas offcanvas-end"
    tabindex="-1"
    aria-labelledby="offcanvasFiltersLabel"
  >
    <div class="offcanvas-header">
      <h5 id="offcanvasFiltersLabel" class="offcanvas-title">Filtra tutti gli articoli)</h5>
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
        :ufd="ufd"
        @clear="filterActions.clear"
        @update_what="(value) => (filters.what = value)"
        @update_language="(value) => (filters.language = value)"
        @update_when="(value) => (filters.when = value)"
        @update_length="(value) => (filters.length = value)"
      />
    </div>
  </div>
</template>

<style>
/* Style to make the filter button less obtrusive with tabs */
.btn-primary[style*="position: fixed"] {
  top: 6rem; /* Adjust based on your navbar height if any */
  left: 1rem;
}
</style>
