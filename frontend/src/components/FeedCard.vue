<script setup lang="ts">
import { RouterLink } from "vue-router"
import { computed } from "vue";
import { secondsToString } from "./sts"
import { useAuthStore } from "../stores/auth.store"
import ThreeStateCheckBox from "./ThreeStateCheckBox.vue";
import type { CheckBoxValue } from "../types/CheckBoxValue";
import { fetch_wrapper } from "../utils";

const auth = useAuthStore()

import type { components } from "../generated/schema.d.ts"
type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { my_rating: number | undefined }

defineProps<{
  feed: PatchedFeed
  clickable: boolean
}>()

const emit = defineEmits<{
  (e: "refresh_feed", feed_id: number): void
  (e: "updating", value: boolean): void
}>()

const showHideState = computed<CheckBoxValue>(() => {
  const rating = props.feed.my_rating;
  if (rating === undefined || rating === null) {
    return null; // Indeterminate
  }
  if (rating >= -4 && rating <= 5) {
    return true; // Checked (Show)
  }
  if (rating === -5) {
    return false; // Unchecked (Don't show)
  }
  return null; // Default to indeterminate for any other unexpected values
});

async function handleShowHideChange(newState: CheckBoxValue) {
  let newRating: number;
  if (newState === true) {
    newRating = 0; // Default "show" rating
  } else if (newState === false) {
    newRating = -5; // "Don't show" rating
  } else { // newState === null (cycled from false to null)
    newRating = 0; // Treat as "show"
  }

  // Optimistically update local state for immediate UI feedback
  const originalRating = props.feed.my_rating; // Store original rating for potential revert
  (props.feed as any).my_rating = newRating;


  const payload = {
    feed: props.feed.id, 
    rating: newRating,
  };

  emit('updating', true);

  try {
    const response = await fetch_wrapper("/api/user-feeds/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      console.log("Visibility updated successfully.");
    } else {
      // Revert optimistic update on failure
      (props.feed as any).my_rating = originalRating;
      const errorData = await response.text();
      alert(`Error updating visibility: ${response.statusText} - ${errorData}`);
    }
  } catch (error) {
    // Revert optimistic update on failure
    (props.feed as any).my_rating = originalRating;
    alert(`Network error: ${error}`);
  } finally {
    emit('updating', false); 
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
            <ThreeStateCheckBox
              class="float-end mb-2"
              :value="showHideState"
              @change="handleShowHideChange"
              title="Toggle visibility"
            />
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
