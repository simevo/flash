<template>
  <div class="container-fluid my-3" v-if="count_fetch == 0">
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <h1 id="page-top" class="text-center">Modifica la fonte</h1>
      </div>
    </div>
    <div class="row" v-if="feed">
      <div class="col-md-10 offset-md-1">
        <form class="needs-validation" novalidate>
          <hr />
          <div class="row">
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
                  data-bs-dismiss="alert"
                  aria-label="Cancella"
                  @click="resetTitle()"
                ></button>
              </div>
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
                style="right: 6em"
                data-bs-dismiss="alert"
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
                data-bs-dismiss="alert"
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
                data-bs-dismiss="alert"
                aria-label="Cancella"
                @click="resetLicense()"
              ></button>
            </div>
          </div>
          <div class="form-group my-3">
            <label for="icon">Icona</label>
            <div>
              <img
                width="100"
                :src="`https://notizie.calomelano.it/${feed.icon}`"
                class="img-fluid border"
                alt="feed logo"
              />
            </div>
          </div>
          <div class="form-group my-3">
            <label for="icon">Tags:</label>
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
import { fetch_wrapper } from "../utils"
import { onActivated, watch } from "vue"
import { useRoute } from "vue-router"
import { ref, onMounted, type Ref } from "vue"

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]

const feed: Ref<Feed | null> = ref(null)
const count_fetch = ref(1)

const route = useRoute()

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
  const response = await fetch_wrapper(`../../api/feeds/${props.feed_id}`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Feed = await response.json()
    feed.value = data
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

watch(
  () => route.params.feed_id,
  async (newId, oldId) => {
    console.log(`FeedEdit watch id, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId != oldId) {
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
</script>
