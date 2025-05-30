<script setup lang="ts">
import { copy_link, fetch_wrapper } from "../utils" // Removed find_voice
import {
  computed,
  // inject, // Removed inject as base_language is no longer injected here
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  watch,
  type Ref,
} from "vue"
import ArticleCard from "../components/ArticleCard.vue"
import TtsToolbar from "../components/TtsToolbar.vue" // Import TtsToolbar

import type { components } from "../generated/schema.d.ts"
import { useRoute } from "vue-router"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type UserArticleListsSerializerFull = components["schemas"]["UserArticleListsSerializerFull"]
type ListsMeRetrieve = (components["schemas"]["UserArticleListsSerializerFull"] & {
  article_count?: number
  total_estimated_reading_time?: string
})[]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]

const route = useRoute()

export interface Props {
  list_id?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  list_id: null,
})

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<FeedSerializerSimple[]> = ref([])
const lists: Ref<ListsMeRetrieve> = ref([])
const count_fetch = ref(2)
const current_list_id: Ref<string | null> = ref(props.list_id)

// TTS-related data properties removed, new ones added below
const show_tts_toolbar = ref(false)
const tts_available = ref(false)

const host = "notizie.calomelano.it"

async function fetchArticles() {
  if (current_list.value && current_list.value.articles.length > 0) {
    const response = await fetch_wrapper(
      `/api/articles/?ids=${current_list.value.articles.join(",")}`, // Changed path
    )
    if (response.status == 403) {
      document.location = "/accounts/"
    } else {
      const data: PaginatedArticleReadList = await response.json()
      articles.value = data.results
    }
  }
}

async function fetchFeeds() {
  const response = await fetch_wrapper(`/api/feeds/simple/`) // Changed path
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: FeedSerializerSimple[] = await response.json()
    feeds.value = data
    count_fetch.value -= 1
  }
}

async function fetchLists() {
  const response = await fetch_wrapper(`/api/lists/me/`) // Changed path
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: UserArticleListsSerializerFull[] = await response.json()
    lists.value = data // Store all lists first
    // Update current_list_id selection logic
    if (
      !current_list_id.value ||
      !lists.value.find((list) => list.id === current_list_id.value && !list.automatic)
    ) {
      const firstNonAutomaticList =
        displayableLists.value.length > 0 ? displayableLists.value[0] : null
      if (firstNonAutomaticList) {
        current_list_id.value = firstNonAutomaticList.id
      } else if (data.length > 0) {
        // Fallback if only automatic lists exist (though they won't be tabbed) or no non-automatic.
        // Or, set to null if no non-automatic lists should be selected by default.
        // For now, let's ensure a list is selected if any exist, even if it won't be tabbed.
        // This might need adjustment based on desired behavior when only automatic lists are present.
        // A better approach: if displayableLists is empty, current_list_id might become null.
        current_list_id.value =
          displayableLists.value.length > 0 ? displayableLists.value[0].id : null
      } else {
        current_list_id.value = null // No lists at all
      }
    }
    count_fetch.value -= 1
  }
}

const displayableLists = computed(() => {
  return lists.value.filter((list) => !list.automatic)
})

const current_list = computed(() => {
  // Ensure current_list is one of the displayable (non-automatic) lists
  if (current_list_id.value === null) return null
  return displayableLists.value.find((list) => list.id == current_list_id.value)
})

const feed_dict = computed(() => {
  const feed_dict: { [key: number]: FeedSerializerSimple } = {}
  feeds.value.forEach((feed) => {
    feed_dict[feed.id] = feed
  })
  return feed_dict
})

watch(current_list_id, (new_list_id) => {
  if (new_list_id) {
    articles.value = []
    fetchArticles()
  }
})

onMounted(async () => {
  console.log("ListsView mounted")
  await fetchLists()
  await fetchFeeds()
  await fetchArticles()
  // tts_init() removed
  tts_available.value = "speechSynthesis" in window
  if (tts_available.value) {
    window.speechSynthesis.cancel() // Clear any previous utterances
  }
})

onUnmounted(() => {
  console.log("ListsView unmounted")
  // Potentially add window.speechSynthesis.cancel() here if toolbar isn't guaranteed to unmount first
})

onActivated(() => {
  console.log("ListsView activated")
})

onDeactivated(() => {
  console.log("ListsView deactivated")
})

