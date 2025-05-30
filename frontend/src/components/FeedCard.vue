<script setup lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */

import { RouterLink } from "vue-router"
import { computed } from "vue"
import { secondsToString } from "./sts"
import { useAuthStore } from "../stores/auth.store"
import { fetch_wrapper } from "../utils"

// icons
const eye = "/res/icons/eye.svg"
const heartFill = "/res/icons/heart-fill.svg"
const eyeSlashFill = "/res/icons/eye-slash-fill.svg"

const auth = useAuthStore()

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number | undefined }

const props = defineProps<{
  feed: PatchedFeed
  clickable: boolean
}>()

const emit = defineEmits<{
  (e: "refresh_feed", feed_id: number): void
  (e: "updating", value: boolean): void
}>()

const currentRatingIconName = computed(() => {
  const rating = props.feed.my_rating
  if (rating === 5) {
    return heartFill
  } else if (rating === -5) {
    return eyeSlashFill
  }
  return eye // Default for normal/visible (0 or any other value)
})

const currentRatingTitle = computed(() => {
  const rating = props.feed.my_rating
  if (rating === 5) {
    return "Preferito"
  } else if (rating === -5) {
    return "Nascosto"
  }
  return "Normale"
})

async function cycleRatingState() {
  const currentRating = props.feed.my_rating
  let newRating: number

  // Cycle logic: Normal -> Favorite -> Hidden -> Normal
  if (currentRating === 5) {
    // Favorite -> Hidden
    newRating = -5
  } else if (currentRating === -5) {
    // Hidden -> Normal
    newRating = 0
  } else {
    // Normal (or any other state) -> Favorite
    newRating = 5
  }

  // Optimistically update local state for immediate UI feedback
  const originalRating = props.feed.my_rating // Store original rating for potential revert
  ;(props.feed as any).my_rating = newRating

  const payload = {
    feed: props.feed.id,
    rating: newRating,
  }

  emit("updating", true)

  try {
    const response = await fetch_wrapper("/api/user-feeds/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })

    if (response.ok) {
      alert(
        `Impostazione per la fonte ${props.feed.id} aggiornata; ci potrebbe volere fino ad un'ora affinché la modifica abbia effetto.`,
      )
    } else {
      // Revert optimistic update on failure
      ;(props.feed as any).my_rating = originalRating
      const errorData = await response.text()
      alert(`Errore di aggiornamento del rating: ${response.statusText} - ${errorData}`)
    }
  } catch (error) {
    // Revert optimistic update on failure
    ;(props.feed as any).my_rating = originalRating
    alert(`Errore di rete: ${error}`)
  } finally {
    emit("updating", false)
  }
}
</script>

<template>
  <div class="card mb-3" :id="'feed_' + feed.id" :class="feed.active ? '' : 'bg-dark-subtle'">
    <div class="row g-0">
      <div class="col-md-1 p-2 text-center align-center">
        <component
          :is="clickable ? 'router-link' : 'span'"
          class="text-decoration-none"
          :to="'/feed/' + feed.id"
          :title="clickable ? 'vai a tutti gli articoli di ' + feed.title : ''"
          :style="{ cursor: clickable ? 'pointer' : '' }"
        >
          <img width="100" :src="`${feed.image}`" class="img-fluid border" alt="feed logo" />
        </component>
      </div>
      <div class="col-md-11">
        <div class="card-body">
          <component
            :is="clickable ? 'router-link' : 'span'"
            class="text-decoration-none"
            :to="'/feed/' + feed.id"
            :title="clickable ? 'vai a tutti gli articoli di ' + feed.title : ''"
            :style="{ cursor: clickable ? 'pointer' : '' }"
          >
            <h5 class="card-title">{{ feed.title }} ({{ feed.article_count }} articoli)</h5>
            <span v-if="clickable" class="card-text text-decoration-underline">{{
              feed.homepage
            }}</span>
            <a v-else :href="feed.homepage" target="_blank">{{ feed.homepage }}</a>
          </component>

          <div
            class="btn-group position-absolute"
            role="group"
            aria-label="Azioni"
            style="top: 1em; right: 1em"
          >
            <RouterLink
              id="edit"
              class="btn btn-outline-danger"
              title="Modifica la fonte (funzione riservata agli utenti di staff)"
              role="button"
              type="button"
              :to="`../edit_feed/${feed.id}`"
              v-if="auth.user?.is_staff"
            >
              <img
                class="icon"
                src="~bootstrap-icons/icons/pencil.svg"
                alt="pencil icon"
                width="18"
                height="18"
              />
            </RouterLink>
            <button
              type="button"
              class="btn btn-outline-success"
              @click="cycleRatingState"
              :title="`Stato attuale: ${currentRatingTitle}. Clicca per cambiare.`"
            >
              <img
                class="icon"
                :src="currentRatingIconName"
                :alt="currentRatingTitle"
                width="18"
                height="18"
              />
            </button>
            <button
              type="button"
              class="btn btn-outline-primary"
              aria-label="Aggiorna la fonte"
              title="Aggiorna la fonte"
              @click="emit('refresh_feed', feed.id)"
            >
              <img
                class="icon"
                src="~bootstrap-icons/icons/arrow-clockwise.svg"
                alt="clockwise arrow icon"
                width="18"
                height="18"
              />
            </button>
          </div>
          <p class="card-text my-1">
            <span v-for="tag in feed.tags" :key="tag" class="badge text-bg-secondary m-1 p-2">
              {{ tag }}
            </span>
          </p>
          <p class="card-text" v-if="feed.last_polled_epoch">
            <small class="text-body-secondary">
              Ultimo aggiornamento
              {{ secondsToString(new Date().getTime() / 1000 - feed.last_polled_epoch) }}
            </small>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
