<script setup lang="ts">
import { RouterLink } from "vue-router"
import RatingToolbar from "./RatingToolbar.vue"
import { secondsToString } from "./sts"

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number }

defineProps<{
  feed: PatchedFeed
}>()
</script>

<template>
  <div class="card mb-3" :id="'feed_' + feed.id" :class="feed.active ? '' : 'bg-dark-subtle'">
    <div class="row g-0">
      <div class="col-md-1 p-2 text-center align-center">
        <RouterLink
          class="text-decoration-none"
          :to="'/feed/' + feed.id"
          :title="'vai a tutti gli articoli di ' + feed.title"
          :style="{ cursor: 'pointer' }"
        >
          <img
            width="100"
            :src="`https://notizie.calomelano.it/${feed.icon}`"
            class="img-fluid border"
            alt="feed logo"
          />
        </RouterLink>
      </div>
      <div class="col-md-11">
        <div class="card-body">
          <RouterLink
            class="text-decoration-none"
            :to="'/feed/' + feed.id"
            :title="'vai a tutti gli articoli di ' + feed.title"
            :style="{ cursor: 'pointer' }"
          >
            <h5 class="card-title">{{ feed.title }} ({{ feed.article_count }} articoli)</h5>
            <span class="card-text text-decoration-underline">{{ feed.homepage }}</span>
          </RouterLink>
          <p class="card-text my-1">
            <span v-for="tag in feed.tags" :key="tag" class="badge text-bg-secondary m-1 p-2">
              {{ tag }}
            </span>
          </p>
          <p class="card-text" v-if="feed.last_polled_epoch">
            <small class="text-body-secondary">
              Ultimo aggiornamento
              {{ secondsToString(new Date().getTime() / 1000 - feed.last_polled_epoch) }}
            </small>
            <RatingToolbar
              class="float-end mb-2"
              :id="feed.id"
              endpoint="/api/user-feeds/"
              v-bind:item="feed"
            ></RatingToolbar>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
