<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <h1 id="page-top" class="text-center">Modifica l'articolo</h1>
      </div>
    </div>
    <div class="row" v-if="article">
      <div class="col-md-10 offset-md-1">
        <form class="needs-validation" novalidate>
          <hr />
          <div class="row">
            <div class="form-group my-3 col">
              <label for="title">Titolo dell'articolo</label>
              <div class="input-group position-relative d-inline-flex align-items-center">
                <input
                  autocomplete="off"
                  autocorrect="off"
                  autocapitalize="off"
                  spellcheck="false"
                  required
                  type="text"
                  class="form-control"
                  id="title"
                  name="titolo"
                  placeholder="titolo"
                  v-model="article.title"
                />
                <button
                  type="button"
                  class="btn-close position-absolute"
                  style="right: 0.5em"
                  aria-label="Cancella"
                  @click="resetTitle()"
                ></button>
              </div>
            </div>
            <div class="form-group my-3 col" v-show="article.language != base_language">
              <label for="title">Titolo dell'articolo in lingua originale</label>
              <div class="input-group position-relative d-inline-flex align-items-center">
                <input
                  autocomplete="off"
                  autocorrect="off"
                  autocapitalize="off"
                  spellcheck="false"
                  required
                  type="text"
                  class="form-control"
                  id="title"
                  name="titolo"
                  placeholder="titolo"
                  v-model="article.title_original"
                />
                <button
                  type="button"
                  class="btn-close position-absolute"
                  style="right: 0.5em"
                  aria-label="Cancella"
                  @click="resetTitleOriginal()"
                ></button>
              </div>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="author">Autore</label>
            <div class="input-group position-relative d-inline-flex align-items-center">
              <input
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                required
                type="text"
                class="form-control"
                id="author"
                name="autore"
                placeholder="autore"
                v-model="article.author"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 0.5em"
                aria-label="Cancella"
                title="Cancella"
                @click="resetAuthor()"
              ></button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="url">Url</label>
            <div class="input-group position-relative d-inline-flex align-items-center">
              <input
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                type="text"
                class="form-control"
                id="url"
                name="url"
                placeholder="url"
                v-model="article.url"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 6em"
                aria-label="Cancella"
                title="Cancella"
                @click="resetUrl()"
                :disabled="!article.url"
              ></button>
              <a
                v-if="article.url"
                target="_blank"
                :href="article.url"
                role="button"
                class="btn btn-danger"
                aria-label="Apri il link in un nuovo tab"
                title="Apri il link in un nuovo tab"
              >
                Apri URL
              </a>
              <button
                v-else
                disabled
                type="button"
                class="btn btn-danger"
                aria-label="Apri il link in un nuovo tab"
                title="Apri il link in un nuovo tab"
              >
                Apri URL
              </button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="language">Lingua</label>
            <select class="form-control" id="language" v-model="article.language">
              <option value="ar">Arabo</option>
              <option value="ca">Catalano</option>
              <option value="de">Tedesco</option>
              <option value="en">Inglese</option>
              <option value="es">Spagnolo</option>
              <option value="fr">Francese</option>
              <option value="it">Italiano</option>
              <option value="nl">Olandese</option>
              <option value="pt">Portoghese</option>
              <option value="ru">Russo</option>
            </select>
          </div>
          <div class="row">
            <div class="form-group my-3 col">
              <label for="content">Testo completo dell'articolo</label>
              <button
                type="button"
                class="btn-close"
                style="float: right; margin-right: 8px"
                aria-label="Cancella"
                title="Cancella"
                @click="resetContent()"
              ></button>
              <div style="margin-top: 5px">
                <div id="editor"></div>
              </div>
              <!-- collapsible -->
            </div>
            <div class="form-group my-3 col" v-show="article.language != base_language">
              <label for="content">Testo completo dell'articolo in lingua originale</label>
              <button
                type="button"
                class="btn-close"
                style="float: right; margin-right: 8px"
                aria-label="Cancella"
                title="Cancella"
                @click="resetContentOriginal()"
              ></button>
              <div style="margin-top: 5px">
                <div id="editor_original"></div>
              </div>
              <!-- collapsible -->
            </div>
          </div>

          <!-- form-group -->
          <div class="text-center">
            <div class="btn-group" role="group" aria-label="Azioni">
              <button
                @click="save()"
                type="button"
                class="btn btn-primary"
                aria-label="Salva l'articolo"
                title="Salva l'articolo"
              >
                Salva
              </button>

              <router-link
                class="btn btn-secondary"
                :to="'/article/' + encodeURIComponent(article.id)"
                aria-label="Apri l'articolo"
                title="Apri l'articolo"
              >
                Apri
              </router-link>
            </div>
            <!-- btn-group -->
          </div>
          <a href="#page-top">&uarr; Torna su</a>
        </form>
      </div>
    </div>
    <div class="row" v-else>
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
import { toast } from "vue3-toastify"
import { inject, nextTick, onActivated, onMounted, ref, watch, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"
import Quill from "quill"

type Article = components["schemas"]["ArticleSerializerFull"]

const article: Ref<Article | null> = ref(null)
const count_fetch = ref(1)

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
    nextTick(() => {
      quill = new Quill("#editor", {
        theme: "snow",
      })
      setHtml(quill, article.value?.content || "")
      quill_original = new Quill("#editor_original", {
        theme: "snow",
      })
      setHtml(quill_original, article.value?.content_original || "")
    })
  }
}

