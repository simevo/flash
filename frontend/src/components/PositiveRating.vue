<template>
  <button
    v-on:click="set(item, threshold + 1, endpoint)"
    type="button"
    class="btn btn-outline-success btn-sm"
    :class="{
      'icon-success': item.my_rating > threshold,
      'icon-light': item.my_rating <= threshold,
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
import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]

defineProps<{
  item: Feed
  threshold: number
  endpoint: string
}>()

const emit = defineEmits(["rated"])

function set(item: Feed, rating: number, endpoint: string) {
  if (item.my_rating == rating) {
    rating = 0
  }
  // alert("set rating for " + item.id + " to " + rating)
  // $("div#rate_control button").attr("disabled", "disabled")
  item.my_rating = rating

  // update the value server-side
  // ...  emit.rated(item.id, rating)
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
