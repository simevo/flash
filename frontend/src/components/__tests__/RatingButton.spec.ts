import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { toast } from "vue3-toastify"
import { mount, VueWrapper } from "@vue/test-utils"
import RatingButton from "../RatingButton.vue" // New component
import axios from "axios" // RatingButton uses axios
import type { components } from "../../generated/schema.d.ts"

type Feed = components["schemas"]["Feed"]
type PatchedFeed = Feed & { rating: number | undefined } // Renamed my_rating to rating to match component

// Mock axios
vi.mock("axios")

// Mock vue3-toastify
vi.mock("vue3-toastify", () => ({ toast: vi.fn() }))

describe("RatingButton.vue", () => {
  let wrapper: VueWrapper<InstanceType<typeof RatingButton>>
  const mockItemBase: PatchedFeed = {
    id: 1,
    title: "Test Feed",
    rating: 0, // Use 'rating' to match RatingButton's prop expectation
    homepage: "https://example.com",
    url: "https://example.com/feed",
    language: "en",
    image: "",
  }
  const mockEndpoint = "/api/rate_feed/"

  beforeEach(() => {
    vi.clearAllMocks()
    // Default mock implementation for axios.post
    ;(axios.post as ReturnType<typeof vi.fn>).mockResolvedValue({
      // Simulate a successful API call
    })
  })

  afterEach(() => {
    if (wrapper && wrapper.exists()) {
      wrapper.unmount()
    }
  })

  // Helper function to create the component
  const createComponent = (
    props: {
      type: "positive" | "negative"
      item: PatchedFeed
      threshold: number
      endpoint: string
      readonly?: boolean
    },
  ) => {
    return mount(RatingButton, {
      props: {
        readonly: false,
        ...props,
      },
    })
  }

  describe.each([
    { type: "positive", initialRating: 0, threshold: 0 },
    { type: "negative", initialRating: 0, threshold: 0 },
    { type: "positive", initialRating: 2, threshold: 1 }, // Already rated positive
    { type: "negative", initialRating: -2, threshold: -1 }, // Already rated negative
  ])("Common Behavior for type: $type", ({ type, initialRating, threshold }) => {
    const specificMockItem = { ...mockItemBase, rating: initialRating }

    it("renders the button", () => {
      wrapper = createComponent({ type, item: specificMockItem, threshold, endpoint: mockEndpoint })
      expect(wrapper.find("button").exists()).toBe(true)
    })

    it("is disabled when readonly is true", async () => {
      wrapper = createComponent({ type, item: specificMockItem, threshold, endpoint: mockEndpoint, readonly: true })
      expect(wrapper.find("button").attributes("disabled")).toBeDefined()
      await wrapper.find("button").trigger("click")
      expect(axios.post).not.toHaveBeenCalled()
      expect(wrapper.emitted("rated")).toBeUndefined()
    })

    it("is not disabled when readonly is false", () => {
      wrapper = createComponent({ type, item: specificMockItem, threshold, endpoint: mockEndpoint, readonly: false })
      expect(wrapper.find("button").attributes("disabled")).toBeUndefined()
    })

    it("emits 'rated' on successful API call", async () => {
      wrapper = createComponent({ type, item: { ...specificMockItem }, threshold, endpoint: mockEndpoint })
      await wrapper.find("button").trigger("click")
      expect(axios.post).toHaveBeenCalled()
      // Check if 'rated' event was emitted. axios.post is mocked to resolve successfully.
      expect(wrapper.emitted("rated")).toBeTruthy()
      expect(wrapper.emitted("rated")?.length).toBe(1)
    })

    it("does not emit 'rated' on API error", async () => {
      (axios.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("API Error"));
      wrapper = createComponent({ type, item: { ...specificMockItem }, threshold, endpoint: mockEndpoint })
      try {
        await wrapper.find("button").trigger("click")
      } catch (e) {
        // Expected
      }
      expect(axios.post).toHaveBeenCalled()
      expect(wrapper.emitted("rated")).toBeUndefined()
      // console.error is expected due to the catch block in the component
      // expect(console.error).toHaveBeenCalled(); // This needs console to be spied on
    })
  })

  describe("Positive Type Specifics", () => {
    const type = "positive"

    it("displays correct class and title for positive type", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 0 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find("button").classes()).toContain("btn-outline-success")
      expect(wrapper.find("button").attributes("title")).toBe("Rate up (threshold: 0)")
    })

    it("applies icon-success when rating > threshold", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 1 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-star-fill").classes()).toContain("icon-success")
    })

    it("applies icon-light when rating <= threshold", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 0 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-star-fill").classes()).toContain("icon-light")
      wrapper.unmount()
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: -1 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-star-fill").classes()).toContain("icon-light")
    })

    it("sets rating to threshold + 1 on click if current rating < threshold + 1", async () => {
      const item = { ...mockItemBase, rating: 0 }
      const threshold = 0
      wrapper = createComponent({ type, item, threshold, endpoint: mockEndpoint })
      await wrapper.find("button").trigger("click")
      expect(axios.post).toHaveBeenCalledWith(mockEndpoint, { rating: threshold + 1 })
      expect(wrapper.emitted("rated")).toBeTruthy()
    })

    it("sets rating to 0 on click if current rating >= threshold + 1", async () => {
      const item = { ...mockItemBase, rating: 1 } // Already rated above threshold
      const threshold = 0
      wrapper = createComponent({ type, item, threshold, endpoint: mockEndpoint })
      await wrapper.find("button").trigger("click")
      expect(axios.post).toHaveBeenCalledWith(mockEndpoint, { rating: 0 })
      expect(wrapper.emitted("rated")).toBeTruthy()
    })
  })

  describe("Negative Type Specifics", () => {
    const type = "negative"

    it("displays correct class and title for negative type", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 0 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find("button").classes()).toContain("btn-outline-danger")
      expect(wrapper.find("button").attributes("title")).toBe("Rate down (threshold: 0)")
    })

    it("applies icon-danger when rating < threshold", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: -1 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-hand-thumbs-down-fill").classes()).toContain("icon-danger")
    })

    it("applies icon-light when rating >= threshold", () => {
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 0 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-hand-thumbs-down-fill").classes()).toContain("icon-light")
      wrapper.unmount()
      wrapper = createComponent({ type, item: { ...mockItemBase, rating: 1 }, threshold: 0, endpoint: mockEndpoint })
      expect(wrapper.find(".bi-hand-thumbs-down-fill").classes()).toContain("icon-light")
    })

    it("sets rating to threshold - 1 on click if current rating > threshold -1", async () => {
      const item = { ...mockItemBase, rating: 0 }
      const threshold = 0
      wrapper = createComponent({ type, item, threshold, endpoint: mockEndpoint })
      await wrapper.find("button").trigger("click")
      expect(axios.post).toHaveBeenCalledWith(mockEndpoint, { rating: threshold - 1 })
      expect(wrapper.emitted("rated")).toBeTruthy()
    })

    it("sets rating to 0 on click if current rating <= threshold -1", async () => {
      const item = { ...mockItemBase, rating: -1 } // Already rated below threshold
      const threshold = 0
      wrapper = createComponent({ type, item, threshold, endpoint: mockEndpoint })
      await wrapper.find("button").trigger("click")
      expect(axios.post).toHaveBeenCalledWith(mockEndpoint, { rating: 0 })
      expect(wrapper.emitted("rated")).toBeTruthy()
    })
  })
})
