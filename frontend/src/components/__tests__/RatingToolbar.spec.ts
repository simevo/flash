import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import RatingToolbar from '../RatingToolbar.vue'
import { defineComponent } from 'vue'

// Define simple stubs for the child components
const NegativeRatingStub = defineComponent({
  name: 'NegativeRating',
  props: ['item', 'endpoint', 'threshold', 'readonly'],
  emits: ['updating'],
  template: '<button class="negative-rating-stub"></button>',
})

const PositiveRatingStub = defineComponent({
  name: 'PositiveRating',
  props: ['item', 'endpoint', 'threshold', 'readonly'],
  emits: ['updating'],
  template: '<button class="positive-rating-stub"></button>',
})

type PatchedFeed = {
  id: number
  title?: string
  my_rating?: number | undefined
}

describe('RatingToolbar.vue', () => {
  let wrapper: VueWrapper<any>
  const mockItem: PatchedFeed = { id: 1, my_rating: 0 }
  const mockEndpoint = '/api/rate_item/'

  const negativeThresholds = [-4, -3, -2, -1, 0]
  const positiveThresholds = [0, 1, 2, 3, 4]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createComponent = (props?: any) => {
    return mount(RatingToolbar, {
      props: {
        item: mockItem,
        endpoint: mockEndpoint,
        ...props,
      },
      global: {
        stubs: {
          NegativeRating: NegativeRatingStub,
          PositiveRating: PositiveRatingStub,
        },
      },
    })
  }

  describe('Rendering Child Components', () => {
    it('renders the correct number of NegativeRating and PositiveRating instances', () => {
      wrapper = createComponent()
      const negativeRatings = wrapper.findAllComponents(NegativeRatingStub)
      const positiveRatings = wrapper.findAllComponents(PositiveRatingStub)

      expect(negativeRatings.length).toBe(negativeThresholds.length)
      expect(positiveRatings.length).toBe(positiveThresholds.length)
    })
  })

  describe('Props Propagation', () => {
    beforeEach(() => {
      wrapper = createComponent()
    })

    it('passes correct props to NegativeRating instances', () => {
      const negativeRatings = wrapper.findAllComponents(NegativeRatingStub)
      negativeRatings.forEach((stubWrapper, index) => {
        expect(stubWrapper.props('item')).toEqual(mockItem)
        expect(stubWrapper.props('endpoint')).toBe(mockEndpoint)
        expect(stubWrapper.props('threshold')).toBe(negativeThresholds[index])
        expect(stubWrapper.props('readonly')).toBe(false) // Initial state
      })
    })

    it('passes correct props to PositiveRating instances', () => {
      const positiveRatings = wrapper.findAllComponents(PositiveRatingStub)
      positiveRatings.forEach((stubWrapper, index) => {
        expect(stubWrapper.props('item')).toEqual(mockItem)
        expect(stubWrapper.props('endpoint')).toBe(mockEndpoint)
        // PositiveRating thresholds in template are [0, 1, 2, 3, 4]
        // The component iterates `threshold in [0, 1, 2, 3, 4]`, so this is correct.
        expect(stubWrapper.props('threshold')).toBe(positiveThresholds[index])
        expect(stubWrapper.props('readonly')).toBe(false) // Initial state
      })
    })
  })

  describe('`updating` State Management', () => {
    beforeEach(() => {
      wrapper = createComponent()
    })

    it('sets readonly to true on all children when one emits updating(true)', async () => {
      const negativeRatings = wrapper.findAllComponents(NegativeRatingStub)
      const positiveRatings = wrapper.findAllComponents(PositiveRatingStub)

      // Simulate event from the first negative rating child
      await negativeRatings[0].vm.$emit('updating', true)

      negativeRatings.forEach((stubWrapper) => {
        expect(stubWrapper.props('readonly')).toBe(true)
      })
      positiveRatings.forEach((stubWrapper) => {
        expect(stubWrapper.props('readonly')).toBe(true)
      })
    })

    it('sets readonly to false on all children when one emits updating(false) after being true', async () => {
      const negativeRatings = wrapper.findAllComponents(NegativeRatingStub)
      const positiveRatings = wrapper.findAllComponents(PositiveRatingStub)

      // First, set to true
      await negativeRatings[0].vm.$emit('updating', true)
      negativeRatings.forEach((stubWrapper) => expect(stubWrapper.props('readonly')).toBe(true))
      positiveRatings.forEach((stubWrapper) => expect(stubWrapper.props('readonly')).toBe(true))

      // Then, set back to false
      await negativeRatings[0].vm.$emit('updating', false)

      negativeRatings.forEach((stubWrapper) => {
        expect(stubWrapper.props('readonly')).toBe(false)
      })
      positiveRatings.forEach((stubWrapper) => {
        expect(stubWrapper.props('readonly')).toBe(false)
      })
    })
  })
})
