import { defineStore } from "pinia"
import { useLocalStorage } from "@vueuse/core"

import type { Filters } from "../types/Filters"

const STORE_NAME = "filters"

const no_filters: Filters = {
  what: "",
  when: "all",
  language: "all",
  length: "all",
}

export const useFiltersStore = defineStore(STORE_NAME, {
  state: () => {
    return { filters: useLocalStorage(STORE_NAME, { ...no_filters }) }
  },
  actions: {
    clear() {
      Object.assign(this.filters, no_filters)
    },
  },
})
