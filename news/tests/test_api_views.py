from unittest import mock

from django.urls import reverse
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APITestCase

from news.models import Feeds, Articles, ArticlesCombined
from flash.users.models import User
from news.tasks import poll as poll_task

# Ensure this task is imported for Celery integration (e.g., if using task_always_eager)
# If poll_task is not a celery task but a regular function, direct call is fine.
# from news.tasks import poll as poll_task

class ArticleAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        cls.feed = Feeds.objects.create(title='Test Feed', url='http://example.com/rss', active=True)
        # Create articles. Assuming ArticlesCombined gets populated correctly from Articles.
        # Or, if ArticlesCombined is the target table for API, create them directly if possible.
        # For this test, we'll create Articles and assume they reflect in ArticlesCombined.
        Articles.objects.create(feed=cls.feed, title='Article 1', content_original='Content 1', url='http://example.com/article1', guid='guid1', stamp=timezone.now() - timezone.timedelta(days=1))
        Articles.objects.create(feed=cls.feed, title='Article 2', content_original='Content 2', url='http://example.com/article2', guid='guid2', stamp=timezone.now())
        # It's important that these articles are also reflected in ArticlesCombined for the API tests to pass,
        # as the ArticlesView queries ArticlesCombined. We assume this happens automatically (e.g. DB view or trigger).

    def setUp(self):
        self.client.login(username='testuser', password='testpassword')
        cache.clear() # Clear cache before each test

    def test_articles_list_caching_and_content(self):
        """
        Test that the articles list endpoint is cached and content is consistent.
        The URL name 'api:articles-list' is assumed based on common DRF router registration.
        If ArticlesView uses ArticlesCombined model, router might generate 'api:articlescombined-list'.
        Confirm the correct URL name from your project's api_router.py.
        """
        # Attempt to determine the correct URL name.
        # Common patterns: 'api:articles-list' or 'api:articlescombined-list'.
        # We will try 'api:articles-list' first, assuming a basename was set for the viewset.
        # If your viewset is registered like router.register('articles', ArticlesView, basename='articles')
        # then 'api:articles-list' is correct.
        # If it's router.register('articles', ArticlesView) and queryset is on ArticlesCombined,
        # it might be 'api:articlescombined-list'.
        try:
            url = reverse('api:articles-list')
        except Exception:
            url = reverse('api:articlescombined-list')


        # Initial request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertIn('results', response1.data, "Response data should contain 'results' for a list view.")
        
        # Check for cache-related headers (optional, but good for debugging)
        # For example, Django's cache_page decorator adds 'Expires' and 'Cache-Control'.
        # self.assertTrue(response1.has_header('Expires'), "Response should have 'Expires' header if page is cached.")

        # Second request - should hit the cache.
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        # Verify content is the same, indicating a cached response or consistent data.
        self.assertEqual(response1.content, response2.content, "Content of first and second (cached) response should be identical.")
        self.assertEqual(len(response1.data['results']), 2, "Initial number of articles should be 2.")

    @mock.patch('news.tasks.poller.Poller') # Mock the Poller class used within the poll_task
    def test_articles_list_cache_invalidation_after_polling(self, mock_poller_class):
        """
        Test cache invalidation: new articles appear in the list after polling.
        Assumes poll_task clears the cache and new data is available.
        """
        try:
            url = reverse('api:articles-list')
        except Exception:
            url = reverse('api:articlescombined-list')

        # Mock the poller's behavior.
        mock_poller_instance = mock_poller_class.return_value
        mock_poller_instance.poll.return_value = None # Simulate poll() completing its run.

        # 1. Initial request, populates cache.
        response_before_poll = self.client.get(url)
        self.assertEqual(response_before_poll.status_code, 200)
        self.assertEqual(len(response_before_poll.data['results']), 2, "Should initially have 2 articles.")

        # 2. Simulate a new article being added (as if by a successful poll run).
        # This article needs to be reflected in ArticlesCombined for the API to see it.
        Articles.objects.create(
            feed=self.feed,
            title='Article 3',
            content_original='Content 3',
            url='http://example.com/article3',
            guid='guid3', # Ensure unique guid
            stamp=timezone.now() + timezone.timedelta(seconds=1) # Ensure it's newer
        )
        # Manually refresh ArticlesCombined if it's a materialized view and needs it.
        # For this test, we assume it reflects changes to Articles table automatically or via triggers.


        # 3. Call the poll task. This task is expected to clear the cache.
        # Ensure Celery is configured for testing (e.g., CELERY_TASK_ALWAYS_EAGER=True).
        poll_task.s().apply() # Executes the task, which should call cache.clear().

        # 4. Fetch the list again. Should be a fresh query due to cache invalidation.
        response_after_poll = self.client.get(url)
        self.assertEqual(response_after_poll.status_code, 200)
        self.assertEqual(len(response_after_poll.data['results']), 3, "A new article should be present after polling and cache invalidation.")

        # Verify that the content is different (due to the new article).
        self.assertNotEqual(response_before_poll.content, response_after_poll.content, "Response content should differ after new article and cache refresh.")
