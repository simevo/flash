<template>
  <div class="container my-3 overflow-hidden" v-if="count_fetch == 0">
    <div class="row my-3" v-if="article == null">
      <div class="col-md-12">
        <div class="alert alert-danger text-center" role="alert">Articolo non trovato.</div>
      </div>
    </div>
    <div v-else>
      <div class="row">
        <div class="text-center col-md-8 offset-md-2">
          <div>
            <router-link
              :to="`/feed/${article.feed}`"
              :href="`/feed/${article.feed}`"
              :title="`vai a tutti gli articoli della fonte ${article.feed}`"
            >
              <span class="h2">
                <img
                  width="30"
                  height="30"
                  :src="`${feed_dict[article.feed].image}`"
                  alt="feed logo"
                />
                {{ feed_dict[article.feed].title }}
              </span>
            </router-link>
          </div>
          <div class="text-muted">
            <div class="float-start">
              <img
                class="icon"
                src="~bootstrap-icons/icons/clock.svg"
                alt="globe icon"
                width="18"
                height="18"
              />
              <small
                >Tempo di lettura stimato:
                {{ secondsToString1((60 * article_length) / 6 / 300) }}&nbsp;</small
              >
            </div>
            <div class="float-end">
              <small
                >{{ secondsToString(new Date().getTime() / 1000 - article.stamp) }} ({{
                  new Date(article.stamp * 1000).toLocaleString()
                }})</small
              >
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-8 offset-md-2 title">
          <h1 class="float-start font-weight-bold">
            <span id="title_tts">
              <span
                v-if="article.language == base_language && article.title"
                :lang="base_language"
                >{{ article.title }}</span
              >
              <span
                v-if="article.language != base_language && article.title_original"
                :lang="article.language || base_language"
                >[{{ article.title_original }}]
              </span>
              <span v-if="!article.title_original && !article.title" :lang="base_language"
                >[Senza titolo]</span
              >
            </span>
            <span v-if="article.language != base_language && article.title" :lang="base_language">{{
              article.title
            }}</span>
          </h1>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 offset-md-2 text-muted">
          <button
            type="button"
            id="button-speak"
            class="btn btn-success btn-sm me-1"
            title="Leggi ad alta voce questo articolo"
            v-if="tts"
            :disabled="tts_open || paragraphs.length === 0"
            v-on:click="tts_speak()"
          >
            <img src="~bootstrap-icons/icons/megaphone.svg" alt="tts icon" />
          </button>
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
              :disabled="current_paragraph == 0"
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
              :disabled="current_paragraph >= paragraphs.length - 1"
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

          <ArticleActions
            :article="article"
            :clean="false"
            :share="true"
            class="float-start me-2"
            :translatable="article.language != base_language && !article.content"
            @translate="translate"
          />
          <small>Articolo originale: </small>
          <a target="_blank" :href="article.url || ''">
            <small style="word-wrap: break-word">{{ article.url }}</small>
          </a>
          <br />
        </div>
        <div class="text-muted col-md-2" v-if="article.author">
          <small class="float-end"
            >di
            <router-link
              :to="'/author/' + encodeURIComponent(article.author)"
              :title="'vai a tutti gli articoli con ' + article.author + ' come autore'"
              ><span>{{ article.author }}</span>
            </router-link>
          </small>
        </div>
      </div>
      <div class="row">
        <div class="col-md-8 offset-md-2" v-if="feed_dict[article.feed].license">
          <small class="text-muted">Licenza: {{ feed_dict[article.feed].license }}</small>
        </div>
      </div>
      <div class="row mt-3" style="min-height: 50vh" v-if="article.language == base_language">
        <div
          id="content_tts"
          :lang="base_language"
          class="content col-md-8 offset-md-2"
          v-html="article.content || ''"
        />
      </div>
      <div
        class="row mt-3"
        style="min-height: 50vh"
        v-else-if="article.content == null || article.content.trim() === ''"
      >
        <div
          id="content_tts"
          :lang="article.language || base_language"
          class="content col-md-8 offset-md-2"
          v-html="article.content_original || ''"
        />
      </div>
      <div class="row mt-3" style="min-height: 50vh" v-else>
        <div
          id="content_tts"
          :lang="article.language || base_language"
          class="content col-md-4 offset-md-2"
          v-html="article.content_original || ''"
        />
        <div :lang="base_language" class="content col-md-4" v-html="article.content || ''" />
      </div>
    </div>
    <div class="row my-3" v-if="related_articles.length > 0">
      <div class="col-md-8 offset-md-2">
        <h1>Articoli correlati:</h1>
        <ArticleCard
          v-for="article in related_articles"
          :key="article.id"
          :article="article"
          :feed_dict="feed_dict"
          :index="1"
          :list_id="null"
        />
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
import { fetch_wrapper, find_voice } from "../utils"
import { computed, nextTick, onActivated, onMounted, ref, watch, type Ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import type { components } from "../generated/schema.d.ts"
import { secondsToString, secondsToString1 } from "@/components/sts"

import ArticleActions from "@/components/ArticleActions.vue"
import ArticleCard from "@/components/ArticleCard.vue"

type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

const route = useRoute()

type Article = components["schemas"]["ArticleSerializerFull"]
type ArticleRead = components["schemas"]["ArticleRead"]

const article: Ref<Article | null> = ref(null)
const related_articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<FeedSerializerSimple[]> = ref([])

const count_fetch = ref(2)
const tts = ref(false)
const tts_open = ref(false)
const stopped = ref(true)
const paragraphs: Ref<Element[]> = ref([])
const current_paragraph = ref(0)
const speaking = ref(false)

let voices: SpeechSynthesisVoice[] = []
let voice: SpeechSynthesisVoice | null = null

if ("speechSynthesis" in window) {
  voices = window.speechSynthesis.getVoices()
  // Chrome loads voices asynchronously.
  window.speechSynthesis.onvoiceschanged = function () {
    voices = window.speechSynthesis.getVoices()
    // alert(voices.map((v) => v.name).join(", "))
  }
}

export interface Props {
  article_id: string
}

const props = withDefaults(defineProps<Props>(), {
  article_id: "",
})

async function fetchArticle() {
  const response = await fetch_wrapper(`../../api/articles/${props.article_id}/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Article = await response.json()
    article.value = data
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

async function fetchRelated() {
  const url = `../../api/articles/${props.article_id}/related/`
  const response = await fetch_wrapper(url)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    related_articles.value = await response.json()
  }
}

const feed_dict = computed(() => {
  const feed_dict: { [key: number]: FeedSerializerSimple } = {}
  feeds.value.forEach((feed) => {
    feed_dict[feed.id] = feed
  })
  return feed_dict
})

const article_length = computed(() => {
  if (article.value) {
    if (article.value.content) {
      return article.value.content.length
    } else if (article.value.content_original) {
      return article.value.content_original.length
    }
  }
  return 0
})

onMounted(async () => {
  console.log("ArticleView mounted")
  await fetchArticle()
  await fetchFeeds()
  await fetchRelated()
  nextTick(tts_init)
})

onActivated(() => {
  console.log("ArticleView activated")
})

watch(
  () => route.params.article_id,
  async (newId, oldId) => {
    console.log(`ArticleView watch, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId !== oldId) {
      article.value = null
      count_fetch.value = 2
      await fetchArticle()
      await fetchFeeds()
      await fetchRelated()
      nextTick(tts_init)
    }
  },
)

