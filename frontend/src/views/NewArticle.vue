<template>
  <div class="container">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <h1 id="page-top" class="text-center">Segnala un nuovo articolo</h1>
        <div class="my-3">
          <button
            @click="send()"
            type="button"
            class="btn btn-primary"
            aria-label="Invia l'articolo all'aggregatore"
            title="Invia l'articolo all'aggregatore"
            v-bind:disabled="errors_any"
            v-show="received"
          >
            Invia
          </button>
          <button
            @click="clean()"
            type="button"
            class="btn btn-secondary"
            aria-label="Pulisci tutti i campi"
            title="Pulisci tutti i campi"
            v-show="article.url"
          >
            Azzera
          </button>
          <a
            target="_blank"
            :href="article.url"
            role="button"
            class="btn btn-danger"
            aria-label="Apri il link in un nuovo tab"
            title="Apri il link in un nuovo tab"
            v-show="!errors['url']"
          >
            Apri URL
          </a>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <form class="needs-validation" novalidate>
          <div class="form-group" :class="{ 'is-invalid': errors['url'] }">
            <label for="url" v-show="!received && !trying">
              Copia e incolla il link all'articolo (URL)
            </label>
            <label style="display: none" v-show="trying"> Attendi qualche istante ...</label>
            <label style="display: none" v-show="received">
              Quando ti sembra a posto, premi sul bottone "Invia" per inviare l'articolo
              all'aggregatore
            </label>
            <input
              type="url"
              class="form-control mt-2"
              id="url"
              name="url"
              placeholder="http://..."
              v-model="article.url"
              :disabled="trying"
              @change="try_it()"
              autocomplete="off"
              spellcheck="false"
              autocorrect="off"
              autofocus
            />
            <p class="text-danger" v-if="errors['url']">{{ errors["url"] }}</p>
          </div>
          <div style="display: none" v-show="received">
            <hr />
            <div class="form-group my-3" :class="{ 'is-invalid': errors['title'] }">
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
              <p class="text-danger" v-if="errors['title']">
                {{ errors["title"] }}
              </p>
            </div>
            <!-- form-group -->
            <div class="form-group my-3" :class="{ 'is-invalid': errors['author'] }">
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
              <p class="text-danger" v-if="errors['author']">
                {{ errors["author"] }}
              </p>
            </div>
            <!-- form-group -->
            <div class="form-group my-3">
              <label for="language">Lingua</label>
              <button
                @click="guess_language()"
                type="button"
                class="btn btn-info btn-sm"
                title="Indovina la lingua"
              >
                ?
              </button>
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
            <!-- form-group -->
            <div class="form-group my-3">
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
            <!-- form-group -->
            <hr />
            <a href="#page-top">&uarr; Torna su</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed, inject, nextTick, onActivated, onMounted, ref } from "vue"
import { toast } from "vue3-toastify"
import { franc } from "franc"
import { Readability } from "@mozilla/readability"
import Quill from "quill"

let quill: Quill | null = null

onMounted(() => {
  console.log("NewArticle mounted")
  quill = new Quill("#editor", {
    theme: "snow",
  })
})

onActivated(() => {
  console.log("NewArticle activated")
  // set focus on the URL field
  const input = document.getElementById("url")
  if (input) {
    input.focus()
  }
})

const base_language: string = inject("base_language", "it")

const article = ref({
  author: "",
  title: "",
  language: "it",
  url: "",
})

function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

const errors = computed(() => {
  return {
    author: article.value.author ? "" : "Campo obbligatorio",
    title: article.value.title ? "" : "Campo obbligatorio",
    url: isValidUrl(article.value.url) ? "" : "Inserisci un URL valido",
  }
})

const errors_any = computed(() => {
  return Object.values(errors.value).some((e) => e)
})

const trying = ref(false)
const received = ref(false)

// ISO 639-3 to ISO 639-1
// https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
// https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
function convert(s: string): string {
  if (s == "arb") return "ar"
  if (s == "cat") return "ca"
  if (s == "fra") return "fr"
  if (s == "eng") return "en"
  if (s == "nld") return "nl"
  if (s == "por") return "pt"
  if (s == "rus") return "ru"
  if (s == "spa") return "es"
  if (s == "deu") return "de"
  return base_language
}

function find_candidates(elements: NodeListOf<Element>) {
  let candidates: string[] = []
  let j
  for (j = 0; j < elements.length; j++) {
    const e = elements[j]
    if (e.textContent) candidates = candidates.concat([e.textContent])
  }
  candidates = candidates.filter(function (value, index, self) {
    return self.indexOf(value) === index
  })
  return candidates
}

function guess_author(doc: Document) {
  let i

  // try first with meta tags
  const metaList = doc.getElementsByTagName("META")
  let candidate
  for (i = 0; i < metaList.length; i++) {
    const m = metaList[i] as HTMLMetaElement
    if (m.getAttribute("property") == "author") {
      candidate = m.content.replace(/\s+/g, " ")
      if (candidate) {
        return candidate
      }
    }
    if (m.getAttribute("property") == "article:author") {
      candidate = m.content.replace(/\s+/g, " ")
      if (candidate) {
        return candidate
      }
    }
    if (m.name == "author") {
      candidate = m.content.replace(/\s+/g, " ")
      if (candidate) {
        return candidate
      }
    }
  }

  // try with the HTML5 Link type "author"
  // <a href="http://johnsplace.com" rel="author">John</a>
  const rel = doc.querySelectorAll('[rel="author"]')
  const c0 = find_candidates(rel)
  if (c0.length == 1) {
    candidate = c0[0].replace(/\s+/g, " ")
    if (candidate) {
      return candidate
    }
  }

  // <a ... title="guido smorto" itemprop="author"><strong>guido smorto</strong></a>
  const itemprop = doc.querySelectorAll('[itemprop="author"]')
  const c1 = find_candidates(itemprop)
  if (c1.length == 1) {
    candidate = c1[0].replace(/\s+/g, " ")
    if (candidate) {
      return candidate
    }
  }

  // now try with the obvious classes:
  const classnames = [
    ".autore",
    ".author",
    ".auth",
    ".author-name",
    ".name-autore",
    ".item_author",
    ".bylines",
  ]
  for (i = 0; i < classnames.length; i++) {
    const classname = classnames[i]
    console.log("looking for ", classname)
    const elements = doc.querySelectorAll(classname)
    const c2 = find_candidates(elements)
    if (c2.length == 1) {
      candidate = c2[0].replace(/\s+/g, " ")
      if (candidate) {
        return candidate
      }
    }
  }

  // default
  return "anonimo"
}

