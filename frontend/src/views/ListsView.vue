<script setup lang="ts">
import { copy_link, fetch_wrapper, find_voice } from "../utils"
import {
  computed,
  inject,
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  watch,
  type Ref,
} from "vue"
import ArticleCard from "../components/ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"
import { useRoute } from "vue-router"

type ArticleRead = components["schemas"]["ArticleRead"]
type Article = components["schemas"]["ArticleSerializerFull"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type UserArticleListsSerializerFull = components["schemas"]["UserArticleListsSerializerFull"]
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
const lists: Ref<UserArticleListsSerializerFull[]> = ref([])
const count_fetch = ref(2)
const current_list_id: Ref<string | null> = ref(props.list_id)

const tts = ref(false)
const tts_open = ref(false)
const stopped = ref(true)
const current_article = ref(0)
const speaking = ref(false)
const current_chunk = ref(0)

const host = "notizie.calomelano.it"

async function fetchArticles() {
  if (current_list.value && current_list.value.articles.length > 0) {
    const response = await fetch_wrapper(
      `../../api/articles/?ids=${current_list.value.articles.join(",")}`,
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
  const response = await fetch_wrapper(`../../api/feeds/simple/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: FeedSerializerSimple[] = await response.json()
    feeds.value = data
    count_fetch.value -= 1
  }
}

async function fetchLists() {
  const response = await fetch_wrapper(`../../api/lists/me/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: UserArticleListsSerializerFull[] = await response.json()
    lists.value = data // Store all lists first
    // Update current_list_id selection logic
    if (!current_list_id.value || !lists.value.find(list => list.id === current_list_id.value && !list.automatic)) {
      const firstNonAutomaticList = displayableLists.value.length > 0 ? displayableLists.value[0] : null
      if (firstNonAutomaticList) {
        current_list_id.value = firstNonAutomaticList.id
      } else if (data.length > 0) {
        // Fallback if only automatic lists exist (though they won't be tabbed) or no non-automatic.
        // Or, set to null if no non-automatic lists should be selected by default.
        // For now, let's ensure a list is selected if any exist, even if it won't be tabbed.
        // This might need adjustment based on desired behavior when only automatic lists are present.
        // A better approach: if displayableLists is empty, current_list_id might become null.
        current_list_id.value = displayableLists.value.length > 0 ? displayableLists.value[0].id : null;
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
  if (current_list_id.value === null) return null;
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
  tts_init()
})

onUnmounted(() => {
  console.log("ListsView unmounted")
})

onActivated(() => {
  console.log("ListsView activated")
})

onDeactivated(() => {
  console.log("ListsView deactivated")
})

async function removeList(list: UserArticleListsSerializerFull) {
  if (confirm(`Sei sicuro di voler rimuovere la lista "${list.name}"?`)) {
    const response = await fetch_wrapper(`../../api/lists/${list.id}/`, {
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

function tts_init() {
  if ("speechSynthesis" in window) {
    console.log("TTS API available")
    window.speechSynthesis.cancel()
    tts.value = true
  } else {
    console.log("no TTS API !")
    tts.value = false
  }
}

function tts_speak() {
  console.log("Speak TTS")
  tts_open.value = true
  current_article.value = 0
  // Mobile Safari requires an utterance (even a blank one) during
  // a user interaction to enable furher utterances
  speechSynthesis.speak(new SpeechSynthesisUtterance(""))
  tts_continue()
}

function tts_continue() {
  console.log("Continue TTS")
  stopped.value = false
  read_article()
}

function tts_restart() {
  console.log("Restart TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_speak()
}

function tts_back() {
  console.log("Back TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_cleanup()
  current_article.value -= 1
  tts_continue()
}

function tts_forward() {
  console.log("Forward TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_cleanup()
  current_article.value += 1
  tts_continue()
}

function tts_stop() {
  console.log("Stop TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_cleanup()
  speaking.value = false
}

let voices: SpeechSynthesisVoice[] = []

if ("speechSynthesis" in window) {
  voices = window.speechSynthesis.getVoices()
  // Chrome loads voices asynchronously.
  window.speechSynthesis.onvoiceschanged = function () {
    voices = window.speechSynthesis.getVoices()
  }
}

const base_language: string = inject("base_language", "it")

async function read_article() {
  console.log("Reading article: " + current_article.value)
  if (current_article.value >= articles.value.length) {
    tts_close()
    return
  }
  if (current_article.value < 0) {
    current_article.value = 0
  }
  const article = articles.value[current_article.value]
  const lang = article.language
  console.log("looking for voices with lang = " + lang)
  const voice = find_voice(voices, lang || "it")
  if (voice) {
    console.log("voice = ", voice)
    const article_full = await fetchArticle(article.id)
    const content =
      article.language === base_language ? article_full.content : article_full.content_original
    const title =
      article.language === base_language ? article_full.title : article_full.title_original
    const article_card = document.getElementById(`article-${article.id}`) as HTMLElement
    if (article_card) {
      article_card.style.background = "white"
      article_card.scrollIntoView()
    }
    speaking.value = true
    const content_stripped = stripHtml(content || "")
    const text = title + ". " + content_stripped
    // . matches any character (except for line terminators)
    // {1,1000} matches the previous token between 1 and 1000 times, as many times as possible, giving back as needed (greedy)
    console.log("Reading text:", text)
    const chunks = text.match(/.{1,1000}/g)
    if (chunks) {
      const trimmed_chunks = chunks.map((chunk) => chunk.trim())
      const filtered_chunks = trimmed_chunks.filter((chunk) => chunk !== "")
      console.log("Reading chunks:", filtered_chunks)
      current_chunk.value = 0
      read(article_card, voice, filtered_chunks, lang || "it")
    }
  } else {
    alert("Nessuna voce disponibile per:" + lang)
    current_article.value += 1
    read_article()
  }
}

async function fetchArticle(article_id: number): Promise<Article> {
  const response = await fetch_wrapper(`../../api/articles/${article_id}/`)
  const data: Article = await response.json()
  return data
}

function stripHtml(html: string): string {
  const doc = new DOMParser().parseFromString(html, "text/html")
  return doc.body.textContent || ""
}

function speaker_start() {
  console.log("Speaker started " + current_article.value)
}

function read(
  article_card: HTMLElement,
  voice: SpeechSynthesisVoice,
  chunks: string[],
  lang: string,
) {
  console.log(`${chunks.length} chunks left to read for article ${current_article.value}`)

  const utterance = new window.SpeechSynthesisUtterance()

  const my_current_article = current_article.value

  function speaker_error(e: SpeechSynthesisErrorEvent) {
    console.log("Speaker error " + e.error)
    if (!stopped.value && current_article.value == my_current_article) {
      read(article_card, voice, chunks, lang)
    }
  }

  function speaker_end() {
    console.log(
      `Speaker ended, current_article = ${current_article.value}, my_current_article = ${my_current_article}`,
    )
    if (!stopped.value && current_article.value == my_current_article) {
      read(article_card, voice, chunks, lang)
    }
  }

  if (current_chunk.value == chunks.length) {
    speaking.value = false
    utterance.removeEventListener("start", speaker_start)
    utterance.removeEventListener("error", speaker_error)
    utterance.removeEventListener("end", speaker_end)
    tts_cleanup()
    current_article.value += 1
    setTimeout(() => {
      read_article()
    }, 1500)
    return
  }
  utterance.voice = voice
  const chunk = chunks[current_chunk.value]
  current_chunk.value += 1
  if (article_card && !stopped.value) {
    const progress = Math.round((100 * current_chunk.value) / chunks.length)
    article_card.style.background = `linear-gradient(90deg, lightgray ${progress}%, white ${progress}%)`
  }
  utterance.text = chunk || ""
  utterance.lang = lang
  utterance.addEventListener("start", speaker_start)
  utterance.addEventListener("error", speaker_error)
  utterance.addEventListener("end", speaker_end)
  window.speechSynthesis.speak(utterance)
}

function tts_close() {
  console.log("Close TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_open.value = false
  tts_cleanup()
}

function tts_cleanup() {
  console.log("Cleanup TTS")
  window.speechSynthesis.cancel()
  const article_cards = document.getElementsByClassName("article-card")
  for (let i = 0; i < article_cards.length; i++) {
    ;(article_cards[i] as HTMLElement).style.removeProperty("background")
  }
}

function window_open(url: string): void {
  window.open(url)
}
</script>

<template>
  <div class="container-fluid" v-if="count_fetch == 0">
    <div class="row my-3" v-if="displayableLists.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non hai ancora creato delle liste personalizzate. Le liste automatiche (come Newsfeed) non sono mostrate qui.
          <br />Per creare la tua prima lista, salva un articolo dalla sua pagina di dettaglio cliccando sul pulsante "<i>Salva in lista</i>"
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
        <h1 class="text-center">Articoli salvati nelle tue liste personalizzate</h1>
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
          <li v-if="current_list_id && current_list"> <!-- Ensure a list is selected before showing these global list actions -->
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
                RSS
              </button>
              <button
                type="button"
                id="button-speak"
                class="btn btn-success"
                title="Leggi ad alta voce tutti gli articoli in questa lista"
                v-if="tts"
                :disabled="tts_open || !current_list || current_list.articles.length === 0 || articles.length === 0"
                v-on:click="tts_speak()"
              >
                <img src="~bootstrap-icons/icons/megaphone.svg" alt="tts icon" /> Leggi
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
                  Scarica
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
          </div>
        </div>
        <div class="row" v-if="current_list && current_list.articles.length > 0">
          <div v-if="articles.length == 0 && current_list.articles.length > 0"> <!-- Show spinner only if current_list expects articles -->
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
    v-if="tts && tts_open"
  >
    <button
      type="button"
      id="button-restart"
      class="btn btn-success"
      title="Dall'inizio"
      v-on:click="tts_restart()"
    >
      <img src="~bootstrap-icons/icons/skip-start-fill.svg" alt="fast backward icon" />
    </button>
    <button
      type="button"
      id="button-back"
      class="btn btn-success"
      title="Indietro"
      v-on:click="tts_back()"
      :disabled="current_article == 0"
    >
      <img src="~bootstrap-icons/icons/rewind-fill.svg" alt="rewind icon" />
    </button>
    <button
      type="button"
      id="button-stop"
      class="btn btn-success"
      title="Stop"
      v-on:click="tts_stop()"
      :disabled="!speaking"
    >
      <img src="~bootstrap-icons/icons/pause-fill.svg" alt="pause icon" />
    </button>
    <button
      type="button"
      id="button-continue"
      class="btn btn-success"
      title="Continua"
      v-on:click="tts_continue()"
      :disabled="speaking"
    >
      <img src="~bootstrap-icons/icons/play-fill.svg" alt="play icon" />
    </button>
    <button
      type="button"
      id="button-forward"
      class="btn btn-success"
      title="Avanti"
      v-on:click="tts_forward()"
      :disabled="current_article >= articles.length - 1"
    >
      <img src="~bootstrap-icons/icons/fast-forward-fill.svg" alt="forward icon" />
    </button>
    <button
      type="button"
      id="button-close"
      class="btn btn-success"
      title="Chiudi"
      v-on:click="tts_close()"
    >
      <img src="~bootstrap-icons/icons/stop-fill.svg" alt="close icon" />
    </button>
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
