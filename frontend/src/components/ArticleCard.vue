<script setup lang="ts">
import type { components } from "../generated/schema.d.ts"
import { secondsToString, secondsToString1 } from "./sts"
import { fetch_wrapper } from "../utils"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

function stripHtml(html: string): string {
  const doc = new DOMParser().parseFromString(html, "text/html")
  return doc.body.textContent || ""
}

const props = defineProps<{
  article: ArticleRead
  feed_dict: { [key: number]: FeedSerializerSimple }
  index: number
  list_id: string | null
}>()

const emit = defineEmits<{
  (e: "removeArticleFromList", article_id: number): void
}>()

async function removeArticleFromList(list_id: string): Promise<void> {
  if (
    confirm(
      `Sei sicuro di voler rimuovere "${props.article.title_original || props.article.title}" dalla lista?`,
    )
  ) {
    const options = {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ article: props.article.id }),
    }
    const response = await fetch_wrapper(
      `../../api/lists/${list_id}/remove_article/`,
      options,
    )
    if (response.status == 403) {
      document.location = "/accounts/"
    } else {
      emit("removeArticleFromList", props.article.id)
    }
  }
}
</script>

<template>
  <div class="card m-1">
    <div class="card-body">
      <img
        style="margin: 5px"
        class="card-img-start"
        width="30"
        height="30"
        src="https://notizie.calomelano.it/static/icons/unknown.png"
        alt="feed logo"
        v-if="!feed_dict[article.feed]"
      />
      <router-link
        :to="`/feed/${article.feed}`"
        class="float-start"
        :title="`vai a tutti gli articoli della fonte ${feed_dict[article.feed].title}`"
        v-else
      >
        <img
          style="margin: 5px"
          class="card-img-start"
          width="30"
          height="30"
          :src="`https://notizie.calomelano.it/${feed_dict[article.feed].icon}`"
          alt="feed logo"
        />
      </router-link>
      <router-link
        :to="`/article/${article.id}`"
        exact
        class="text-decoration-none"
      >
        <div>
          <h5 class="fw-bold">
            <span
              v-if="article.language != base_language && article.title"
              style="margin-bottom: 0px"
              :lang="article.language || base_language"
              >{{ article.title_original }} &mdash; </span
            ><span
              :lang="
                article.title
                  ? base_language
                  : article.language || base_language
              "
              >{{ article.title || article.title_original }}</span
            ><span
              v-if="!article.title_original && !article.title"
              :lang="base_language"
              >[Senza titolo]</span
            >
          </h5>
        </div>
        <div class="text-justify small" style="font-family: serif">
          <span v-html="stripHtml(article.excerpt || '')"></span>...
        </div>
      </router-link>
    </div>
    <div class="card-footer">
      <div class="d-flex align-items-start">
        <div class="flex-grow-1 mb-1 text-truncate">
          <small
            data-toggle="tooltip"
            class="text-muted"
            :title="new Date(article.stamp * 1000).toLocaleString()"
            >{{
              secondsToString(new Date().getTime() / 1000 - article.stamp)
            }}</small
          >
          <small v-if="article.author">
            <span class="text-muted"> di </span>
            <router-link
              :to="`/author/${encodeURIComponent(article.author)}`"
              :title="`vai a tutti gli articoli con ${article.author} come autore`"
            >
              <span>{{ article.author }}</span>
            </router-link>
          </small>
        </div>
      </div>
      <div class="d-flex align-items-center">
        <small
          class="text-muted"
          data-toggle="tooltip"
          title="tempo di lettura stimato"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/clock.svg"
            alt="view icon"
            width="18"
            height="18"
          />
          {{ secondsToString1((60 * article.length) / 6 / 300) }}</small
        >
      </div>
      <span class="float-end" v-if="list_id">
        <button
          class="btn btn-outline-danger btn-sm"
          title="Rimuovi questo articolo dalla lista"
          @click="removeArticleFromList(list_id)"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/trash.svg"
            alt="view icon"
            width="18"
            height="18"
          />
        </button>
      </span>
    </div>
  </div>
</template>
