import { defineStore } from 'pinia'

const TABS_STORAGE_KEY = 'activeTab'

export const useTabsStore = defineStore('tabs', {
  state: () => ({
    activeTab: localStorage.getItem(TABS_STORAGE_KEY) || 'Tutti',
  }),
  actions: {
    setActiveTab(tabName: string) {
      this.activeTab = tabName
    },
  },
})

// Subscribe to store changes to persist activeTab to localStorage
// This needs to be done after the store is defined and used by a component,
// so we'll handle this part when integrating with HomeView.vue or in main.ts
// For now, let's ensure the basic store is set up.

// A more direct way to handle persistence within the store setup if Pinia version supports it,
// or by using a plugin. For simplicity, we'll initially try a direct subscription.

// Update: Pinia's $subscribe method is suitable here.
// We need to ensure this code runs after the store instance is created.
// A common pattern is to call this subscription logic in main.ts or when the app initializes.
// However, let's try to include it directly in the store definition for encapsulation.

export function initTabsStore() {
  const tabsStore = useTabsStore();
  tabsStore.$subscribe((mutation, state) => {
    localStorage.setItem(TABS_STORAGE_KEY, state.activeTab);
  });
  // Ensure the initial value from localStorage (or default) is set.
  // This is already handled by the state initializer.
  // If the value in localStorage is null, it defaults to 'Tutti'.
  // If we want to explicitly save it back if it was null, we can do:
  if (localStorage.getItem(TABS_STORAGE_KEY) === null) {
    localStorage.setItem(TABS_STORAGE_KEY, tabsStore.activeTab);
  }
}