function getSentences(elements: Element[]): Element[] {
  let sentences: Element[] = []
  for (const element of elements) {
    if (["P", "H1", "H2", "H3", "H4", "H5", "H6", "LI", "SPAN"].includes(element.tagName)) {
      sentences.push(element)
    } else if (element.children) {
      sentences = sentences.concat(getSentences(Array.from(element.children)))
    }
  }
  return sentences
}

function tts_init() {
  if ("speechSynthesis" in window) {
    console.log("TTS API available")
    window.speechSynthesis.cancel()
    const content_tts = document.getElementById("content_tts")
    if (content_tts) {
      const lang = content_tts.getAttribute("lang")
      console.log("looking for voices with lang = " + lang)
      voice = find_voice(voices, lang || "it")
      if (voice) {
        console.log("voice = ", voice)
        const title_tts = document.getElementById("title_tts")
        if (title_tts) {
          paragraphs.value = [title_tts]
        } else {
          paragraphs.value = []
        }
        const children = Array.from(content_tts.children)
        paragraphs.value = paragraphs.value.concat(getSentences(children))
        current_paragraph.value = 0
        tts.value = true
        console.log("ready")
      } else {
        console.log("no voice found !")
        tts.value = false
      } // voice found
    } else {
      console.log("no content")
      tts.value = false
    } // voice found
  } else {
    console.log("no TTS API !")
    tts.value = false
  }
}

