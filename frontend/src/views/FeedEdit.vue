<template>
  <div class="container-fluid my-3" v-if="count_fetch == 0">
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <h1 id="page-top" class="text-center">Modifica la fonte</h1>
      </div>
    </div>
    <div class="row" v-if="feed">
      <div class="col-md-10 offset-md-1">
        <form id="form" class="needs-validation" novalidate>
          <hr />
          <div class="form-group my-3 col">
            <label for="title">Nome della fonte</label>
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
                v-model="feed.title"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 0.5em"
                aria-label="Cancella"
                @click="resetTitle()"
                :disabled="!feed.title"
              ></button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="homepage">Homepage</label>
            <div class="input-group position-relative d-inline-flex align-items-center">
              <input
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                type="text"
                class="form-control"
                id="homepage"
                name="homepage"
                placeholder="homepage"
                v-model="feed.homepage"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 9.5em"
                aria-label="Cancella"
                title="Cancella"
                @click="resetHomepage()"
                :disabled="!feed.homepage"
              ></button>
              <a
                v-if="feed.homepage"
                target="_blank"
                :href="feed.homepage"
                role="button"
                class="btn btn-danger"
                aria-label="Apri il link in un nuovo tab"
                title="Apri il link in un nuovo tab"
              >
                Apri Homepage
              </a>
              <button
                v-else
                disabled
                type="button"
                class="btn btn-danger"
                aria-label="Apri il link in un nuovo tab"
                title="Apri il link in un nuovo tab"
              >
                Apri Homepage
              </button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="url">Url del feed RSS</label>
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
                v-model="feed.url"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 6em"
                aria-label="Cancella"
                title="Cancella"
                @click="resetUrl()"
                :disabled="!feed.url"
              ></button>
              <a
                v-if="feed.url"
                target="_blank"
                :href="feed.url"
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
                aria-label="Scarica il contenuto dell'URL"
                title="Scarica il contenuto dell'URL"
              >
                Apri URL
              </button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="language">Lingua</label>
            <select class="form-control" id="language" v-model="feed.language">
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
          <div class="form-group my-3">
            <label for="active" class="form-check-label">Attiva</label>
            <input
              id="active"
              class="form-check-input float-end"
              type="checkbox"
              v-model="feed.active"
            />
          </div>
          <div class="form-group my-3">
            <label for="license">Licenza</label>
            <div class="input-group position-relative d-inline-flex align-items-center">
              <input
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                required
                type="text"
                class="form-control"
                id="license"
                name="licenza"
                placeholder="licenza"
                v-model="feed.license"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 0.5em"
                aria-label="Cancella"
                @click="resetLicense()"
              ></button>
            </div>
          </div>
          <div class="form-group my-3">
            <label>Tags:</label>
            <div>
              <span
                v-for="[tag, value] of Object.entries(tags)"
                :key="tag"
                class="badge text-bg-secondary m-1 p-2"
              >
                <input
                  type="checkbox"
                  :checked="value"
                  @input="(event) => (tags[<tag_keys>tag] = !value)"
                />
                {{ tag }}
              </span>
              <button
                type="button"
                class="btn-close"
                style="float: right; margin-right: 8px"
                aria-label="ripristina"
                title="ripistina selezione dei tag"
                @click="resetTags()"
              ></button>
            </div>
          </div>
          <div class="accordion" id="advancedAccordion">
            <div class="accordion-item">
              <h2 class="accordion-header">
                <button
                  class="accordion-button"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#collapseAdvanced"
                  aria-expanded="false"
                  aria-controls="collapseAdvanced"
                >
                  Avanzate
                </button>
              </h2>
              <div
                id="collapseAdvanced"
                class="accordion-collapse collapse"
                data-bs-parent="#advancedAccordion"
              >
                <div class="accordion-body">
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Icona</div>
                    <div class="col-md-2">
                      <input class="form-control" type="text" v-model="feed.image" />
                      <button
                        type="button"
                        class="btn-close"
                        aria-label="Cancella"
                        @click="resetIcon()"
                      ></button>
                    </div>
                    <div class="col-md-8">
                      <img
                        width="100"
                        :src="`${feed.image}`"
                        class="img-fluid border"
                        alt="feed logo"
                      />
                      <p>
                        <small class="text-muted">
                          Sono accettabili immagini in formato GIF, JPG/JPEG, PNG, SVG e WEBP più o
                          meno quadrate con lato minimo 16 pixel e dimensione massima 1 MB
                        </small>
                      </p>
                      <input
                        type="file"
                        id="image-input"
                        accept="image/svg+xml,image/png,image/jpeg,image/webp,image/gif"
                        class="form-control"
                        @change="handleFileSelect"
                        aria-label="Scegli un nuovo logo per la fonte"
                      />
                    </div>
                  </div>
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Attiva</div>
                    <div class="col-md-2">
                      <input class="form-check-input" type="checkbox" v-model="feed.active" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Se selezionato, la fonte sarà acquisita per mezzo del polling
                        automatico</small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Script</div>
                    <div class="col-md-2">
                      <input class="form-control" type="text" v-model="feed.script" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Percorso e parametri dello script specifico da invocare per questa fonte,
                        es: <code>/srv/calo.news/py/poll_XXX.py</code></small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light" v-show="feed.active">
                    <div class="col-md-2">Frequency</div>
                    <div class="col-md-2">
                      <input class="form-control" type="text" v-model="feed.frequency" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Il polling avverrà solo se la data e l'ora soddisfano tutte le condizioni
                        (in formato JSON:
                        <code>{ "day": [1, 2, 3], "hour": [12, 13], "weekday": [7] }</code>);
                        <code>hour</code> è l'ora 0-24 nel fuso orario UTC, <code>day</code> è il
                        giorno del mese (un numero negativo conta dal fondo) e
                        <code>weekday</code> è il giorno della settimana, numerando il Lunedì con 1
                        etc.</small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Incomplete</div>
                    <div class="col-md-2">
                      <input class="form-check-input" type="checkbox" v-model="feed.incomplete" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Forza lo scraping delle url per ottenere il testo completo</small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light" v-show="feed.incomplete">
                    <div class="col-md-2">Main</div>
                    <div class="col-md-2">
                      <input class="form-control" type="text" v-model="feed.main" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Selettore CSS dell'elemento che contiene il testo</small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light" v-show="feed.incomplete">
                    <div class="col-md-2">Exclude</div>
                    <div class="col-md-2">
                      <textarea class="form-control" type="text" v-model="feed.exclude" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted">Selettore CSS degli elementi da escludere</small>
                    </div>
                  </div>
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Salt url</div>
                    <div class="col-md-2">
                      <input class="form-check-input" type="checkbox" v-model="feed.salt_url" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >Per aggiungere un suffisso che renda uniche le urls (utile per fonti che le
                        riciclano)</small
                      >
                    </div>
                  </div>
                  <div class="row m-1 bg-light">
                    <div class="col-md-2">Cookies</div>
                    <div class="col-md-2">
                      <input class="form-control" type="text" v-model="feed.cookies" />
                    </div>
                    <div class="col-md-8">
                      <small class="text-muted"
                        >File col cookie jar da inviare con le richieste, es:
                        <code>/app/cookies_XXX.txt</code></small
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="text-center mt-3">
            <div class="btn-group" role="group" aria-label="Azioni">
              <button
                @click="save()"
                :disabled="!dirty"
                type="button"
                class="btn btn-primary"
                aria-label="Salva la fonte"
                title="Salva la fonte"
              >
                Salva
              </button>
              <button
                @click="restore()"
                :disabled="!dirty"
                type="button"
                class="btn btn-danger"
                aria-label="Ripristina la fonte ai valori originali"
                title="Ripristina la fonte ai valori originali"
              >
                Ripristina
              </button>
              <router-link
                class="btn btn-secondary"
                :to="'/feed/' + encodeURIComponent(feed.id)"
                aria-label="Apri la fonte"
                title="Apri la fonte"
              >
                Apri
              </router-link>
            </div>
          </div>
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
import { fetch_wrapper, getCookie } from "../utils"
import { computed, onActivated, watch } from "vue"
import { ref, onMounted, type Ref } from "vue"

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]

