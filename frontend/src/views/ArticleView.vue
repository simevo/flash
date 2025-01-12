<template>
  <div class="container my-3" v-if="article">
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
              v-if="article.language != base_language && article.title_original"
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
              'vai a tutti gli articoli con ' + article.author + ' come autore'
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
      <!-- eslint-disable -->
      <div
        id="content_tts"
        :lang="base_language"
        class="content col-md-8 offset-md-2"
        v-html="article.content || ''"
      />
      <!-- eslint-enable -->
    </div>
    <div class="row mt-3" v-else-if="article.content">
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
    <div class="row mt-3" v-else>
      <div
        id="content_tts"
        :lang="article.language || base_language"
        class="content col-md-8 offset-md-2"
        v-html="article.content_original || ''"
      />
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
import { computed, onMounted, ref, watch, type Ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import type { components } from "../generated/schema.d.ts"
import { secondsToString, secondsToString1 } from "@/components/sts"

const route = useRoute()

type Article = components["schemas"]["ArticleSerializerFull"]

const article: Ref<Article | null> = ref(null)

export interface Props {
  id: string
}

const props = withDefaults(defineProps<Props>(), {
  id: "",
})

async function fetchArticle() {
  const response = await fetch_wrapper(`../../api/articles/${props.id}`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Article = await response.json()
    article.value = data
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

onMounted(() => {
  console.log("ArticleView mounted")
  fetchArticle()
})

watch(
  () => route.params.id,
  async (newId) => {
    alert(newId)
  },
)
</script>
