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
type UserArticleListsSerializerFull = components["schemas"]["UserArticleListsSerializerFull"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]

// --- All News Tab Data ---
const articles: Ref<ArticleRead[]> = ref([])
const next = ref<string>("") // For pagination of "All News"
const fetching = ref<boolean>(false) // For "All News" pagination loading state
const count_fetch = ref(0) // Combined counter for initial data loading (feeds + initial articles for active tab)

// --- Read Tab Data ---
const readArticles: Ref<ArticleRead[]> = ref([])

// --- For You Tab Data ---
const forYouArticles: Ref<ArticleRead[]> = ref([])
const allLists: Ref<UserArticleListsSerializerFull[]> = ref([])

// --- Common Data ---
const feeds: Ref<FeedSerializerSimple[]> = ref([]) // All feeds, potentially used by multiple tabs

// --- Tab Management ---
const activeTab: Ref<string> = ref("all-news")
const initialDataLoaded: Ref<{ allNews: boolean; read: boolean; forYou: boolean }> = ref({
  allNews: false,
  read: false,
  forYou: false,
})

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

// Computed properties for "All News" tab, also used by filter offcanvas
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
        image: feed_dict.value[article.feed].image,
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
    let summary = "Filtro articoli attivo"
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
      summary += ` - per fonti: [${filters.feed_ids.map((id) => feed_dict.value[id]?.title || id)}]`
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

// --- Fetching Functions ---

async function fetchAllNewsArticles() {
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
    articles.value = data.results
    next.value = data.next ? data.next : ""
    initialDataLoaded.value.allNews = true
    count_fetch.value -= 1
  }
}

async function fetchMoreAllNewsArticles() {
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

async function fetchReadArticles() {
  count_fetch.value += 1
  const response = await fetch_wrapper(`../../api/articles/?read=true`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: PaginatedArticleReadList = await response.json()
    readArticles.value = data.results
    initialDataLoaded.value.read = true
    count_fetch.value -= 1
  }
}

async function fetchForYouData() {
  count_fetch.value += 1
  const listsResponse = await fetch_wrapper(`../../api/lists/me/`)
  if (listsResponse.status == 403) {
    document.location = "/accounts/"
    count_fetch.value -= 1
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
      forYouArticles.value = articlesData.results
    }
  } else {
    forYouArticles.value = [] // Clear if no newsfeed or it's empty
  }
  initialDataLoaded.value.forYou = true
  count_fetch.value -= 1
}

