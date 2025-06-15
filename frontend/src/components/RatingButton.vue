<template>
  <button
    v-if="props.item"
    type="button"
    class="btn"
    :class="buttonClass"
    :title="title"
    :disabled="props.readonly"
    @click="setRating"
  >
    <svg
      v-if="props.type === 'positive'"
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      class="bi bi-star-fill"
      :class="iconClass"
      viewBox="0 0 16 16"
    >
      <path
        d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"
      />
    </svg>
    <svg
      v-else-if="props.type === 'negative'"
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      class="bi bi-hand-thumbs-down-fill"
      :class="iconClass"
      viewBox="0 0 16 16"
    >
      <path
        d="M6.956 14.534c.065.936.952 1.659 1.908 1.42l.261-.065a1.378 1.378 0 0 0 1.012-.965c.22-.816.533-2.512.062-4.51.136.02.285.037.443.051.713.065 1.669.071 2.516-.211.518-.173.994-.68 1.2-1.272a1.896 1.896 0 0 0-.234-1.734c.058-.118.103-.242.138-.368.077-.27.113-.568.113-.856 0-.29-.036-.586-.113-.857a2.094 2.094 0 0 0-.16-.403c.169-.387.107-.819-.003-1.14a.002.002 0 0 0-.002-.002L13.692 2.5c.099-.28.035-.595-.15-.816a.897.897 0 0 0-1.07-.24L10.32 2.01c-.311.1-.611.26-.862.488l-.057.045c-.055.041-.11.077-.163.108a.94.94 0 0 1-.21.094l-.006.002L6.957 4.03c-.589.44-.758 1.245-.52 1.863l.003.007a.498.498 0 0 0 .47.33H8.5a.5.5 0 0 1 .5.5v1.226c0 .276-.224.5-.5.5H5.707l-.002-.001L4.23 10.124a.498.498 0 0 0-.47-.33H1.5a.5.5 0 0 1-.5-.5V8.025a.5.5 0 0 1 .5-.5H3.88l.07-.006.028-.002a.5.5 0 0 0 .44-.263l.01-.017.018-.032.005-.009.002-.004.002-.003c.038-.075.096-.206.096-.43 0-.224-.058-.355-.096-.43l-.003-.004a1.49 1.49 0 0 0-.13-.149l-.195-.164-.02-.017c-.07-.055-.11-.08-.11-.08a2.496 2.496 0 0 0-.227-.19c-.23-.17-.43-.28-.59-.33-.31-.1-.65-.12-.95-.05H2.5a.5.5 0 0 1-.5-.5V4.7a.5.5 0 0 1 .5-.5h.25C3.12 4.2 3.5 4.03 4 3.83V2.5a.5.5 0 0 1 .5-.5h1.362c.305-.005.607.02.91.07l.006.001c.315.05.622.13.92.23l.03.01c.27.09.52.23.75.4l.07.05.02.015c.03.02.06.04.09.06l2.12 1.69c.06.045.09.07.09.07.07.055.11.08.11.08.16.12.29.29.39.49.08.15.14.33.15.51h.001L13 5.21V6.5a.5.5 0 0 1-.5.5h-1.362c-.305.005-.607-.02-.91-.07l-.006-.001c-.315-.05-.622-.13-.92-.23l-.03-.01c-.27-.09-.52-.23-.75-.4l-.07-.05-.02-.015a.502.502 0 0 0-.09-.06L6.88 4.31a.5.5 0 0 0-.44.263l-.01-.017-.018-.032-.005-.009-.002-.004-.002-.003c-.038-.075-.096-.206-.096-.43 0-.224.058-.355.096-.43l.003.004.018.028.06.055.196.164.02.017c.07.055.11.08.11.08.16.12.29.29.39.49.08.15.14.33.15.51h.001L6 8.21V9.5a.5.5 0 0 1-.5.5H4.138l-.002.001L2.667 7.876a.498.498 0 0 0-.47-.33H.5a.5.5 0 0 1-.5-.5V6.275a.5.5 0 0 1 .5-.5H2.38l.07-.006.028-.002a.5.5 0 0 0 .44-.263l.01-.017.018-.032.005-.009.002-.004.002-.003c.038-.075-.096-.206-.096-.43 0-.224-.058-.355-.096-.43l-.003-.004a1.49 1.49 0 0 0-.13-.149l-.195-.164-.02-.017c-.07-.055-.11-.08-.11-.08a2.496 2.496 0 0 0-.227-.19c-.23-.17-.43-.28-.59-.33-.31-.1-.65-.12-.95-.05H.5a.5.5 0 0 1-.5-.5V2.7a.5.5 0 0 1 .5-.5h.25c.37 0 .74-.17 1.19-.37V1a.5.5 0 0 1 .5-.5h1.362c.305-.005.607.02.91.07l.006.001c.315.05.622.13.92.23l.03.01.002.001z"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { fetch_wrapper } from "../utils";
