<template>
  <nav v-if="totalPages > 1" aria-label="Page navigation" class="mt-3">
    <ul class="pagination justify-content-center">
      <li class="page-item" :class="{ disabled: page === 1 }">
        <a class="page-link" href="#" @click.prevent="changePage(page - 1)">Previous</a>
      </li>
      <li
        v-for="p in pages"
        :key="p"
        class="page-item"
        :class="{ active: p === page, disabled: p === '...' }"
      >
        <a class="page-link" href="#" @click.prevent="changePage(p)">{{ p }}</a>
      </li>
      <li class="page-item" :class="{ disabled: page === totalPages }">
        <a class="page-link" href="#" @click.prevent="changePage(page + 1)">Next</a>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  count: number
  page: number
  itemsPerPage: number
}>()

const emit = defineEmits(["page-change"])

const totalPages = computed(() => Math.ceil(props.count / props.itemsPerPage))

const pages = computed(() => {
  const pages: (number | "...")[] = []
  const currentPage = props.page
  const lastPage = totalPages.value

  if (lastPage <= 7) {
    for (let i = 1; i <= lastPage; i++) {
      pages.push(i)
    }
    return pages
  }

  // Show first page
  pages.push(1)

  // Show window around current page
  let start = Math.max(2, currentPage - 1)
  let end = Math.min(lastPage - 1, currentPage + 1)

  if (currentPage > 3) {
    pages.push("...")
  }

  if (currentPage === lastPage) {
    start = Math.max(2, lastPage - 2)
  }
  if (currentPage === 1) {
    end = Math.min(lastPage - 1, 3)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  if (currentPage < lastPage - 2) {
    pages.push("...")
  }

  // Show last page
  pages.push(lastPage)

  return pages
})

function changePage(p: number | "...") {
  if (typeof p === "number" && p > 0 && p <= totalPages.value) {
    emit("page-change", p)
  }
}
</script>
