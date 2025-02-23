<script setup lang="ts">
import { copy_link, fetch_wrapper } from "../utils"
import {
  computed,
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

type ArticleRead = components["schemas"]["ArticleRead"]
type Feed = components["schemas"]["Feed"]
type UserArticleListsSerializerFull =
  components["schemas"]["UserArticleListsSerializerFull"]
type PaginatedArticleReadList =
  components["schemas"]["PaginatedArticleReadList"]

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<Feed[]> = ref([])
const lists: Ref<UserArticleListsSerializerFull[]> = ref([])
const count_fetch = ref(2)
const current_list_id: Ref<string | null> = ref(null)

const host = "notizie.calomelano.it"

async function fetchArticles() {
  if (current_list.value) {
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
  const response = await fetch_wrapper(`../../api/feeds/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Feed[] = await response.json()
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
    if (data.length > 0) {
      current_list_id.value = data[0].id
    }
    count_fetch.value -= 1
  }
}

const current_list = computed(() => {
  return lists.value.find((list) => list.id == current_list_id.value)
})

const feed_dict = computed(() => {
  const feed_dict: { [key: number]: Feed } = {}
  feeds.value.forEach((feed) => {
    feed_dict[feed.id] = feed
  })
  return feed_dict
})

watch(current_list_id, (new_list_id) => {
  if (new_list_id) {
    fetchArticles()
  }
})

onMounted(() => {
  console.log("ReadPage mounted")
  fetchLists()
  fetchFeeds()
})

onUnmounted(() => {
  console.log("ReadPage unmounted")
})

onActivated(() => {
  console.log("ReadPage activated")
})

onDeactivated(() => {
  console.log("ReadPage deactivated")
})

async function removeArticleFromList() {
  count_fetch.value += 1
  await fetchLists()
  fetchArticles()
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
</template>

<style>
.wrapper {
  display: grid;
  margin: 0 auto;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-auto-rows: minmax(150px, auto);
}
</style>