const feed: Ref<Feed | null> = ref(null)
let feed_original: Feed | null = null
const count_fetch = ref(1)

export interface Props {
  feed_id: string
}

const props = withDefaults(defineProps<Props>(), {
  feed_id: "",
})

type tag_keys =
  | "cultura"
  | "società"
  | "italia"
  | "estero"
  | "scienza_tecnica"
  | "sport"
  | "economia"
  | "blog"
  | "notiziario"
  | "rivista"

const tags = ref({
  cultura: false,
  società: false,
  italia: false,
  estero: false,
  scienza_tecnica: false,
  sport: false,
  economia: false,
  blog: false,
  notiziario: false,
  rivista: false,
})

async function fetchFeed() {
  const response = await fetch_wrapper(`../../api/feeds/${props.feed_id}/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Feed = await response.json()
    feed.value = data
    feed_original = { ...data }
    resetTags()
    feed.value.tags?.forEach((tag) => {
      tags.value[<tag_keys>tag] = true
    })
    count_fetch.value -= 1
  }
}

onMounted(() => {
  console.log("FeedEdit mounted")
  fetchFeed()
})

onActivated(() => {
  console.log("FeedEdit activated")
})

const dirty = computed(() => {
  return JSON.stringify(feed.value) !== JSON.stringify(feed_original)
})

watch(
  () => props.feed_id,
  async (newId, oldId) => {
    console.log(`FeedEdit watch id, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId != oldId) {
      feed.value = null
      count_fetch.value += 1
      await fetchFeed()
    }
  },
)

