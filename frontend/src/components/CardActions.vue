<script setup lang="ts">
import type { components } from "../generated/schema.d.ts"

type Article = components["schemas"]["ArticleSerializerFull"]

const props = defineProps<{
  article: Article
  index: number
}>()

const emit = defineEmits<{
  (e: "marked", id: number, to_read: boolean): void
  (e: "rating", index: number, item: Article): void
  (e: "dismissed", id: number, dismissed: boolean): void
}>()

function toggle_to_read() {
  const n = props.article
  console.log(`set to_read for ${n.id} to ${!n.to_read}`)
  const selectedElement = document.getElementById(`selected_${n.id}`)
  if (selectedElement !== null) {
    selectedElement.setAttribute("disabled", "disabled")
  }
  const dataTo = { to_read: !n.to_read }
  fetch(`/api/articles/${n.id}`, {
    method: "POST",
    body: JSON.stringify(dataTo),
  }).then((response) => {
    if (!response.ok) {
      // toast error
    } else {
      n.to_read = !n.to_read
      emit("marked", n.id, n.to_read)
      if (selectedElement !== null) {
        selectedElement.removeAttribute("disabled")
      }
    }
  })
}

function rate(index: number, item: Article): void {
  emit("rating", index, item)
}

const toggle_dismiss = () => {
  const n = props.article
  const dataTo = { dismissed: !n.dismissed }
  fetch(`/api/articles/${n.id}`, {
    method: "POST",
    body: JSON.stringify(dataTo),
  }).then((response) => {
    if (!response.ok) {
      // toast error
    } else {
      n.dismissed = !n.dismissed
      emit("dismissed", n.id, n.dismissed)
    }
  })
}
</script>

<template>
  <div
    class="btn-toolbar float-start"
    role="toolbar"
    aria-label="Toolbar with button groups"
  >
    <div class="btn-group me-2" role="group" aria-label="First group">
      <button
        type="button"
        class="btn btn-outline-primary btn-sm"
        :title="
          article.dismissed
            ? 'non nascondere l\'articolo'
            : 'nascondi l\'articolo'
        "
        @click="toggle_dismiss()"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/trash3.svg"
          :class="{
            'dimmed-icon': !article.dismissed,
          }"
          alt="trash icon"
          width="18"
          height="18"
        />
      </button>
      <button
        :id="`selected_${article.id}`"
        type="button"
        class="btn btn-outline-primary btn-sm"
        :title="
          article.to_read
            ? 'togli dall\'elenco di articoli da leggere dopo'
            : 'salva per leggere dopo'
        "
        @click="toggle_to_read()"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/heart-fill.svg"
          :class="{
            'dimmed-icon': !article.to_read,
          }"
          alt="fav icon"
          width="18"
          height="18"
        />
      </button>
      <button
        type="button"
        class="btn btn-outline-primary btn-sm"
        :class="{
          'icon-danger': article.my_rating < 0,
          'icon-light': article.my_rating == 0,
          'icon-success': article.my_rating > 0,
        }"
        :title="
          article.my_rating === 0
            ? 'valuta l\'articolo'
            : 'cambia la tua valutazione'
        "
        @click="rate(index, article)"
      >
        <img
          class="icon"
          :class="{
            'dimmed-icon': article.my_rating === 0,
            'red-icon': article.my_rating < 0,
            'green-icon': article.my_rating > 0,
          }"
          :style="{
            transform: `rotate(${(article.my_rating < 0 ? 0 : 180) + 'deg'}`,
          }"
          src="~bootstrap-icons/icons/hand-thumbs-down-fill.svg"
          alt="rate icon"
          width="18"
          height="18"
        />
      </button>
    </div>
  </div>
</template>
<style>
.inverted-icon {
  filter: invert(1);
}
.dimmed-icon {
  filter: invert(0.7);
}
button:hover .icon {
  filter: invert(1);
}
.green-icon {
  filter: invert(0.4) sepia(1) hue-rotate(90deg);
}
.red-icon {
  filter: invert(0.5) sepia(1) hue-rotate(300deg);
}
</style>
