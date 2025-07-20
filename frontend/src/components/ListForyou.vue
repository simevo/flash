<script setup lang="ts">
import { copy_link, fetch_wrapper } from "../utils"
import {
  computed,
  inject,
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  type Ref,
} from "vue"
import { toast } from "vue3-toastify"

import ArticleCard from "./ArticleCard.vue"
import TtsToolbar from "../components/TtsToolbar.vue"

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type UserArticleListsSerializerFull = components["schemas"]["UserArticleListsSerializerFull"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

const ready = ref(false)
const articles: Ref<ArticleRead[]> = ref([])
const allLists: Ref<UserArticleListsSerializerFull[]> = ref([])

// TTS-related data properties removed, new ones added below
const show_tts_toolbar = ref(false)
const tts_available = ref(false)
const current_list_id: Ref<string | null> = ref(null)

const host = "notizie.calomelano.it"
const base_language: string = inject("base_language", "it")

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
    current_list_id.value = newsfeedList.id
    const articlesResponse = await fetch_wrapper(
      `../../api/articles/?ids=${newsfeedList.articles.join(",")}`,
    )
    if (articlesResponse.status == 403) {
      document.location = "/accounts/"
    } else {
      const articlesData: PaginatedArticleReadList = await articlesResponse.json()
      articles.value = sort(articlesData.results)
    }
  } else {
    articles.value = [] // Clear if no newsfeed or it's empty
  }
  ready.value = true
}

function tts_speak() {
  if (!tts_available.value) {
    console.log("TTS not available")
    toast("La funzionalità Text-to-Speech non è disponibile su questo browser.", { type: "error" })
    return
  }
  console.log("ListsView tts_speak: showing toolbar")
  show_tts_toolbar.value = true
}

// Event handlers for TtsToolbar events
function handleTtsClosed() {
  console.log("ListsView handleTtsClosed: hiding toolbar")
  show_tts_toolbar.value = false
  clearHighlights()
}

function handleTtsStarted() {
  console.log("ListsView handleTtsStarted")
  // Optional: Add logic if needed when TTS starts
}

function handleTtsStopped() {
  console.log("ListsView handleTtsStopped")
  // Optional: Add logic if needed when TTS stops
}

function clearHighlights() {
  const all_cards = document.querySelectorAll(".foryou-article-card")
  all_cards.forEach((card) => (card as HTMLElement).style.removeProperty("background"))
}

function handleArticleChanged(articleId: number) {
  console.log(`ListsView handleArticleChanged: articleId=${articleId}`)
  const article_card = document.getElementById(`foryou-article-${articleId}`)
  if (article_card) {
    clearHighlights()
    article_card.scrollIntoView({ behavior: "smooth", block: "center" })
  }
}

function handleArticleProgress(articleId: number, progress: number) {
  console.log(`ListsView handleArticleProgress: articleId=${articleId}`)
  const article_card = document.getElementById(`foryou-article-${articleId}`)
  if (article_card) {
    article_card.style.background = `linear-gradient(90deg, lightgray ${progress}%, white ${progress}%)`
  }
}

function window_open(url: string): void {
  window.open(url)
}

onMounted(async () => {
  console.log("ListForyou mounted")
  fetchArticles()
  tts_available.value = "speechSynthesis" in window
  if (tts_available.value) {
    window.speechSynthesis.cancel() // Clear any previous utterances
  }
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
  <div>
    Gli articoli scelti per te. Personalizza questo newsfeed scegliendo le parole (prioritarie o
    vietate) e le lingue preferite nella
    <RouterLink to="/settings">pagina "Impostazioni"</RouterLink>.
    <div class="btn-group float-end">
      <button
        type="button"
        class="btn btn-primary ms-3"
        title="Copia il link al feed RSS di questa lista"
        @click="copy_link(`https://${host}/api/lists/${current_list_id}/rss/`)"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/rss.svg"
          alt="rss icon"
          width="18"
          height="18"
        />
      </button>
      <button
        type="button"
        id="button-speak"
        class="btn btn-success"
        title="Leggi ad alta voce tutti gli articoli in questa lista"
        v-if="tts_available"
        :disabled="
          show_tts_toolbar || // Disabled if toolbar is already open
          articles.length === 0
        "
        @click="tts_speak()"
      >
        <img src="~bootstrap-icons/icons/megaphone.svg" alt="tts icon" />
      </button>
      <span class="dropdown" role="group">
        <button
          id="download_menu"
          class="btn btn-secondary"
          type="button"
          data-bs-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
          title="Scarica"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/download.svg"
            alt="share icon"
            width="18"
            height="18"
          />
        </button>
        <span class="dropdown-menu" aria-labelledby="download_menu">
          <a class="dropdown-item" href="#" tabindex="-1" aria-disabled="true"
            >Scarica questa lista:</a
          >
          <a
            class="dropdown-item"
            href="#"
            title="Scarica in formato html"
            role="button"
            @click="window_open(`/api/lists/${current_list_id}/html/`)"
          >
            <img
              class="icon"
              src="~bootstrap-icons/icons/code.svg"
              alt="link icon"
              width="18"
              height="18"
            />
            <span> html</span>
          </a>
          <a
            class="dropdown-item"
            href="#"
            title="Scarica in formato epub"
            role="button"
            @click="window_open(`/api/lists/${current_list_id}/epub/`)"
          >
            <img
              class="icon"
              src="~bootstrap-icons/icons/book.svg"
              alt="link icon"
              width="18"
              height="18"
            />
            <span> epub</span>
          </a>
          <a
            class="dropdown-item"
            href="#"
            title="Scarica in formato pdf"
            role="button"
            @click="window_open(`/api/lists/${current_list_id}/pdf/`)"
          >
            <img
              class="icon"
              src="~bootstrap-icons/icons/file-earmark-pdf.svg"
              alt="link icon"
              width="18"
              height="18"
            />
            <span> pdf</span>
          </a>
        </span>
      </span>
    </div>
  </div>
  <div v-if="ready && Object.keys(feed_dict).length > 0">
    <div class="row my-5" v-if="articles.length == 0">
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
            :id="`foryou-article-${article.id}`"
            class="foryou-article-card"
            :list_id="current_list_id"
          />
        </div>
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
  <div
    style="position: fixed; z-index: 1000; bottom: 1em; left: 1em"
    class="btn-group btn-group-sm"
    id="button-tts"
    role="group"
    aria-label="Controlla la lettura"
    v-if="show_tts_toolbar"
  >
    <TtsToolbar
      :articles="articles"
      :base_language="base_language"
      @tts-closed="handleTtsClosed"
      @tts-started="handleTtsStarted"
      @tts-stopped="handleTtsStopped"
      @article-changed="handleArticleChanged"
      @article-progress="handleArticleProgress"
    />
  </div>
</template>