function tts_speak() {
  console.log("Speak TTS")
  tts_open.value = true
  current_paragraph.value = 0
  tts_continue()
}

function read_paragraph() {
  console.log("Reading " + current_paragraph.value)
  if (voice === null) {
    return
  }
  if (paragraphs.value.length <= current_paragraph.value) {
    tts_close()
    return
  }
  if (current_paragraph.value < 0) {
    current_paragraph.value = 0
  }
  const paragraph = paragraphs.value[current_paragraph.value]
  if (paragraph === null) {
    console.log("Null paragraph " + current_paragraph.value)
    current_paragraph.value += 1
    read_paragraph()
    return
  } else {
    if (paragraph.textContent) {
      const utterance = new window.SpeechSynthesisUtterance()
      utterance.voice = voice
      utterance.lang = voice.lang
      utterance.text = paragraph.textContent
      utterance.addEventListener("start", function () {
        console.log("Speaker started " + current_paragraph.value)
        speaking.value = true
        ;(paragraph as HTMLElement).style.backgroundColor = "lightgray"
        paragraph.scrollIntoView()
      })
      utterance.addEventListener("error", function (e) {
        console.log("Speaker error " + e.error)
        speaking.value = false
        ;(paragraph as HTMLElement).style.backgroundColor = "white"
        if (!stopped.value) {
          current_paragraph.value += 1
          read_paragraph()
        }
      })
      utterance.addEventListener("end", function (e) {
        console.log(
          "Speaker finished " + current_paragraph.value + " in " + e.elapsedTime + " seconds.",
        )
        speaking.value = false
        ;(paragraph as HTMLElement).style.backgroundColor = "white"
        if (!stopped.value) {
          current_paragraph.value += 1
          read_paragraph()
        }
      })
      window.speechSynthesis.speak(utterance)
    } else {
      console.log("Paragraph without innerText" + current_paragraph.value)
      current_paragraph.value += 1
      read_paragraph()
    }
  }
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
  current_paragraph.value -= 1
  tts_continue()
}

function tts_stop() {
  console.log("Stop TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_cleanup()
}

function tts_continue() {
  console.log("Continue TTS")
  stopped.value = false
  read_paragraph()
}

function tts_forward() {
  console.log("Forward TTS")
  stopped.value = true
  window.speechSynthesis.cancel()
  tts_cleanup()
  current_paragraph.value += 1
  tts_continue()
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
  for (let i = 0; i < paragraphs.value.length; i++) {
    const paragraph = paragraphs.value[i]
    if (paragraph && "style" in paragraph) {
      ;(paragraph as HTMLElement).style.backgroundColor = "white"
    }
  }
}

async function translate() {
  if (!article.value) {
    return
  }
  console.log("translate")
  count_fetch.value += 1
  const response = await fetch_wrapper(`../../api/articles/${props.article_id}/translate/`, {
    method: "POST",
  })
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    fetchArticle()
  }
}
</script>
