<script setup lang="ts">
import { RouterLink } from "vue-router"
import RatingToolbar from "./RatingToolbar.vue"

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]

defineProps<{
  feed: Feed
}>()
</script>

<template>
  <div
    :id="'feed_' + feed.id"
    style="flex-direction: row; line-height: 1.1"
    class="card mb-3"
  >
    <img
      style="margin: 5px"
      class="float-start"
      width="50"
      height="50"
      :src="`https://notizie.calomelano.it/${feed.icon}`"
      alt="feed logo"
    />
    <div class="card-body text-secondary" style="padding: 5px">
      <div class="card-text">
        <RouterLink
          class="text-decoration-none"
          :to="'/feed/' + feed.id"
          :title="'vai a tutti gli articoli di ' + feed.title"
          :style="{ cursor: 'pointer' }"
        >
          <h5>{{ feed.title }} ({{ feed.article_count }} articoli)</h5>
        </RouterLink>
        <span
          ><a :href="feed.url" target="_blank">{{ feed.url }}</a></span
        >
        <span class="float-end">
          {{ feed.tags }}
          <RatingToolbar
            :id="'rating_' + feed.id"
            endpoint="feeds"
            v-bind:item="feed"
          ></RatingToolbar>
        </span>
      </div>
    </div>
  </div>
</template>
