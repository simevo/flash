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
  watch,
  type Ref,
} from "vue"
import ArticleCard from "../components/ArticleCard.vue"

import type { components } from "../generated/schema.d.ts"
import { useRoute } from "vue-router"

type ArticleRead = components["schemas"]["ArticleRead"]
type Article = components["schemas"]["ArticleSerializerFull"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]
type UserArticleListsSerializerFull =
  components["schemas"]["UserArticleListsSerializerFull"]
type PaginatedArticleReadList =
  components["schemas"]["PaginatedArticleReadList"]

const route = useRoute()

export interface Props {
  list_id: string | null
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
    lists.value = data
    if (data.length > 0 && !current_list_id.value) {
      const newsfeed = data.find((list) => list.name == "newsfeed")
      if (newsfeed) {
        current_list_id.value = newsfeed.id
      } else {
        current_list_id.value = data[0].id
      }
    }
    count_fetch.value -= 1
  }
}

const current_list = computed(() => {
  return lists.value.find((list) => list.id == current_list_id.value)
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
  speaking.value = false
  tts_cleanup()
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
  console.log("Reading " + current_article.value)
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
      article.language === base_language
        ? article_full.content
        : article_full.content_original
    const title =
      article.language === base_language
        ? article_full.title
        : article_full.title_original
    const article_card = document.getElementById(
      `article-${article.id}`,
    ) as HTMLElement
    if (article_card) {
      article_card.style.backgroundColor = "lightgray"
      article_card.scrollIntoView()
    }
    speaking.value = true
    const content_stripped = stripHtml(content || "")
    read(voice, title || "", content_stripped, lang || "it")
  }
}

// returns the voice
function find_voice(
  voices: SpeechSynthesisVoice[],
  lang: string,
): SpeechSynthesisVoice | null {
  console.log("found " + voices.length + " voices")
  let voices_filtered = voices.filter(function (v) {
    console.log("name = " + v.name + " lang = " + v.lang)
    return v.lang == lang
  })
  if (voices_filtered.length == 0) {
    // try matching only 2-character ISO code
    voices_filtered = voices.filter(function (v) {
      return v.lang.substr(0, 2) == lang
    })
  }
  console.log("found " + voices_filtered.length + " " + lang + " voices")
  if (voices_filtered.length == 0) {
    return null
  } else if (voices_filtered.length == 1) {
    return voices_filtered[0]
  } else {
    if (detectApple()) {
      if (lang == "it") {
        const voices_filtered_alice = voices_filtered.filter(function (v) {
          return v.name == "Alice"
        })
        if (voices_filtered_alice.length > 0) {
          return voices_filtered_alice[0]
        }
      } else {
        const voices_filtered_samantha = voices_filtered.filter(function (v) {
          return v.name == "Samantha"
        })
        if (voices_filtered_samantha.length > 0) {
          return voices_filtered_samantha[0]
        }
      }
    } // Apple-specific
    const voices_filtered_default = voices_filtered.filter(function (v) {
      return v.default
    })
    console.log(
      "found " +
        voices_filtered_default.length +
        " " +
        lang +
        " default voices",
    )
    if (voices_filtered_default.length > 0) {
      return voices_filtered_default[0]
    } else {
      return voices_filtered[0]
    }
  }
} // find_voice

function detectApple() {
  const userAgent = navigator.userAgent
  if (/Macintosh|MacIntel|MacPPC|Mac68K/.test(userAgent)) {
    return true
  } else if (/iPhone|iPad|iPod/.test(userAgent)) {
    return true
  } else {
    return false
  }
}

async function fetchArticle(article_id: number): Promise<Article> {
  const response = await fetch_wrapper(`../../api/articles/${article_id}`)
  const data: Article = await response.json()
  return data
}

function stripHtml(html: string): string {
  const doc = new DOMParser().parseFromString(html, "text/html")
  return doc.body.textContent || ""
}

