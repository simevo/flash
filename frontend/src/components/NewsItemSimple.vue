<script setup lang="ts">
import type { News } from "../types/News"
import { RouterLink } from "vue-router"
import { secondsToString, secondsToString1 } from "./sts"
defineProps<{
  news: News
  index: number
}>()
</script>

<template>
  <li
    :id="'news_' + news.id"
    style="flex-direction: row; line-height: 1.1"
    class="card mb-3"
    :class="{
      'bg-light': news.read,
      'border-secondary': news.views > 0 && !news.read,
    }"
  >
    <img
      style="margin: 5px"
      class="float-start"
      width="30"
      height="30"
      :src="`${news.icon}`"
      alt="feed logo"
    />
    <div class="card-body text-secondary" style="padding: 5px">
      <RouterLink
        class="text-decoration-none"
        :to="'/article/' + news.id"
        exact
        :style="{ cursor: 'pointer' }"
      >
        <span
          v-if="news.language != base_language && news.title"
          class="card-text"
          style="margin-bottom: 0px"
          :lang="news.language"
          >[{{ news.title_original }}] </span
        ><span :lang="news.title ? base_language : news.language">{{
          news.title || news.title_original
        }}</span
        ><span v-if="!news.title_original && !news.title" :lang="base_language"
          >[Senza titolo]</span
        >
      </RouterLink>
      <div class="card-text">
        <small
          data-toggle="tooltip"
          class="text-muted"
          :title="new Date(news.epoch * 1000).toLocaleString()"
          >{{ secondsToString(news.age) }}</small
        >
        <small v-show="news.author.length > 0">
          <small class="text-muted"> di </small>
          <span>{{ news.author }}</span>
        </small>
        <small
          class="text-muted float-end"
          data-toggle="tooltip"
          title="tempo di lettura"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/clock.svg"
            alt="view icon"
            width="18"
            height="18"
          />
          {{ secondsToString1((60 * news.length) / 6 / 300) }}&nbsp;</small
        >
      </div>
      <!-- card-text -->
    </div>
  </li>
</template>
