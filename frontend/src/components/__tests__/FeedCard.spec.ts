import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import FeedCard from '../FeedCard.vue';
import ThreeStateCheckBox from '../ThreeStateCheckBox.vue';
import { fetch_wrapper } from '../../utils'; // Adjusted path assuming utils is in src/utils
import { useAuthStore } from '../../stores/auth.store'; // Adjusted path

// Mock fetch_wrapper
vi.mock('../../utils', () => ({
  fetch_wrapper: vi.fn(),
}));

// Mock auth store
vi.mock('../../stores/auth.store', () => ({
  useAuthStore: vi.fn(() => ({
    user: { is_staff: false }, // Default mock user
  })),
}));

// Helper function to create a mock feed
const createMockFeed = (id: number, my_rating: number | undefined | null, last_polled_epoch: number | null = Date.now() / 1000) => ({
  id,
  title: `Feed ${id}`,
  url: `http://example.com/feed${id}`,
  homepage: `http://example.com/${id}`,
  image: `http://example.com/image${id}.png`,
  article_count: 10,
  last_polled_epoch,
  my_rating,
  tags: ['tag1', 'tag2'],
  active: true,
  // Add other necessary fields from the Feed type if FeedCard uses them
  // For example:
  // description: "A mock feed",
  // created_at: "2023-01-01T00:00:00Z",
  // updated_at: "2023-01-01T00:00:00Z",
  // user_id: 1,
});

