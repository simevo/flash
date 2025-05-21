<template>
  <button
    v-on:click="set(item, threshold + 1, endpoint)"
    type="button"
    class="btn btn-outline-success btn-sm p-1"
    :disabled="readonly"
    :class="{
      'icon-success': (item.my_rating || 0) > threshold,
      'icon-light': (item.my_rating || 0) <= threshold,
    }"
    :title="`Dai ${threshold + 1} voti positivi`"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20px"
      height="20px"
      class="bi bi-star-fill"
      viewBox="0 0 16 16"
    >
      <path
        d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number | undefined }

const props = defineProps<{
  item: PatchedFeed
  threshold: number
  endpoint: string
  readonly: boolean
}>()

const emit = defineEmits<{
  (e: "rated", id: number, rating: number): void
  (e: "updating", status: boolean): void
}>()

function set(item: PatchedFeed, rating: number, endpoint: string) {
  if (props.readonly) {
    return
  }
  if (item.my_rating == rating) {
    rating = 0
  }
  item.my_rating = rating

  emit("updating", true)
  // update the value server-side ...
  const data = {
    feed: item.id,
    rating: rating,
  }
  fetch_wrapper(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.status == 403) {
        if (typeof window !== "undefined" && window.location) {
          window.location.href = "/accounts/"
        }
      } else if (response.status == 200) {
        alert("Rating aggiornato con successo")
      } else if (response.status == 201) {
        alert("Rating inserito con successo")
      } else {
        response.json().then((data) => {
          alert("Errore: " + response.statusText + "; " + JSON.stringify(data))
        })
      }
      emit("updating", false)
    })
    .catch((error) => {
      alert("Errore di rete: " + error)
      emit("updating", false)
    })
}
</script>

<style scoped>
.icon-success {
  fill: green;
}
.icon-light {
  fill: lightgray;
}
</style>
