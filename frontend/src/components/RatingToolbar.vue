<template>
  <div
    class="btn-toolbar float-right"
    role="toolbar"
    aria-label="Toolbar with button groups"
  >
    <div class="btn-group mr-2" role="group" aria-label="ratings">
      <NegativeRating
        v-for="threshold in [-4, -3, -2, -1, 0]"
        :key="threshold"
        :endpoint="endpoint"
        :item="item"
        :threshold="threshold"
      ></NegativeRating>
      <PositiveRating
        v-for="threshold in [0, 1, 2, 3, 4]"
        :endpoint="endpoint"
        :key="threshold"
        :item="item"
        :threshold="threshold"
      ></PositiveRating>
    </div>
  </div>
</template>

<script setup lang="ts">
import PositiveRating from "./PositiveRating.vue"
import NegativeRating from "./NegativeRating.vue"

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]

defineProps<{
  item: Feed
  endpoint: string
}>()
</script>
