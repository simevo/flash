<script setup lang="ts">
import type {
  LanguageFilter,
  WhenFilter,
  LengthFilter,
  Filters,
  FeedCounts,
  Ufd,
} from "../types/Filters"

import { computed, onMounted, ref } from "vue"

import type { components } from "../generated/schema.d.ts"

type ArticleRead = components["schemas"]["ArticleRead"]
type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

const props = defineProps<{
  articles: ArticleRead[]
  feeds: FeedSerializerSimple[]
  filters: Filters
  feedCounts: FeedCounts
  notFiltering: boolean
  ufd: Ufd
}>()

const emit = defineEmits<{
  (e: "clear"): void
  (e: "update_what", value: string): void
  (e: "update_language", value: LanguageFilter): void
  (e: "update_when", value: WhenFilter): void
  (e: "update_length", value: LengthFilter): void
}>()

const local_what = ref(props.filters.what)

function update_what(value: string) {
  local_what.value = value
  if (value && value.trim().split(" ").length < 2) {
    return
  }
  emit("update_what", value)
}

function clearFilters() {
  emit("clear")
  local_what.value = ""
}

const mergedFeedCounts = computed(() => {
  const mfc = props.feedCounts
  props.feeds.forEach((feed) => {
    if (!(feed.id in mfc)) {
      mfc[feed.id] = {
        feed: feed.title,
        image: feed.image,
        count: 0,
        feed_id: feed.id,
      }
    }
  })
  // sort by decreasing count
  return Object.values(mfc).sort((a, b) => b.count - a.count)
})

onMounted(() => {
  console.log("FormFilter mounted")
})
</script>
<template>
  <div class="mb-3">
    <button
      type="button"
      class="btn btn-primary mb-3"
      :disabled="notFiltering"
      @click="clearFilters"
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
      :value="local_what"
      class="form-control mb-1"
      :class="{ 'is-invalid': local_what && local_what.trim().split(' ').length < 2 }"
      type="search"
      placeholder="parola1 parola2"
      aria-label="Filtra gli articoli che contengono tutte le parole chiave; inserisci due o più parole separate da spazi"
      title="Filtra gli articoli che contengono tutte le parole chiave; inserisci una o più parole separate da spazi"
      @change="update_what(($event.target as HTMLInputElement).value)"
    />
    <div id="validationServerUsernameFeedback" class="invalid-feedback">
      Almeno due parole chiave
    </div>
  </div>
  <select
    :value="filters.language"
    class="form-select mb-3"
    aria-label="Filtra per lingua"
    title="Filtra per lingua"
    @change="emit('update_language', ($event.target as HTMLSelectElement).value as LanguageFilter)"
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
    title="Filtra per data"
    @change="emit('update_when', ($event.target as HTMLSelectElement).value as WhenFilter)"
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
    title="Filtra per lunghezza"
    @change="emit('update_length', ($event.target as HTMLSelectElement).value as LengthFilter)"
  >
    <option value="all" selected>Qualsiasi lunghezza</option>
    <option value="0-1000">corto (&lt; 1000 caratteri)</option>
    <option value="1000-5000">medio</option>
    <option value="5000-10000000">lungo (&gt; 5000 caratteri)</option>
  </select>
  <hr />
  <h5>Frequenza delle fonti:</h5>
  <div v-for="feed in mergedFeedCounts" :key="feed.feed_id" class="my-3">
    <div v-if="!(feed.feed_id in ufd && ufd[feed.feed_id] == -5)">
      <img class="me-2" width="30" height="30" :src="feed.image" alt="feed logo" />
      <span class="text-muted">{{ feed.feed }} ({{ feed.count }})</span>
    </div>
  </div>
</template>
