<template>
  <div class="container-fluid my-3">
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <h1 id="page-top" class="text-center">Crea una nuova fonte</h1>
      </div>
    </div>
    <div class="row" v-if="feed">
      <div class="col-md-10 offset-md-1">
        <form class="needs-validation" novalidate>
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
                :class="{ 'is-invalid': errors['title'] }"
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
            <p class="text-danger" v-if="errors['title']">{{ errors["title"] }}</p>
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
                :class="{ 'is-invalid': errors['homepage'] }"
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
            <p class="text-danger" v-if="errors['homepage']">{{ errors["homepage"] }}</p>
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
                :class="{ 'is-invalid': errors['url'] }"
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
            <p class="text-danger" v-if="errors['url']">{{ errors["url"] }}</p>
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
                :class="{ 'is-invalid': errors['license'] }"
              />
              <button
                type="button"
                class="btn-close position-absolute"
                style="right: 0.5em"
                aria-label="Cancella"
                @click="resetLicense()"
              ></button>
            </div>
            <p class="text-danger" v-if="errors['license']">{{ errors["license"] }}</p>
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
                @click="send()"
                type="button"
                class="btn btn-primary"
                aria-label="Crea la fonte"
                title="Crea la fonte"
                :disabled="errors_any"
              >
                Crea
              </button>
              <button
                @click="clean()"
                type="button"
                class="btn btn-secondary"
                aria-label="Pulisci tutti i campi"
                title="Pulisci tutti i campi"
              >
                Azzera
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { computed } from "vue"
import { toast } from "vue3-toastify"
import { ref, onMounted, type Ref } from "vue"

import type { components } from "../generated/schema.d.ts"
type FeedCreate = components["schemas"]["FeedCreate"]
type FeedCreatePatched = Pick<
  FeedCreate,
  | "homepage"
  | "url"
  | "language"
  | "title"
  | "license"
  | "active"
  | "tags"
  | "exclude"
  | "main"
  | "script"
  | "frequency"
  | "cookies"
  | "incomplete"
  | "salt_url"
>

const feed: Ref<FeedCreatePatched> = ref({
  homepage: "",
  url: "",
  language: "en",
  title: "",
  license: "",
  active: true,
  tags: [],

  exclude: "",
  main: "",
  script: "",
  frequency: "",
  cookies: "",
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

onMounted(() => {
  console.log("NewFeed mounted")
})

async function send() {
  if (errors_any.value) {
    return
  }
  const data = { ...feed.value }
  data.tags = Object.keys(tags.value).filter((v) => tags.value[<tag_keys>v])
  fetch_wrapper(`/api/feeds/`, {
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
        toast("Fonte aggiunta con successo", { type: "success" })
        clean()
        response.json().then((data) => {
          document.location = "/res/feed/" + data.id
        })
      } else {
        response.json().then((data) => {
          toast("Errore: " + response.statusText + "; " + JSON.stringify(data), { type: "error" })
        })
      }
    })
    .catch((error) => {
      toast("Errore di rete: " + error, { type: "error" })
    })
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

function clean() {
  resetUrl()
  resetTitle()
  resetHomepage()
  resetLicense()
  resetTags()
}

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
    title: feed.value.title ? "" : "Campo obbligatorio",
    url: isValidUrl(feed.value.url) ? "" : "Inserisci un RSS URL valido",
    license: feed.value.license ? "" : "Campo obbligatorio",
    homepage: isValidUrl(feed.value.homepage) ? "" : "Inserisci un homepage URL valido",
  }
})

const errors_any = computed(() => {
  return Object.values(errors.value).some((e) => e)
})
</script>