async function fetchFeeds() {
  count_fetch.value += 1
  const response = await fetch_wrapper(`../../api/feeds/simple/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: FeedSerializerSimple[] = await response.json()
    feeds.value = data
  }
  count_fetch.value -= 1
}

const feed_dict = computed(() => {
  const dict: { [key: number]: FeedSerializerSimple } = {}
  feeds.value.forEach((feed) => {
    dict[feed.id] = feed
  })
  return dict
})

async function activateTab(tabName: string) {
  activeTab.value = tabName
  // Fetch feeds if not already fetched. They are needed by all tabs for feed_dict.
  if (feeds.value.length === 0) {
    await fetchFeeds()
  }

  // Fetch specific tab data if not already loaded
  if (tabName === "all-news" && !initialDataLoaded.value.allNews) {
    await fetchAllNewsArticles()
  } else if (tabName === "read" && !initialDataLoaded.value.read) {
    await fetchReadArticles()
  } else if (tabName === "for-you" && !initialDataLoaded.value.forYou) {
    await fetchForYouData()
  }
}

onMounted(async () => {
  console.log("HomeView mounted")
  // Activate "All News" by default. This will also trigger feed fetch if necessary.
  await activateTab("all-news")
})

onUnmounted(() => {
  console.log("HomeView unmounted")
})

onActivated(() => {
  console.log("HomeView activated")
  // Potentially refresh data or check active tab if coming back to the view
  // For now, let's rely on initial load and tab switching logic
})

onDeactivated(() => {
  console.log("HomeView deactivated")
})

watch(
  () => filters.what,
  async (newWhat, oldWhat) => {
    console.log(`HomeView what watch for 'All News', newWhat = [${newWhat}] oldWhat = [${oldWhat}]`)
    if (newWhat !== oldWhat && activeTab.value === "all-news") {
      articles.value = [] // Clear current "All News" articles
      // count_fetch is handled by fetchAllNewsArticles itself
      await fetchAllNewsArticles()
    }
  },
)
</script>

<template>
  <button
    v-if="activeTab === 'all-news'"
    class="btn btn-primary ms-2 btn-lg"
    :class="{ active: !not_filtering }"
    :title="filters_summary"
    data-bs-toggle="offcanvas"
    data-bs-target="#offcanvasFilters"
    type="button"
    style="position: fixed; top: 5rem; left: 95vw; z-index: 1030;"
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

  <div class="container-fluid mt-3">
    <ul class="nav nav-tabs mb-3" id="homeTab" role="tablist">
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'all-news' }"
          id="all-news-tab"
          data-bs-toggle="tab"
          data-bs-target="#all-news-pane"
          type="button"
          role="tab"
          aria-controls="all-news-pane"
          :aria-selected="activeTab === 'all-news'"
          @click="activateTab('all-news')"
        >
          Tutti
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'read' }"
          id="read-tab"
          data-bs-toggle="tab"
          data-bs-target="#read-pane"
          type="button"
          role="tab"
          aria-controls="read-pane"
          :aria-selected="activeTab === 'read'"
          @click="activateTab('read')"
        >
          Letti
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'for-you' }"
          id="for-you-tab"
          data-bs-toggle="tab"
          data-bs-target="#for-you-pane"
          type="button"
          role="tab"
          aria-controls="for-you-pane"
          :aria-selected="activeTab === 'for-you'"
          @click="activateTab('for-you')"
        >
          Per te
        </button>
      </li>
    </ul>

    <div class="tab-content" id="homeTabContent">
      <!-- All News Tab Pane -->
      <div
        class="tab-pane fade"
        :class="{ 'show active': activeTab === 'all-news' }"
        id="all-news-pane"
        role="tabpanel"
        aria-labelledby="all-news-tab"
        tabindex="0"
      >
        <p>
          Gli articoli più recenti.
        </p>
        <div v-if="count_fetch <= 0 && initialDataLoaded.allNews">
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
                @click="fetchMoreAllNewsArticles"
                :disabled="fetching"
                v-if="next != ''"
              >
                Carica altri articoli (tutti)
              </button>
              <p v-else>Fine (tutti)).</p>
            </div>
          </div>
        </div>
        <div class="container my-3" v-else-if="!initialDataLoaded.allNews && count_fetch > 0">
          <div class="row">
            <div class="text-center col-md-8 offset-md-2">
              <h1 class="mb-3" v-if="!not_filtering && activeTab === 'all-news'">
                {{ filters_summary }}...
              </h1>
              <h1 class="mb-3" v-else-if="activeTab === 'all-news'">
                Tutti gli articoli in ordine cronologico ...
              </h1>
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Read Tab Pane -->
      <div
        class="tab-pane fade"
        :class="{ 'show active': activeTab === 'read' }"
        id="read-pane"
        role="tabpanel"
        aria-labelledby="read-tab"
        tabindex="0"
      >
        <div v-if="count_fetch <= 0 && initialDataLoaded.read">
          <p>
            Gli articoli più recenti già letti da altri e/o da te
          </p>
          <div class="row my-3" v-if="readArticles.length == 0">
            <div class="col-md-12">
              <div class="alert alert-warning text-center" role="alert">
                Non ci sono articoli letti da visualizzare.
              </div>
            </div>
          </div>
          <div class="row my-3" v-else>
            <div class="col-md-12">
              <div class="wrapper">
                <ArticleCard
                  v-for="article in readArticles"
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
        <div
          class="container my-3"
          v-else-if="!initialDataLoaded.read && count_fetch > 0 && activeTab === 'read'"
        >
          <div class="row">
            <div class="text-center col-md-8 offset-md-2">
              <h1 class="mb-3">Articoli letti...</h1>
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- For You Tab Pane -->
      <div
        class="tab-pane fade"
        :class="{ 'show active': activeTab === 'for-you' }"
        id="for-you-pane"
        role="tabpanel"
        aria-labelledby="for-you-tab"
        tabindex="0"
      >
        <div v-if="count_fetch <= 0 && initialDataLoaded.forYou">
          <div class="row my-3" v-if="forYouArticles.length == 0">
            <div class="col-md-12">
              <div class="alert alert-warning text-center" role="alert">
                Non ci sono articoli per te da visualizzare. Assicurati
                di avere una lista chiamata "newsfeed" con articoli.
              </div>
            </div>
          </div>
          <div class="row my-3" v-else>
            <div class="col-md-12">
              <p>
                Personalizza questa lista automatica scegliendo le parole (prioritarie o vietate) e le lingue preferite nella
                <RouterLink to="/settings">pagina "Impostazioni"</RouterLink>.
              </p>
              <div class="wrapper">
                <ArticleCard
                  v-for="article in forYouArticles"
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
        <div
          class="container my-3"
          v-else-if="!initialDataLoaded.forYou && count_fetch > 0 && activeTab === 'for-you'"
        >
          <div class="row">
            <div class="text-center col-md-8 offset-md-2">
              <h1 class="mb-3">Articoli "For You"...</h1>
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="activeTab === 'all-news'"
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

/* Style to make the filter button less obtrusive with tabs */
.btn-primary[style*="position: fixed"] {
  top: 6rem; /* Adjust based on your navbar height if any */
  left: 1rem;
}
</style>