describe('FeedCard.vue', () => {
  let mockAuthStore: any;

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
    // Default mock user for most tests
    mockAuthStore = useAuthStore as any;
    mockAuthStore.mockReturnValue({ user: { is_staff: false } });
  });

  describe('Rendering', () => {
    it('should NOT render RatingToolbar', () => {
      const feed = createMockFeed(1, 0);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: {
            RouterLink: true, // Stub RouterLink for simplicity
            ThreeStateCheckBox: true, // Stub if not testing its internals here
          },
        },
      });
      // Assuming RatingToolbar had a specific class or ID
      expect(wrapper.findComponent({ name: 'RatingToolbar' }).exists()).toBe(false);
      expect(wrapper.find('.rating-toolbar-class').exists()).toBe(false); // Example class
    });

    it('should render ThreeStateCheckBox when last_polled_epoch is present', () => {
      const feed = createMockFeed(1, 0, Date.now() / 1000);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      expect(wrapper.findComponent(ThreeStateCheckBox).exists()).toBe(true);
    });

    it('should NOT render ThreeStateCheckBox when last_polled_epoch is null', () => {
      const feed = createMockFeed(1, 0, null);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      expect(wrapper.findComponent(ThreeStateCheckBox).exists()).toBe(false);
    });

    it('passes correct `value` (true) to ThreeStateCheckBox when my_rating is between -4 and 5', () => {
      const feed = createMockFeed(1, 3); // Example rating: 3
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      expect(checkBox.exists()).toBe(true);
      expect(checkBox.props('value')).toBe(true);
    });

    it('passes correct `value` (false) to ThreeStateCheckBox when my_rating is -5', () => {
      const feed = createMockFeed(1, -5);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      expect(checkBox.exists()).toBe(true);
      expect(checkBox.props('value')).toBe(false);
    });

    it('passes correct `value` (null) to ThreeStateCheckBox when my_rating is undefined', () => {
      const feed = createMockFeed(1, undefined);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      expect(checkBox.exists()).toBe(true);
      expect(checkBox.props('value')).toBe(null);
    });

     it('passes correct `value` (null) to ThreeStateCheckBox when my_rating is null', () => {
      const feed = createMockFeed(1, null);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      expect(checkBox.exists()).toBe(true);
      expect(checkBox.props('value')).toBe(null);
    });

    it('renders edit button if user is staff', () => {
      mockAuthStore.mockReturnValue({ user: { is_staff: true } });
      const feed = createMockFeed(1, 0);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: false }, // Don't stub RouterLink to find it by id
        },
      });
      expect(wrapper.find('#edit').exists()).toBe(true);
    });

    it('does NOT render edit button if user is not staff', () => {
      mockAuthStore.mockReturnValue({ user: { is_staff: false } });
      const feed = createMockFeed(1, 0);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      expect(wrapper.find('#edit').exists()).toBe(false);
    });
  });

  describe('Checkbox Interaction (handleShowHideChange)', () => {
    const mockFeedId = 123;

    // Scenario 1: Checkbox changes to true (Show)
    it('handles checkbox change to true (Show): calls API, optimistically updates, handles success', async () => {
      const initialRating = -5;
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // Simulate the change event from ThreeStateCheckBox
      // ThreeStateCheckBox emits the new desired state (true, false, or null)
      checkBox.vm.$emit('change', true); // Directly emit the target state
      
      // Check optimistic update
      expect(wrapper.props('feed').my_rating).toBe(0);
      
      // Check emitted 'updating' event
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledWith('/api/user-feeds/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockFeedId, rating: 0 }),
      });
      expect(wrapper.props('feed').my_rating).toBe(0); // Remains 0 on success
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
    });
    
    it('handles checkbox change to true (Show): API failure reverts optimistic update', async () => {
      const initialRating = -5;
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
          plugins: [/* provide(AuthStoreSymbol, mockAuthStore) if needed */],
        },
      });
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: false, statusText: 'Error', text: async () => "API Error" });

      checkBox.vm.$emit('change', true);
      expect(wrapper.props('feed').my_rating).toBe(0); // Optimistic update
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledTimes(1);
      expect(wrapper.props('feed').my_rating).toBe(initialRating); // Reverted
      expect(alertSpy).toHaveBeenCalledWith('Error updating visibility: Error - API Error');
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
      alertSpy.mockRestore();
    });

    // Scenario 2: Checkbox changes to false (Don't Show)
    it('handles checkbox change to false (Dont Show): calls API, optimistically updates, handles success', async () => {
      const initialRating = 0;
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      checkBox.vm.$emit('change', false);
      
      expect(wrapper.props('feed').my_rating).toBe(-5); // Optimistic
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledWith('/api/user-feeds/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockFeedId, rating: -5 }),
      });
      expect(wrapper.props('feed').my_rating).toBe(-5); // Remains -5
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
    });

    it('handles checkbox change to false (Dont Show): API failure reverts optimistic update', async () => {
      const initialRating = 0;
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: false, statusText: 'Error', text: async () => "API Error" });

      checkBox.vm.$emit('change', false);
      expect(wrapper.props('feed').my_rating).toBe(-5); // Optimistic
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledTimes(1);
      expect(wrapper.props('feed').my_rating).toBe(initialRating); // Reverted
      expect(alertSpy).toHaveBeenCalled();
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
      alertSpy.mockRestore();
    });

    // Scenario 3: Checkbox changes from null to true (Show)
    it('handles checkbox change from null to true (Show): calls API, optimistically updates, handles success', async () => {
      const initialRating = undefined; // Or null
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // ThreeStateCheckBox emits `true` when clicked from `null` state
      checkBox.vm.$emit('change', true); 
      
      expect(wrapper.props('feed').my_rating).toBe(0); // Optimistic
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledWith('/api/user-feeds/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockFeedId, rating: 0 }),
      });
      expect(wrapper.props('feed').my_rating).toBe(0); // Remains 0
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
    });

     // Scenario 4: Checkbox changes from false to null (which component treats as show with rating 0)
    it('handles checkbox change from false to null (effectively Show): calls API with rating 0', async () => {
      const initialRating = -5; // Checkbox is initially false
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      (fetch_wrapper as any).mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // Simulate the change event from ThreeStateCheckBox when it cycles from false to null
      checkBox.vm.$emit('change', null); 
      
      // Component's handleShowHideChange should interpret null (from false) as "show" with rating 0
      expect(wrapper.props('feed').my_rating).toBe(0); // Optimistic update to 0
      
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledWith('/api/user-feeds/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feed: mockFeedId, rating: 0 }), // Expecting rating 0
      });
      expect(wrapper.props('feed').my_rating).toBe(0); // Remains 0 on success
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
    });


    // Test for network error
    it('handles network error during API call and reverts optimistic update', async () => {
      const initialRating = 0;
      const feed = createMockFeed(mockFeedId, initialRating);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true },
        },
      });
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const checkBox = wrapper.findComponent(ThreeStateCheckBox);
      const networkError = new Error("Network failure");
      (fetch_wrapper as any).mockRejectedValueOnce(networkError);

      checkBox.vm.$emit('change', false); // Change to "Don't Show"
      expect(wrapper.props('feed').my_rating).toBe(-5); // Optimistic update
      expect(wrapper.emitted().updating).toEqual([[true]]);

      await flushPromises();

      expect(fetch_wrapper).toHaveBeenCalledTimes(1);
      expect(wrapper.props('feed').my_rating).toBe(initialRating); // Reverted
      expect(alertSpy).toHaveBeenCalledWith(`Network error: ${networkError}`);
      expect(wrapper.emitted().updating).toEqual([[true], [false]]);
      alertSpy.mockRestore();
    });
  });

  describe('Refresh button', () => {
    it('emits "refresh_feed" with feed id when refresh button is clicked', async () => {
      const feed = createMockFeed(42, 0);
      const wrapper = mount(FeedCard, {
        props: { feed, clickable: true },
        global: {
          stubs: { RouterLink: true, ThreeStateCheckBox: true },
        },
      });

      const refreshButton = wrapper.find('button[aria-label="Aggiorna la fonte"]');
      expect(refreshButton.exists()).toBe(true);

      await refreshButton.trigger('click');

      expect(wrapper.emitted().refresh_feed).toBeTruthy();
      expect(wrapper.emitted().refresh_feed![0]).toEqual([feed.id]);
    });
  });
});
