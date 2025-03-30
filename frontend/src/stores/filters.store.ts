import { defineStore } from "pinia"
import { useLocalStorage } from "@vueuse/core"

import type { Filters, FeedCount } from "../types/Filters"
import type { CheckBoxValue } from "../types/CheckBoxValue"

const STORE_NAME = "filters"

const no_filters: Filters = {
  what: "",
  when: "all",
  language: "all",
  length: "all",
  feed_ids: [-1],
}

export const useFiltersStore = defineStore(STORE_NAME, {
  state: () => {
    return { filters: useLocalStorage(STORE_NAME, { ...no_filters }) }
  },
  actions: {
    clear() {
      Object.assign(this.filters, no_filters)
    },
    toggle_all_feeds(value: CheckBoxValue, feed_counts: FeedCount[]) {
      if (value === null) {
        const feed_ids = this.filters.feed_ids.slice()
        this.filters.feed_ids = []
        feed_counts.forEach((feed) => {
          if (!feed_ids.includes(feed.feed_id)) {
            this.filters.feed_ids.push(feed.feed_id)
          }
        })
        return
      }
      if (value === true) {
        this.filters.feed_ids.push(-1)
        return
      } else {
        const index = this.filters.feed_ids.indexOf(-1)
        if (this.filters.feed_ids.length === 1) {
          this.filters.feed_ids = []
          feed_counts.forEach((feed) => this.filters.feed_ids.push(feed.feed_id))
        } else {
          this.filters.feed_ids.splice(index, 1)
        }
      }
    },
    toggle_feed(feed_id: number) {
      const index = this.filters.feed_ids.indexOf(feed_id)
      if (index === -1) {
        this.filters.feed_ids.push(feed_id)
      } else {
        this.filters.feed_ids.splice(index, 1)
      }
    },
  },
})
