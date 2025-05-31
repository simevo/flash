<script setup lang="ts">
import { defineAsyncComponent } from "vue"
import { useTabsStore } from '../stores/tabs.store' // Import the store
import { storeToRefs } from 'pinia'

import { fetch_wrapper } from "../utils"
import {
  computed,
  onActivated,
  onDeactivated,
  onMounted,
  onUnmounted,
  ref,
  type Ref,
  shallowRef,
} from "vue"
import type { components } from "../generated/schema.d.ts"

// Define lazy-loaded components
const ListAll = defineAsyncComponent(() => import("../components/ListAll.vue"))
const ListRead = defineAsyncComponent(() => import("../components/ListRead.vue"))
const ListForyou = defineAsyncComponent(() => import("../components/ListForyou.vue"))
const ListFavs = defineAsyncComponent(() => import("../components/ListFavs.vue"))

type FeedSerializerSimple = components["schemas"]["FeedSerializerSimple"]

// --- Common Data ---
const ready = ref(false)
const feeds: Ref<FeedSerializerSimple[]> = ref([]) // All feeds, potentially used by multiple tabs

// --- Tab Management ---
type Tabs = "Tutti" | "Letti" | "Per te" | "Preferiti"
const tabs = {
  Tutti: ListAll,
  Letti: ListRead,
  "Per te": ListForyou,
  Preferiti: ListFavs,
}

// Use Pinia store for active tab
const tabsStore = useTabsStore()
const { activeTab: storeActiveTab } = storeToRefs(tabsStore) // Get reactive state

const currentTab = shallowRef() // Will be set based on store's activeTab
const currentTabName: Ref<Tabs> = ref(storeActiveTab.value as Tabs) // Initialize with store's value

// --- Fetching Functions ---

async function fetchFeeds() {
  ready.value = false
  const response = await fetch_wrapper(`../../api/feeds/simple/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: FeedSerializerSimple[] = await response.json()
    feeds.value = data
  }
  ready.value = true
}

const feed_dict = computed(() => {
  const dict: { [key: number]: FeedSerializerSimple } = {}
  feeds.value.forEach((feed) => {
    dict[feed.id] = feed
  })
  return dict
})

async function activateTab(tab: Tabs) {
  tabsStore.setActiveTab(tab) // Update store
  currentTabName.value = tab
  currentTab.value = tabs[tab]
}

onMounted(async () => {
  console.log("HomeView mounted")
  // Initialize tab from store
  // The component's currentTabName is already initialized from storeActiveTab.value
  // We need to ensure currentTab (the component instance) is also set.
  currentTab.value = tabs[storeActiveTab.value as Tabs]

  // It's important that initTabsStore() from tabs.store.ts is called.
  // This could be done in main.ts, App.vue, or here.
  // For now, let's assume it will be called in main.ts as per the plan.
  // If not, it should be called here:
  // import { initTabsStore } from '../stores/tabs.store';
  // initTabsStore();


  fetchFeeds()
})

onUnmounted(() => {
  console.log("HomeView unmounted")
})

onActivated(() => {
  console.log("HomeView activated")
})

onDeactivated(() => {
  console.log("HomeView deactivated")
})
</script>

<template>
  <div class="container-fluid mt-3">
    <ul class="nav nav-tabs mb-3" id="homeTab" role="tablist">
      <li class="nav-item" role="presentation" v-for="tabKey in Object.keys(tabs)" :key="tabKey">
        <button
          class="nav-link"
          :class="{ active: currentTabName === tabKey }"
          :id="`${tabKey}-tab`"
          type="button"
          role="tab"
          :aria-controls="`${tabKey}-pane`"
          :aria-selected="currentTabName === tabKey"
          @click="activateTab(tabKey as Tabs)"
        >
          {{ tabKey }}
        </button>
      </li>
    </ul>
    <div class="tab-content" id="tabContent">
      <div
        class="tab-pane fade show active"
        id="pane"
        role="tabpanel"
        aria-labelledby="tab"
        tabindex="0"
      >
        <KeepAlive>
          <component :is="currentTab" :feeds="feeds" :feed_dict="feed_dict" />
        </KeepAlive>
      </div>
    </div>
  </div>
</template>

<style>
.wrapper {
  display: grid;
  margin: 0 auto;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-auto-rows: minmax(150px, auto);
}

/* Style to make the filter button less obtrusive with tabs */
.btn-primary[style*="position: fixed"] {
  top: 6rem; /* Adjust based on your navbar height if any */
  left: 1rem;
}
</style>
