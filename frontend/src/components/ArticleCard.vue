<script setup lang="ts">
import type { components } from "../generated/schema.d.ts"
import { secondsToString, secondsToString1 } from "./sts"

type ArticleRead = components["schemas"]["ArticleRead"]
type Feed = components["schemas"]["Feed"]

defineProps<{
  article: ArticleRead
  feed_dict: { [key: number]: Feed }
  index: number
}>()
</script>

<template>
  <div class="card m-1">
    <div class="card-body">
      <router-link
        :to="`/feed/${article.feed}`"
        class="float-start"
        :title="`vai a tutti gli articoli della fonte ${feed_dict[article.feed].title}`"
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
          <span v-html="article.excerpt"></span>...
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
    </div>
  </div>
</template>
