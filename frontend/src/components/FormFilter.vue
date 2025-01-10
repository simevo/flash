<script setup lang="ts">
import type {
  LanguageFilter,
  WhenFilter,
  LengthFilter,
  Filters,
  FeedCounts,
  FeedCount,
} from "../types/Filters"

import { fetch_wrapper } from "../utils"

import type { CheckBoxValue } from "../types/CheckBoxValue"
import ThreeStateCheckBox from "./ThreeStateCheckBox.vue"
import type { Ref } from "vue"
import { computed, onMounted, ref } from "vue"
const all_feeds: Ref<CheckBoxValue> = ref(true)
const feeds: Ref<Feed[]> = ref([])

import type { components } from "../generated/schema.d.ts"

type Article = components["schemas"]["Article"]
type Feed = components["schemas"]["Feed"]

const props = defineProps<{
  articles: Article[]
  filters: Filters
  feedCounts: FeedCounts
  notFiltering: boolean
}>()

const emit = defineEmits<{
  (e: "clear"): void
  (e: "toggle_all_feeds", value: CheckBoxValue, feed_counts: FeedCount[]): void
  (e: "toggle_feed", feed_id: number): void
  (e: "update_what", value: string): void
  (e: "update_language", value: LanguageFilter): void
  (e: "update_when", value: WhenFilter): void
  (e: "update_length", value: LengthFilter): void
}>()

function changeAllFeeds(value: CheckBoxValue) {
  all_feeds.value = value
  emit("toggle_all_feeds", value, [])
}

async function fetchFeeds() {
  const response = await fetch_wrapper(`../../api/feeds/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Feed[] = await response.json()
    feeds.value = data
  }
}

const mergedFeedCounts = computed(() => {
  const mfc = props.feedCounts
  feeds.value.forEach((feed) => {
    if (!(feed.id in mfc)) {
      mfc[feed.id] = {
        feed: feed.title,
        icon: feed.icon,
        count: 0,
        feed_id: feed.id,
      }
    }
  })
  return mfc
})

onMounted(() => {
  console.log("FormFilter mounted")
  fetchFeeds()
})
</script>
<template>
  <form>
    <div class="mb-3">
      <button
        type="button"
        class="btn btn-primary mb-3"
        :disabled="notFiltering"
        @click="emit('clear')"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/trash3.svg"
          alt="trash icon"
          width="18"
          height="18"
        />
        Rimuovi tutti i filtri
      </button>
      <input
        :value="filters.what"
        class="form-control mb-1"
        type="search"
        placeholder="Parola chiave"
        aria-label="Filtra per parole chiave"
        @change="emit('update_what', ($event.target as HTMLInputElement).value)"
      />
    </div>
    <select
      :value="filters.language"
      class="form-select mb-3"
      aria-label="Filtra per lingua"
      @change="
        emit(
          'update_language',
          ($event.target as HTMLSelectElement).value as LanguageFilter,
        )
      "
    >
      <option value="all" selected>Qualsiasi lingua</option>
      <option value="ar">araba</option>
      <option value="ca">catalana</option>
      <option value="fr">francese</option>
      <option value="en">inglese</option>
      <option value="it">italiana</option>
      <option value="nl">olandese</option>
      <option value="pt">portoghese</option>
      <option value="ru">russa</option>
      <option value="es">spagnola</option>
      <option value="de">tedesca</option>
    </select>
    <select
      :value="filters.when"
      class="form-select mb-3"
      aria-label="Filtra per data"
      @change="
        emit(
          'update_when',
          ($event.target as HTMLSelectElement).value as WhenFilter,
        )
      "
    >
      <option value="all" selected>Qualsiasi data</option>
      <option value="24-0">Ultime 24 ore</option>
      <option value="168-0">Ultima settimana</option>
      <option value="720-0">Ultimo mese</option>
      <option value="8760-0">Ultimo anno</option>
      <option value="17520-8760">Un anno fa</option>
      <option value="26280-17520">Due anni fa</option>
      <option value="35040-26280">Tre anni fa</option>
      <option value="876000-35040">Più di tre anni fa</option>
    </select>
    <select
      :value="filters.length"
      class="form-select mb-3"
      aria-label="Filtra per lunghezza"
      @change="
        emit(
          'update_length',
          ($event.target as HTMLSelectElement).value as LengthFilter,
        )
      "
    >
      <option value="all" selected>Qualsiasi lunghezza</option>
      <option value="0-1000">corto (&lt; 1000 caratteri)</option>
      <option value="1000-5000">medio</option>
      <option value="5000-10000000">lungo (&gt; 5000 caratteri)</option>
    </select>
    <div class="form-check mb-3">
      <ThreeStateCheckBox
        id="flexCheckDefault"
        :value="all_feeds"
        @change="changeAllFeeds"
      />
      <label class="form-check-label" for="flexCheckDefault">
        <img
          class="me-2"
          width="30"
          height="30"
          src="~bootstrap-icons/icons/question-square-fill.svg"
          alt="question mark icon"
        />
        <span v-if="all_feeds === true">Qualsiasi fonte</span>
        <span v-else>Solo le fonti selezionate</span>
      </label>
    </div>
    <div v-for="feed in mergedFeedCounts" :key="feed.feed_id" class="mb-3">
      <div class="form-check">
        <input
          id="flexCheckDefault"
          class="form-check-input"
          type="checkbox"
          :disabled="filters.feed_ids.indexOf(-1) !== -1"
          :checked="filters.feed_ids.indexOf(feed.feed_id) !== -1"
          @change="emit('toggle_feed', feed.feed_id)"
        />
        <label class="form-check-label" for="flexCheckDefault">
          <img
            class="me-2"
            width="30"
            height="30"
            :src="'https://notizie.calomelano.it/' + feed.icon"
            alt="feed logo"
          />
          <span class="text-muted">{{ feed.feed }} ({{ feed.count }})</span>
        </label>
      </div>
    </div>
  </form>
</template>