let quill: Quill | null = null
let quill_original: Quill | null = null

function setHtml(quill: Quill, html: string) {
  const delta = quill.clipboard.convert({ html })
  quill.setContents(delta)
}

onMounted(async () => {
  console.log("EditArticle mounted")
  await fetchArticle()
})

onActivated(() => {
  console.log("EditArticle activated")
})

watch(
  () => props.article_id,
  async (newId, oldId) => {
    console.log(`ArticleEdit watch, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId !== oldId) {
      article.value = null
      count_fetch.value = 1
      await fetchArticle()
    }
  },
)

watch(
  () => article.value?.language,
  (newLanguage, oldLanguage) => {
    if (oldLanguage === base_language && newLanguage !== base_language) {
      if (article.value && quill && quill_original) {
        let currentContent = quill.root.innerHTML
        if (currentContent === "<p><br></p>") {
          currentContent = ""
        }
        setHtml(quill_original, currentContent)
        quill.setText("") // Clear the main editor
        article.value.content_original = currentContent
        article.value.content = ""
        article.value.title_original = article.value.title
        article.value.title = ""
      }
    } else if (oldLanguage !== base_language && newLanguage === base_language) {
      if (article.value && quill && quill_original) {
        let originalContent = quill_original.root.innerHTML
        if (originalContent === "<p><br></p>") {
          originalContent = ""
        }

        const currentMainContent = quill.root.innerHTML
        const isMainContentEmpty = currentMainContent === "" || currentMainContent === "<p><br></p>"

        if (!isMainContentEmpty) {
          if (
            !window.confirm(
              "There is already a translation in the main content field. Do you want to overwrite it with the content from the original language?",
            )
          ) {
            article.value.language = oldLanguage // Revert language change
            return // Stop processing
          }
        }

        setHtml(quill, originalContent)
        quill_original.setText("")
        article.value.content = originalContent
        article.value.content_original = ""
        article.value.title = article.value.title_original
        article.value.title_original = ""
      }
    }
  },
)

const base_language: string = inject("base_language", "it")

async function save() {
  if (!article.value) return
  const id = article.value.id
  let content = quill?.root.innerHTML
  if (content === "<p><br></p>") content = ""
  let content_original = quill_original?.root.innerHTML
  if (content_original === "<p><br></p>") content_original = ""
  const data = {
    title: article.value.title,
    title_original: article.value.title_original,
    author: article.value.author,
    language: article.value.language,
    url: article.value.url,
    content: content,
    content_original: content_original,
  }

  // send the data to the server
  fetch_wrapper(`/api/articles/${article.value.id}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.status == 403) {
        document.location = "/accounts/"
      } else if (response.status == 200) {
        alert("Articolo modificato con successo")
        document.location = "/res/article/" + id
      } else {
        response.json().then((data) => {
          toast("Errore: " + response.statusText + "; " + JSON.stringify(data), {
            type: "error",
          })
        })
      }
    })
    .catch((error) => {
      toast("Errore di rete: " + error, {
        type: "error",
      })
    })
}

function resetContent() {
  if (quill) quill.setText("")
  if (article.value) article.value.content = ""
}

function resetUrl() {
  if (article.value) article.value.url = ""
}

function resetAuthor() {
  if (article.value) article.value.author = ""
}

function resetTitle() {
  if (article.value) article.value.title = ""
}

function resetTitleOriginal() {
  if (article.value) article.value.title_original = ""
}

function resetContentOriginal() {
  if (quill_original) quill_original.setText("")
  if (article.value) article.value.content_original = ""
}
</script>
