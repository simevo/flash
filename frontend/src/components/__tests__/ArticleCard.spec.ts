import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ArticleCard from '../ArticleCard.vue'

describe('ArticleCard', () => {
  it('renders article title', () => {
    const article = {
      id: 1,
      feed: 1,
      title: 'Test Article Title',
      title_original: 'Test Article Title Original',
      url: 'http://example.com',
      stamp: Math.floor(Date.now() / 1000),
      author: 'Test Author',
      language: 'fr', // Changed to 'fr' to be different from base_language
      base_language: 'en',
      excerpt: 'Test excerpt',
      length: 100,
      image: '',
      saved: false,
      read: false,
      score: 0,
      created_at: '',
      updated_at: '',
    }
    const feed_dict = {
      1: {
        id: 1,
        url: 'http://example.com/feed',
        title: 'Test Feed',
        image: 'http://example.com/feed_image.png',
        description: '',
        language: '',
        official_url: null,
        last_success: null,
        last_error: null,
        error_counter: 0,
        next_try: null,
        active: false,
        is_nsfw: false,
        ignore_older_than: null,
        ignore_shorter_than: null,
        created_at: '',
        updated_at: '',
      },
    }

    const wrapper = mount(ArticleCard, {
      props: {
        article,
        feed_dict,
        index: 0,
        list_id: null,
      },
      global: {
        stubs: ['router-link'], // Stubbing router-link to avoid router dependency
        provide: {
          base_language: 'en', // Provide base_language
        },
        renderStubDefaultSlot: true, // Render slot content for stubs
      },
    })

    // Check for both titles, joined by "—"
    expect(wrapper.find('h5').text()).toContain('Test Article Title Original — Test Article Title')
  })
})
