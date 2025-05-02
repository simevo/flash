<script setup lang="ts">
import { RouterLink } from "vue-router"
import RatingToolbar from "./RatingToolbar.vue"
import { secondsToString } from "./sts"
import { useAuthStore } from "../stores/auth.store"

const auth = useAuthStore()

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number | undefined }

defineProps<{
  feed: PatchedFeed
  clickable: boolean
}>()
</script>

<template>
  <div class="card mb-3" :id="'feed_' + feed.id" :class="feed.active ? '' : 'bg-dark-subtle'">
    <div class="row g-0">
      <div class="col-md-1 p-2 text-center align-center">
        <component
          :is="clickable ? 'router-link' : 'span'"
          class="text-decoration-none"
          :to="'/feed/' + feed.id"
          :title="clickable ? 'vai a tutti gli articoli di ' + feed.title : ''"
          :style="{ cursor: clickable ? 'pointer' : '' }"
        >
          <img
            width="100"
            :src="`https://notizie.calomelano.it/${feed.icon}`"
            class="img-fluid border"
            alt="feed logo"
          />
        </component>
      </div>
      <div class="col-md-11">
        <div class="card-body">
          <component
            :is="clickable ? 'router-link' : 'span'"
            class="text-decoration-none"
            :to="'/feed/' + feed.id"
            :title="clickable ? 'vai a tutti gli articoli di ' + feed.title : ''"
            :style="{ cursor: clickable ? 'pointer' : '' }"
          >
            <h5 class="card-title">{{ feed.title }} ({{ feed.article_count }} articoli)</h5>
            <span class="card-text text-decoration-underline">{{ feed.homepage }}</span>
          </component>
          <RouterLink
            id="edit"
            class="btn btn-outline-danger float-end"
            title="Modifica la fonte (funzione riservata agli utenti di staff)"
            role="button"
            type="button"
            :to="`../edit_feed/${feed.id}`"
            v-if="auth.user?.is_staff"
          >
            <img
              class="icon"
              src="~bootstrap-icons/icons/pencil.svg"
              alt="pencil icon"
              width="18"
              height="18"
            />
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
