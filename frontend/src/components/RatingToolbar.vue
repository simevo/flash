<template>
  <div class="btn-toolbar float-right" role="toolbar" aria-label="Dai una valutazione">
    <div class="btn-group mr-2" role="group" aria-label="ratings">
      <NegativeRating
        v-for="threshold in [-4, -3, -2, -1, 0]"
        :key="threshold"
        :endpoint="endpoint"
        :item="item"
        :threshold="threshold"
        :readonly="updating"
        @updating="(status) => (updating = status)"
      ></NegativeRating>
      <PositiveRating
        v-for="threshold in [0, 1, 2, 3, 4]"
        :endpoint="endpoint"
        :key="threshold"
        :item="item"
        :threshold="threshold"
        :readonly="updating"
        @updating="(status) => (updating = status)"
      ></PositiveRating>
    </div>
  </div>
</template>

<script setup lang="ts">
import PositiveRating from "./PositiveRating.vue"
import NegativeRating from "./NegativeRating.vue"

import type { components } from "../generated/schema.d.ts"
import { ref } from "vue"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number }

const updating = ref(false)

defineProps<{
  item: PatchedFeed
  endpoint: string
}>()
</script>
