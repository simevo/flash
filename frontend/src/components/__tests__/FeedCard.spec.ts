/* eslint-disable @typescript-eslint/no-explicit-any */

import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { createRouter, createMemoryHistory } from "vue-router"
import FeedCard from "../FeedCard.vue"
import { useAuthStore } from "../../stores/auth.store" // Adjusted path

// Mock fetch_wrapper
vi.mock("../../utils", () => ({
  fetch_wrapper: vi.fn(),
}))

// Mock auth store
vi.mock("../../stores/auth.store", () => ({
  useAuthStore: vi.fn(() => ({
    user: { is_staff: false }, // Default mock user
  })),
}))

// Helper function to create a mock feed
const createMockFeed = (
  id: number,
  my_rating: number | undefined,
  last_polled_epoch: number | null = Date.now() / 1000,
) => ({
  id,
  title: `Feed ${id}`,
  url: `http://example.com/feed${id}`,
  homepage: `http://example.com/${id}`,
  image: `http://example.com/image${id}.png`,
  article_count: 10,
  last_polled_epoch,
  my_rating,
  tags: ["tag1", "tag2"],
  active: true,
  language: "en",
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: "/", component: { template: "<div>Home</div>" } },
    // Route for the edit feed page, as used in FeedCard's RouterLink
    { path: "/edit_feed/:id", name: "edit_feed", component: { template: "<div>Edit Feed</div>" } },
  ],
})

describe("FeedCard.vue", () => {
  let mockAuthStore: any

  beforeEach(async () => {
    // Reset mocks before each test
    vi.clearAllMocks()
    // Default mock user for most tests
    mockAuthStore = useAuthStore as any
    mockAuthStore.mockReturnValue({ user: { is_staff: false } })

    // It's good practice to push a default route to the router before each test
    // that uses it, to ensure a consistent starting point.
    await router.push("/")
    await router.isReady()
  })

  describe("Rendering", () => {
    it("should NOT render RatingToolbar", () => {
      const feed = createMockFeed(1, 0)
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: {
            RouterLink: true, // Stub RouterLink for simplicity
          },
        },
      })
      // Assuming RatingToolbar had a specific class or ID
      expect(wrapper.findComponent({ name: "RatingToolbar" }).exists()).toBe(false)
      expect(wrapper.find(".rating-toolbar-class").exists()).toBe(false) // Example class
    })

    it("renders edit button if user is staff", async () => {
      // Ensure the auth store mock is correctly updated for this specific test
      ;(useAuthStore as any).mockReturnValue({ user: { is_staff: true } })
      const feed = createMockFeed(1, 0)
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          plugins: [router], // Add the router plugin
          // Do not stub RouterLink here to allow it to work with the router
        },
      })
      // Wait for any potential navigation or async updates triggered by router
      await flushPromises()
      expect(wrapper.find("#edit").exists()).toBe(true)
    })

    it("does NOT render edit button if user is not staff", async () => {
      // Ensure the auth store mock is correctly updated for this specific test
      ;(useAuthStore as any).mockReturnValue({ user: { is_staff: false } })
      const feed = createMockFeed(1, 0)
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          plugins: [router], // Add the router plugin
          stubs: {
            // If RouterLink is used elsewhere and not for the edit button,
            // you might still need to stub it globally or locally for other tests.
            // For this specific test, not stubbing RouterLink is important for the edit button.
          },
        },
      })
      // Wait for any potential navigation or async updates triggered by router
      await flushPromises()
      expect(wrapper.find("#edit").exists()).toBe(false)
    })
  })

  describe("Refresh button", () => {
    it('emits "refresh_feed" with feed id when refresh button is clicked', async () => {
      const feed = createMockFeed(42, 0)
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true, ThreeStateCheckBox: true },
        },
      })

      const refreshButton = wrapper.find('button[aria-label="Aggiorna la fonte"]')
      expect(refreshButton.exists()).toBe(true)

      await refreshButton.trigger("click")

      expect(wrapper.emitted().refresh_feed).toBeTruthy()
      expect(wrapper.emitted().refresh_feed![0]).toEqual([feed.id])
    })
  })
})
