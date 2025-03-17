<template>
  <div class="container my-3" v-if="count_fetch == 0">
    <div class="row my-3" v-if="article == null">
      <div class="col-md-12">
        <div class="alert alert-danger text-center" role="alert">
          Articolo non trovato.
        </div>
      </div>
    </div>
    <div v-else>
      <div class="row">
        <div class="text-center col-md-8 offset-md-2">
          <div>
            <router-link
              :to="`/feed/${article.feed.id}`"
              :href="`/feed/${article.feed.id}`"
              :title="`vai a tutti gli articoli della fonte ${article.feed}`"
            >
              <span class="h2">
                <img
                  width="30"
                  height="30"
                  :src="`https://notizie.calomelano.it/${article.feed.icon}`"
                  alt="feed logo"
                />
                {{ article.feed.title }}
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
                {{
                  secondsToString1((60 * article_length) / 6 / 300)
                }}&nbsp;</small
              >
            </div>
            <div class="float-end">
              <small
                >{{
                  secondsToString(new Date().getTime() / 1000 - article.stamp)
                }}
                ({{ new Date(article.stamp * 1000).toLocaleString() }})</small
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
                v-if="
                  article.language != base_language && article.title_original
                "
                :lang="article.language || base_language"
                >[{{ article.title_original }}]
              </span>
              <span
                v-if="!article.title_original && !article.title"
                :lang="base_language"
                >[Senza titolo]</span
              >
            </span>
            <span
              v-if="article.language != base_language && article.title"
              :lang="base_language"
              >{{ article.title }}</span
            >
          </h1>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 offset-md-2 text-muted">
          <button
            type="button"
            id="button-speak"
            class="btn btn-success btn-sm"
            title="Leggi ad alta voce"
            v-if="tts && !tts_open && paragraphs.length > 0"
            v-on:click="tts_speak()"
          >
            <img src="~bootstrap-icons/icons/megaphone.svg" alt="tts icon" />
          </button>
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
              :disabled="current_paragraph == 0"
            >
              <img
                src="~bootstrap-icons/icons/rewind-fill.svg"
                alt="rewind icon"
              />
            </button>
            <button
              type="button"
              id="button-stop"
              class="btn btn-success"
              title="Stop"
              v-on:click="tts_stop()"
              :disabled="!speaking"
            >
              <img
                src="~bootstrap-icons/icons/pause-fill.svg"
                alt="pause icon"
              />
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
              <img
                src="~bootstrap-icons/icons/stop-fill.svg"
                alt="close icon"
              />
            </button>
          </div>

          <ArticleActions
            :article="article"
            :clean="false"
            :share="true"
            class="float-start me-2"
            :translatable="
              article.language != base_language && !article.content
            "
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
              :title="
                'vai a tutti gli articoli con ' +
                article.author +
                ' come autore'
              "
              ><span>{{ article.author }}</span>
            </router-link>
          </small>
        </div>
      </div>
      <div class="row">
        <div class="col-md-8 offset-md-2" v-if="article.feed.license">
          <small class="text-muted">Licenza: {{ article.feed.license }}</small>
        </div>
      </div>
      <div class="row mt-3" v-if="article.language == base_language">
        <div
          id="content_tts"
          :lang="base_language"
          class="content col-md-8 offset-md-2"
          v-html="article.content || ''"
        />
      </div>
      <div
        class="row mt-3"
        v-else-if="
          article.content == null ||
          article.content.trim() === '' ||
          article.content.trim() === '<p><br></p>'
        "
      >
        <div
          id="content_tts"
          :lang="article.language || base_language"
          class="content col-md-8 offset-md-2"
          v-html="article.content_original || ''"
        />
      </div>
      <div class="row mt-3" v-else>
        <div
          id="content_tts"
          :lang="article.language || base_language"
          class="content col-md-4 offset-md-2"
          v-html="article.content_original || ''"
        />
        <div
          :lang="base_language"
          class="content col-md-4"
          v-html="article.content || ''"
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
import { fetch_wrapper } from "../utils"
import {
  computed,
  nextTick,
  onActivated,
  onMounted,
  ref,
  watch,
  type Ref,
} from "vue"
import { RouterLink, useRoute } from "vue-router"
import type { components } from "../generated/schema.d.ts"
import { secondsToString, secondsToString1 } from "@/components/sts"

import ArticleActions from "@/components/ArticleActions.vue"

const route = useRoute()

type Article = components["schemas"]["ArticleSerializerFull"]

const article: Ref<Article | null> = ref(null)
const count_fetch = ref(1)
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
  const response = await fetch_wrapper(`../../api/articles/${props.article_id}`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Article = await response.json()
    article.value = data
    count_fetch.value -= 1
  }
}

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
      count_fetch.value = 1
      await fetchArticle()
      nextTick(tts_init)
    }
  },
)

function getSentences(elements: Element[]): Element[] {
  let sentences: Element[] = []
  for (const element of elements) {
    if (
      ["P", "H1", "H2", "H3", "H4", "H5", "H6", "LI", "SPAN"].includes(
        element.tagName,
      )
    ) {
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
      find_voice(voices, lang || "it")
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
          "Speaker finished " +
            current_paragraph.value +
            " in " +
            e.elapsedTime +
            " seconds.",
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

// returns the voice
function find_voice(voices: SpeechSynthesisVoice[], lang: string) {
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
    voice = null
  } else if (voices_filtered.length == 1) {
    voice = voices_filtered[0]
  } else {
    if (detectApple()) {
      if (lang == "it") {
        const voices_filtered_alice = voices_filtered.filter(function (v) {
          return v.name == "Alice"
        })
        if (voices_filtered_alice.length > 0) {
          voice = voices_filtered_alice[0]
        }
      } else {
        const voices_filtered_samantha = voices_filtered.filter(function (v) {
          return v.name == "Samantha"
        })
        if (voices_filtered_samantha.length > 0) {
          voice = voices_filtered_samantha[0]
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
      voice = voices_filtered_default[0]
    } else {
      voice = voices_filtered[0]
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
</script>