import { toast } from "vue3-toastify";
import type { components } from "../generated/schema.d.ts"; // For PatchedFeed type

// Define PatchedFeed based on schema.d.ts, assuming Feed is a defined type there
// and my_rating is the property we expect.
type Feed = components["schemas"]["Feed"];
interface PatchedFeed extends Feed {
  my_rating?: number; // Or number | undefined, matching original components
}

const props = defineProps<{
  type: "positive" | "negative";
  item: PatchedFeed;
  threshold: number;
  endpoint: string;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  (e: "rated"): void;
  (e: "updating", status: boolean): void;
}>();

const buttonClass = computed(() => {
  return props.type === "positive" ? "btn-outline-success" : "btn-outline-danger";
});

const iconClass = computed(() => {
  const currentRating = props.item.my_rating || 0;
  if (props.type === "positive") {
    return currentRating > props.threshold ? "icon-success" : "icon-light";
  } else { // negative
    return currentRating < props.threshold ? "icon-danger" : "icon-light";
  }
});

const title = computed(() => {
  if (props.type === "positive") {
    return `Dai ${props.threshold + 1} voti positivi`;
  } else { // negative
    return `Dai ${1 - props.threshold} voti negativi`;
  }
});

async function setRating() {
  if (!props.item || !props.item.id) {
    console.error("Item or item.id is undefined", props.item);
    return;
  }
  emit("updating", true);

  const currentRating = props.item.my_rating || 0;
  let targetRating: number;
  let newRating: number;

  if (props.type === "positive") {
    targetRating = props.threshold + 1;
    newRating = currentRating === targetRating ? 0 : targetRating;
  } else { // negative
    targetRating = props.threshold - 1;
    newRating = currentRating === targetRating ? 0 : targetRating;
  }

  // Local update for immediate reactivity (matches original behavior)
  // This does mutate the prop, which is generally discouraged but was in the original.
  // If this is not desired, this line should be removed and parent should handle update.
  props.item.my_rating = newRating;

  try {
    const response = await fetch_wrapper(props.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feed: props.item.id, rating: newRating }),
    });

    if (response.status === 201) {
      toast("Rating inserito con successo", { type: "success" });
      emit("rated");
    } else if (response.status === 200) {
      toast("Rating aggiornato con successo", { type: "success" });
      emit("rated");
    } else if (response.status === 403) {
      if (typeof window !== 'undefined' && window.location) {
        window.location.href = '/accounts/';
      }
    } else {
      const errorData = await response.json().catch(() => ({})); // Try to parse error, default to empty obj
      const errorDetail = errorData.detail || response.statusText;
      toast(`Errore HTTP nell'aggiornamento del rating: ${errorDetail}`, { type: "error" });
    }
  } catch (error) {
    toast(`Eccezione nell'aggiornamento del rating: ${error}`, { type: "error" });
    // If local mutation occurred, consider reverting it here or ensuring parent re-fetches
    // For now, matching original behavior where local optimistic update remains.
  } finally {
    emit("updating", false);
  }
}
</script>

<style scoped>
.icon-danger {
  color: red;
}
.icon-success {
  color: green;
}
.icon-light {
  color: lightgray;
}
</style>
