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
  <div :id="'feed_' + feed.id" class="card mb-3 p-1">
    <div class="d-flex flex-row justify-content-between align-items-center">
      <img
        style="margin: 5px"
        width="50"
        height="50"
        :src="`https://notizie.calomelano.it/${feed.icon}`"
        alt="feed logo"
      />
      <RouterLink
        class="text-decoration-none card-body"
        :to="'/feed/' + feed.id"
        :title="'vai a tutti gli articoli di ' + feed.title"
        :style="{ cursor: 'pointer' }"
      >
        <h5>{{ feed.title }} ({{ feed.article_count }} articoli)</h5>
        <span class="text-decoration-underline">{{ feed.homepage }}</span>
      </RouterLink>
      <div class="text-end">
        <span v-for="tag in feed.tags" :key="tag" class="badge text-bg-secondary m-1 p-2">
          {{ tag }}
        </span>
      </div>
    </div>
    <RatingToolbar
      class="d-flex justify-content-end mb-1"
      :id="feed.id"
      endpoint="/api/user-feeds/"
      v-bind:item="feed"
    ></RatingToolbar>
  </div>
</template>
