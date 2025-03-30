import { defineStore } from "pinia"
import { useLocalStorage } from "@vueuse/core"
import type { Profile } from "../types/Profile"

const STORE_NAME = "profile"

const MAX_FONT_SIZE = 24
const MIN_FONT_SIZE = 12

const default_profile: Profile = {
  mastodon_server: "",
  font_size: 16,
}

export const useProfileStore = defineStore(STORE_NAME, {
  state: () => {
    return { profile: useLocalStorage(STORE_NAME, { ...default_profile }) }
  },
  actions: {
    set_mastodon_server(mastodon_server: string) {
      this.profile.mastodon_server = mastodon_server
    },
    enlarge_font_size() {
      if (this.profile.font_size < MAX_FONT_SIZE) {
        this.profile.font_size += 1
        this.set_font_size()
      }
    },
    reset_font_size() {
      this.profile.font_size = default_profile.font_size
      this.set_font_size()
    },
    reduce_font_size() {
      if (this.profile.font_size > MIN_FONT_SIZE) {
        this.profile.font_size -= 1
        this.set_font_size()
      }
    },
    set_font_size(): void {
      const font_size = Math.round(this.profile.font_size)
      const html = document.querySelector("html")
      if (html && font_size <= MAX_FONT_SIZE && font_size >= MIN_FONT_SIZE) {
        html.style.fontSize = `${font_size}px`
      }
    },
  },
})