function guess_language() {
  if (quill) {
    let text = quill.getText()
    // strip HTML tags
    const regex = /(<([^>]+)>)/gi
    text = text.replace(regex, "")
    // convert HTML entities
    const textarea = document.createElement("textarea")
    textarea.innerHTML = text
    text = textarea.value
    const language = franc(article.value.title + ". " + text, {
      only: ["arb", "fra", "eng", "ita", "nld", "por", "rus", "spa", "deu"],
    })
    article.value.language = convert(language)
  }
}

function try_it() {
  nextTick(() => {
    if (article.value.url && !errors.value["url"]) {
      trying.value = true
      prefill()
    }
  })
}

function send() {
  if (errors_any.value) {
    return
  }
  const data = {
    author: article.value.author,
    language: article.value.language,
    url: article.value.url,
    feed: 0,
    title: "",
    title_original: "",
    content: "",
    content_original: "",
  }
  if (article.value.language == base_language) {
    data["title"] = article.value.title
    if (quill) data["content"] = quill.root.innerHTML
  } else {
    data["title_original"] = article.value.title
    if (quill) data["content_original"] = quill.root.innerHTML
  }

  // send the data to the server
  fetch_wrapper("/api/articles/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.status == 403) {
        document.location = "/accounts/"
      } else if (response.status == 201) {
        toast("Articolo inviato con successo", { type: "success" })
        clean()
        response.json().then((data) => {
          document.location = "/res/article/" + data.id
        })
      } else {
        toast("Errore HTTP nel salvataggio dell'articolo: " + response.statusText, {
          type: "error",
        })
      }
    })
    .catch((error) => {
      toast("Eccezione durante il salvataggio dell'articolo: " + error, { type: "error" })
    })
}

function clean() {
  trying.value = false
  received.value = false
  if (quill) quill.setText("")
  article.value.author = ""
  article.value.title = ""
  article.value.language = base_language
  article.value.url = ""
  // set focus on the URL field
  const input = document.getElementById("url")
  if (input) {
    input.focus()
  }
}

function sanitize(doc: Document) {
  const blacklist = [
    "img",
    "figcaption",
    "figure",
    "hr",
    "source",
    "object",
    "video",
    "audio",
    "track",
    "embed",
    "param",
    "map",
    "area",
    "form",
    "input",
    "button",
    "canvas",
    "style",
    "script",
    "svg",
    "picture",
  ]
  let i
  for (i = 0; i < blacklist.length; i++) {
    const tag = blacklist[i]
    const elements = doc.getElementsByTagName(tag)
    if (elements.length > 0) {
      console.log(`sanitizing tag <${tag}>, found ${elements.length} occurrences`)
      let index
      for (index = elements.length - 1; index >= 0; index--) {
        elements[index].parentNode?.removeChild(elements[index])
      }
    }
  }
}

function prefill() {
  const escaped = encodeURIComponent(article.value.url)

  fetch_wrapper("/api/articles/?url=" + escaped, { method: "GET" })
    .then((response) => {
      if (!response.ok) {
        toast("Errore HTTP nel caricamento dell'articolo:" + response.statusText, { type: "error" })
      }
      return response.json()
    })
    .then((data) => {
      // { "count": 1, "next": null, "previous": null, "results": [...] }
      if (data.count === 0) {
        fetch_wrapper("/proxy/" + escaped, { method: "GET" })
          .then((response) => {
            if (!response.ok) {
              toast("Errore HTTP nel proxying dell'articolo:" + response.statusText, {
                type: "error",
              })
            }
            return response.text()
          })
          .then((html) => {
            const parser = document.createElement("a")
            parser.href = article.value.url
            const doc = document.implementation.createHTMLDocument("")
            doc.documentElement.innerHTML = html
            sanitize(doc)
            article.value.author = guess_author(doc)
            const r = new Readability(doc)
            try {
              const a = r.parse()
              if (a) {
                article.value.title = a.title
                if (quill) quill.clipboard.dangerouslyPasteHTML(0, a.content)
                guess_language()
              }
            } catch (error) {
              toast("Impossibile estrarre il contenuto: " + error, { type: "error" })
            }
            trying.value = false
            received.value = true
          })
          .catch((error) => {
            toast("La pagina non risponde: " + error, { type: "error" })
            trying.value = false
            received.value = true
          })
      } else {
        if (confirm("Un articolo con questa url esiste già, vuoi vederlo?")) {
          document.location = `/article/${data.results[0].id}`
        } else {
          trying.value = false
          clean()
        }
      }
    })
}

function resetAuthor() {
  article.value.author = ""
}

function resetTitle() {
  article.value.title = ""
}

function resetContent() {
  if (quill) quill.setText("")
}
</script>