function read(
  voice: SpeechSynthesisVoice,
  title: string,
  content: string,
  lang: string,
) {
  const utterance = new window.SpeechSynthesisUtterance()
  utterance.voice = voice
  utterance.text = title + ". " + content
  utterance.lang = lang
  utterance.addEventListener("end", function () {
    speaking.value = false
    tts_cleanup()
    if (!stopped.value) {
      current_article.value += 1
      read_article()
    }
  })
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
  const article_cards = document.getElementsByClassName("article-card")
  for (let i = 0; i < article_cards.length; i++) {
    ;(article_cards[i] as HTMLElement).style.removeProperty("background-color")
  }
}
</script>

<template>
  <div class="container-fluid" v-if="count_fetch == 0">
    <div class="row my-3" v-if="lists.length == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non hai ancora delle liste da visualizzare. Per creare la tua prima
          lista salva un articolo, dalla pagina di dettaglio articolo clicca sul
          pulsante "<i>Salva in lista</i>"
          <img
            class="icon me-2"
            src="~bootstrap-icons/icons/heart-fill.svg"
            alt="view icon"
            width="18"
            height="18"
          />.
        </div>
      </div>
    </div>
    <div class="row my-3" v-else>
      <div class="col-md-12">
        <h1 class="text-center">Articoli salvati nelle liste</h1>
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li
            class="nav-item"
            role="presentation"
            v-for="list in lists"
            :key="list.id"
          >
            <button
              class="nav-link"
              :class="{ active: list.id == current_list_id }"
              :id="`list-${list.id}-tab`"
              @click="current_list_id = list.id"
              type="button"
              role="tab"
            >
              <img
                v-if="list.automatic"
                class="icon"
                src="~bootstrap-icons/icons/robot.svg"
                alt="rss icon"
                width="18"
                height="18"
                title="Lista automatica"
              />
              {{ list.name }}
              <button
                v-show="list.id == current_list_id"
                type="button"
                class="btn btn-outline-primary btn-sm ms-3"
                title="Copia il link al feed RSS di questa lista"
                @click="
                  copy_link(`https://${host}/api/lists/${current_list_id}/rss/`)
                "
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
                class="btn btn-success btn-sm"
                title="Leggi ad alta voce"
                v-show="list.id == current_list_id"
                v-if="tts"
                :disabled="tts_open || articles.length === 0"
                v-on:click="tts_speak()"
              >
                <img
                  src="~bootstrap-icons/icons/megaphone.svg"
                  alt="tts icon"
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
            <div v-if="current_list?.articles.length == 0">
              <div class="alert alert-warning" role="alert">
                Non ci sono ancora articoli in questa lista. Per salvare un
                articolo, dalla pagina di dettaglio articolo clicca sul pulsante
                "<i>Salva in lista</i>"
                <img
                  class="icon me-2"
                  src="~bootstrap-icons/icons/heart-fill.svg"
                  alt="view icon"
                  width="18"
                  height="18"
                />.
              </div>
            </div>
          </div>
        </div>
        <div
          class="row"
          v-if="current_list && current_list?.articles.length > 0"
        >
          <div v-if="articles.length == 0">
            <div class="text-center col-md-8 offset-md-2">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
          <div class="col-md-12" v-else>
            <div class="wrapper">
              <ArticleCard
                v-for="article in articles"
                :key="article.id"
                :article="article"
                :feed_dict="feed_dict"
                :index="1"
                :id="`article-${article.id}`"
                class="article-card"
                :list_id="current_list.automatic ? null : current_list_id"
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
    aria-label="Leggi ad alta voce"
    v-if="tts && tts_open"
  >
    <button
      type="button"
      id="button-restart"
      class="btn btn-success"
      title="Dall'inizio"
      v-on:click="tts_restart()"
    >
      <img
        src="~bootstrap-icons/icons/skip-start-fill.svg"
        alt="fast backward icon"
      />
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
      <img
        src="~bootstrap-icons/icons/fast-forward-fill.svg"
        alt="forward icon"
      />
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
