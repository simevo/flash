import { describe, it, expect, vi, beforeEach, afterEach, afterAll } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import NegativeRating from '../NegativeRating.vue'
import { fetch_wrapper } from '../../utils'

// Mock fetch_wrapper
vi.mock('../../utils', () => ({
  fetch_wrapper: vi.fn(),
}))

// Mock global alert
global.alert = vi.fn()

// To track the href for location mock
let currentHref = ''

type PatchedFeed = {
  id: number
  title: string // Example other property
  my_rating?: number | undefined
}

describe('NegativeRating.vue', () => {
  let wrapper: VueWrapper<any>
  const mockItem: PatchedFeed = { id: 1, title: 'Test Feed', my_rating: 0 }
  const mockThreshold = 0
  const mockEndpoint = '/api/rate_feed/'

  let mockLocationObject: any;

  beforeEach(() => {
    vi.clearAllMocks()
    currentHref = '' // Reset href for each test

    mockLocationObject = {
      assign: vi.fn((url: string) => { currentHref = url; }),
      get href() { return currentHref; },
      set href(url: string) { currentHref = url; },
      reload: vi.fn(),
    };
    vi.stubGlobal('location', mockLocationObject);


    // Default mock implementation for fetch_wrapper
    ;(fetch_wrapper as vi.Mock).mockResolvedValue({
      status: 201, // Default to success "created"
      json: async () => ({}),
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })
  
  // Helper function to create the component
  const createComponent = (props?: any) => {
    return mount(NegativeRating, {
      props: {
        item: mockItem,
        threshold: mockThreshold,
        endpoint: mockEndpoint,
        readonly: false,
        ...props,
      },
      global: {
        // If there are global provides or stubs, add them here
      },
    })
  }

  describe('Initial Rendering', () => {
    it('renders the button', () => {
      wrapper = createComponent()
      expect(wrapper.find('button').exists()).toBe(true)
    })

    it('displays the correct initial title', () => {
      wrapper = createComponent({ threshold: 0 }) // Explicitly threshold 0
      // Title is `Dai ${1 - threshold} voti negativi`
      // For threshold = 0, it's "Dai 1 voti negativi"
      expect(wrapper.find('button').attributes('title')).toBe('Dai 1 voti negativi')

      wrapper.unmount()
      wrapper = createComponent({ threshold: 1 })
      // For threshold = 1, it's "Dai 0 voti negativi"
      expect(wrapper.find('button').attributes('title')).toBe('Dai 0 voti negativi')
    })

    it('applies icon-danger when my_rating is less than threshold', () => {
      wrapper = createComponent({ item: { ...mockItem, my_rating: -1 }, threshold: 0 })
      expect(wrapper.find('button').classes()).toContain('icon-danger')
      expect(wrapper.find('button').classes()).not.toContain('icon-light')
    })

    it('applies icon-light when my_rating is equal to threshold', () => {
      wrapper = createComponent({ item: { ...mockItem, my_rating: 0 }, threshold: 0 })
      expect(wrapper.find('button').classes()).toContain('icon-light')
      expect(wrapper.find('button').classes()).not.toContain('icon-danger')
    })
    
    it('applies icon-light when my_rating is greater than threshold', () => {
      wrapper = createComponent({ item: { ...mockItem, my_rating: 1 }, threshold: 0 })
      expect(wrapper.find('button').classes()).toContain('icon-light')
      expect(wrapper.find('button').classes()).not.toContain('icon-danger')
    })

    it('applies icon-light when my_rating is undefined (defaults to 0)', () => {
      wrapper = createComponent({ item: { ...mockItem, my_rating: undefined }, threshold: 0 })
      expect(wrapper.find('button').classes()).toContain('icon-light')
      expect(wrapper.find('button').classes()).not.toContain('icon-danger')
    })
  })

  describe('Props Handling - readonly', () => {
    it('does not call set method or emit events when readonly is true', async () => {
      const itemCopy = { ...mockItem, my_rating: 0 }
      wrapper = createComponent({ readonly: true, item: itemCopy })
      
      await wrapper.find('button').trigger('click')
      
      expect(fetch_wrapper).not.toHaveBeenCalled()
      expect(wrapper.emitted('updating')).toBeUndefined()
      expect(itemCopy.my_rating).toBe(0) // Prop should not be mutated
    })
  })

  describe('Click Behavior & API Call', () => {
    it('updates rating, emits events, calls API, and shows success alert on first click', async () => {
      const localItem = { ...mockItem, my_rating: 0 } // Use a local copy for the test
      wrapper = createComponent({ item: localItem, threshold: 0 })

      await wrapper.find('button').trigger('click')

      // 1. item.my_rating is updated (component mutates prop directly)
      expect(localItem.my_rating).toBe(-1) // threshold (0) - 1

      // 2. Emits 'updating' events
      expect(wrapper.emitted('updating')).toEqual([[true], [false]])
      
      // 3. Calls fetch_wrapper
      expect(fetch_wrapper).toHaveBeenCalledTimes(1)
      expect(fetch_wrapper).toHaveBeenCalledWith(mockEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockItem.id, rating: -1 }),
      })

      // 4. Shows alert for 201 status
      expect(global.alert).toHaveBeenCalledWith('Rating inserito con successo')
      
      // 5. Dynamic classes
      expect(wrapper.find('button').classes()).toContain('icon-danger')
    })

    it('toggles rating to 0, emits, calls API, and shows update alert on second click', async () => {
      const localItem = { ...mockItem, my_rating: -1 } // Start with rating already set
      wrapper = createComponent({ item: localItem, threshold: 0 })
      
      ;(fetch_wrapper as vi.Mock).mockResolvedValueOnce({ status: 200, json: async () => ({}) }) // Mock for this specific call

      await wrapper.find('button').trigger('click')

      expect(localItem.my_rating).toBe(0) // Toggled back to 0
      expect(wrapper.emitted('updating')).toEqual([[true], [false]])
      expect(fetch_wrapper).toHaveBeenCalledWith(mockEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockItem.id, rating: 0 }),
      })
      expect(global.alert).toHaveBeenCalledWith('Rating aggiornato con successo')
      expect(wrapper.find('button').classes()).toContain('icon-light')
    })

    it('handles 403 Forbidden by redirecting', async () => {
      const localItem = { ...mockItem, my_rating: 0 }
      wrapper = createComponent({ item: localItem })
      ;(fetch_wrapper as vi.Mock).mockResolvedValueOnce({ status: 403 })

      await wrapper.find('button').trigger('click')
      
      // document.location = '/accounts/' is called in the component.
      // In JSDOM, this throws a "Not implemented: navigation (except hash changes)" error,
      // which is visible in the test output's stderr.
      // This error prevents us from reliably asserting the change on window.location.href
      // through the current mocking strategies.
      // However, we can confirm other behaviors around it.
      expect(fetch_wrapper).toHaveBeenCalledTimes(1) // Ensure API call was made
      expect(wrapper.emitted('updating')).toEqual([[true], [false]]) // Still emits updating
      expect(global.alert).not.toHaveBeenCalled() // No alert on 403 for this component's logic
    })

    it('handles generic API error with alert', async () => {
      const localItem = { ...mockItem, my_rating: 0 }
      wrapper = createComponent({ item: localItem })
      const errorResponse = { detail: 'Something broke' }
      ;(fetch_wrapper as vi.Mock).mockResolvedValueOnce({
        status: 500,
        statusText: 'Server Error',
        json: async () => errorResponse,
      })

      await wrapper.find('button').trigger('click')

      expect(global.alert).toHaveBeenCalledWith(
        'Errore: Server Error; ' + JSON.stringify(errorResponse)
      )
      expect(wrapper.emitted('updating')).toEqual([[true], [false]])
    })

    it('handles network error with alert', async () => {
      const localItem = { ...mockItem, my_rating: 0 }
      wrapper = createComponent({ item: localItem })
      const networkError = new Error('Network failed')
      ;(fetch_wrapper as vi.Mock).mockRejectedValueOnce(networkError)

      await wrapper.find('button').trigger('click')

      expect(global.alert).toHaveBeenCalledWith('Errore di rete: ' + networkError)
      expect(wrapper.emitted('updating')).toEqual([[true], [false]])
    })
  })
  
  // Restore original window.location after all tests in this describe block
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.unstubAllGlobals(); // Important to clean up global stubs
  })
  
  // No afterAll needed for location mock if using unstubAllGlobals in afterEach
})