// New tts_speak method
function tts_speak() {
  if (!tts_available.value) {
    console.log("TTS not available")
    alert("La funzionalità Text-to-Speech non è disponibile su questo browser.")
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
  const all_cards = document.querySelectorAll(".article-card")
  all_cards.forEach((card) => (card as HTMLElement).style.removeProperty("background"))
}

function handleArticleChanged(articleId: number) {
  console.log(`ListsView handleArticleChanged: articleId=${articleId}`)
  const article_card = document.getElementById(`article-${articleId}`)
  if (article_card) {
    clearHighlights()
    article_card.scrollIntoView({ behavior: "smooth", block: "center" })
  }
}

function handleArticleProgress(articleId: number, progress: number) {
  console.log(`ListsView handleArticleProgress: articleId=${articleId}`)
  const article_card = document.getElementById(`article-${articleId}`)
  if (article_card) {
    article_card.style.background = `linear-gradient(90deg, lightgray ${progress}%, white ${progress}%)`
  }
}

async function removeList(list: UserArticleListsSerializerFull) {
  if (confirm(`Sei sicuro di voler rimuovere la lista "${list.name}"?`)) {
    const response = await fetch_wrapper(`/api/lists/${list.id}/`, {
      // Changed path
      method: "DELETE",
    })
    if (response.status == 403) {
      document.location = "/accounts/"
    } else {
      count_fetch.value += 1
      await fetchLists()
    }
  }
}

async function removeArticleFromList() {
  count_fetch.value += 1
  articles.value = []
  await fetchLists()
  fetchArticles()
}

watch(
  () => route.params.list_id,
  async (newId, oldId) => {
    console.log(`ListsView watch, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId !== oldId) {
      current_list_id.value = Array.isArray(newId) ? newId[0] : newId
    }
  },
)

// All TTS methods like tts_init, tts_speak (old), tts_continue, tts_restart, tts_back,
// tts_forward, tts_stop, read_article, fetchArticle (if only for TTS), stripHtml (if only for TTS),
// speaker_start, read, tts_close, tts_cleanup are removed.
// The 'voices' array and its 'onvoiceschanged' handler are also removed.
// 'base_language' inject is removed as it's passed as a prop.

function window_open(url: string): void {
  window.open(url)
}
</script>

<template>
  <div class="container-fluid" v-if="count_fetch == 0">
    <div class="row my-3" v-if="displayableLists.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non hai ancora creato delle liste personalizzate.
          <br />Per creare la tua prima lista, salva un articolo dalla sua pagina di dettaglio
          cliccando sul pulsante "<i>Salva in lista</i>"
          <img
            class="icon me-2"
            src="~bootstrap-icons/icons/heart-fill.svg"
            alt="filled heart icon"
            width="18"
            height="18"
          />.
        </div>
      </div>
    </div>
    <div class="row my-3" v-else>
      <div class="col-md-12">
        <p>Articoli salvati nelle tue liste personalizzate</p>
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item" role="presentation" v-for="list in displayableLists" :key="list.id">
            <button
              class="nav-link"
              :class="{ active: list.id == current_list_id }"
              :id="`list-${list.id}-tab`"
              @click="current_list_id = list.id"
              type="button"
              role="tab"
            >
              <!-- Removed automatic list icon as they are filtered out -->
              {{ list.name }}
              <button
                v-show="list.id == current_list_id"
                class="btn btn-outline-danger btn-sm ms-3"
                title="Rimuovi questa lista"
                @click="removeList(list)"
              >
                <img
                  class="icon"
                  src="~bootstrap-icons/icons/trash.svg"
                  alt="trash icon"
                  width="18"
                  height="18"
                />
              </button>
            </button>
          </li>
        </ul>
        <div class="tab-content my-3" id="myTabContent">
          <div
            class="tab-pane fade show active"
            id="home-tab-pane"
            role="tabpanel"
            tabindex="0"
            v-if="current_list"
          >
            <div v-if="current_list.articles.length == 0">
              <div class="alert alert-warning" role="alert">
                Non ci sono ancora articoli in questa lista. Per salvare un articolo, dalla pagina
                di dettaglio articolo clicca sul pulsante "<i>Salva in lista</i>"
                <img
                  class="icon me-2"
                  src="~bootstrap-icons/icons/heart-fill.svg"
                  alt="filled heart icon"
                  width="18"
                  height="18"
                />.
              </div>
            </div>
            <!-- Display article count and estimated reading time -->
            <div
              v-if="current_list && current_list.article_count !== undefined"
              class="mt-3 text-muted"
            >
              Questa lista contiene {{ current_list.article_count }}
              {{ current_list.article_count === 1 ? "articolo" : "articoli" }}. Il tempo totale di
              lettura stimato è: {{ current_list.total_estimated_reading_time }}.
              <div style="position: absolute; right: 1em" class="btn-group">
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
                    !current_list ||
                    current_list.articles.length === 0 ||
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
          </div>
        </div>
        <div class="row" v-if="current_list && current_list.articles.length > 0">
          <div v-if="articles.length == 0 && current_list.articles.length > 0">
            <!-- Show spinner only if current_list expects articles -->
            <div class="text-center col-md-8 offset-md-2">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          <div class="col-md-12" v-else-if="articles.length > 0">
            <div class="wrapper">
              <ArticleCard
                v-for="article in articles"
                :key="article.id"
                :article="article"
                :feed_dict="feed_dict"
                :index="1"
                :id="`article-${article.id}`"
                class="article-card"
                :list_id="current_list_id"
                @remove-article-from-list="removeArticleFromList"
              />
            </div>
          </div>
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
    style="position: fixed; z-index: 1000; bottom: 1em; left: 1em"
    class="btn-group btn-group-sm"
    id="button-tts"
    role="group"
    aria-label="Controlla la lettura"
    v-if="show_tts_toolbar"
  >
    <TtsToolbar
      :articles="articles"
      :base_language="'it'"
      :current_list_id="current_list_id"
      @tts-closed="handleTtsClosed"
      @tts-started="handleTtsStarted"
      @tts-stopped="handleTtsStopped"
      @article-changed="handleArticleChanged"
      @article-progress="handleArticleProgress"
    />
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