async function save() {
  if (!feed.value) return
  const id = feed.value.id
  const data = { ...feed.value }
  data.tags = Object.keys(tags.value).filter((v) => tags.value[<tag_keys>v])
  fetch_wrapper(`/api/feeds/${id}/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.status == 403) {
        document.location = "/accounts/"
      } else if (response.status == 200) {
        alert("Fonte modificata con successo")
        document.location = "/res/feed/" + id
      } else {
        response.json().then((data) => {
          alert("Errore: " + response.statusText + "; " + JSON.stringify(data))
        })
      }
    })
    .catch((error) => {
      alert("Errore di rete: " + error)
    })
}

function restore() {
  const form = document.getElementById("form") as HTMLFormElement
  form.reset()
  feed.value = feed_original
}

function resetUrl() {
  if (feed.value) feed.value.url = ""
}

function resetTitle() {
  if (feed.value) feed.value.title = ""
}

function resetHomepage() {
  if (feed.value) feed.value.homepage = ""
}

function resetLicense() {
  if (feed.value) feed.value.license = ""
}

function resetTags() {
  Object.keys(tags.value).forEach((tag) => {
    tags.value[<tag_keys>tag] = false
  })
}

function resetIcon() {
  if (feed.value) feed.value.image = "/static/icons/unknown.png"
}

async function handleFileSelect(event: Event) {
  if (!event.target) return
  const target = event.target as HTMLInputElement
  if (!target.files) return
  const file = target.files[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append("image", file)

    const csrftoken = getCookie("csrftoken")
    const response = await fetch("/api/upload/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrftoken,
      },
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(`${response.status} - ${text}`)
    }

    const data = await response.json()
    handleSuccess(data)
  } catch (error) {
    alert(`Impossibile caricare l'immagine: ${error}`)
  }
}

type SuccessResponse = {
  fileUrl: string
  filename: string
}

function handleSuccess(data: SuccessResponse) {
  console.log("Upload successful:", data)
  if (feed.value) feed.value.image = data.fileUrl
  // Update UI with success message
}
</script>
