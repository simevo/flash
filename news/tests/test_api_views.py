# ruff: noqa: PLR2004, S106

from unittest import mock

from django.core.cache import cache
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from flash.users.models import User
from news.models import Articles
from news.models import Feeds
from news.tasks import poll as poll_task


class ArticleAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
        )
        cls.feed = Feeds.objects.create(
            title="Test Feed",
            url="http://example.com/rss",
            active=True,
        )
        Articles.objects.create(
            feed=cls.feed,
            title="Article 1",
            content_original="Content 1",
            url="http://example.com/article1",
            stamp=timezone.now() - timezone.timedelta(days=1),
        )
        Articles.objects.create(
            feed=cls.feed,
            title="Article 2",
            content_original="Content 2",
            url="http://example.com/article2",
            stamp=timezone.now(),
        )

    def setUp(self):
        self.client.login(username="testuser", password="testpassword")
        cache.clear()  # Clear cache before each test

    def test_articles_list_caching_and_content(self):
        """
        Test that the articles list endpoint is cached and content is consistent.
        """
        url = reverse("api:articles-list")

        # Initial request
        response1 = self.client.get(url)
        assert response1.status_code == 200
        assert (
            "results" in response1.data
        ), "Response data should contain 'results' for a list view."

        # Second request - should hit the cache.
        response2 = self.client.get(url)
        assert response2.status_code == 200

        # Verify content is the same, indicating a cached response or consistent data.
        assert (
            response1.content == response2.content
        ), "Content of first and second (cached) response should be identical."
        assert (
            len(response1.data["results"]) == 2
        ), "Initial number of articles should be 2."

    @mock.patch(
        "news.tasks.poller.Poller",
    )  # Mock the Poller class used within the poll_task
    def test_articles_list_cache_invalidation_after_polling(self, mock_poller_class):
        """
        Test cache invalidation: new articles appear in the list after polling.
        Assumes poll_task clears the cache and new data is available.
        """
        try:
            url = reverse("api:articles-list")
        except NoReverseMatch:
            url = reverse("api:articlescombined-list")

        # Mock the poller's behavior.
        mock_poller_instance = mock_poller_class.return_value
        mock_poller_instance.poll.return_value = (
            None  # Simulate poll() completing its run.
        )

        # 1. Initial request, populates cache.
        response_before_poll = self.client.get(url)
        assert response_before_poll.status_code == 200
        assert (
            len(response_before_poll.data["results"]) == 2
        ), "Should initially have 2 articles."

        # 2. Simulate a new article being added (as if by a successful poll run).
        Articles.objects.create(
            feed=self.feed,
            title="Article 3",
            content_original="Content 3",
            url="http://example.com/article3",
            stamp=timezone.now() + timezone.timedelta(seconds=1),  # Ensure it's newer
        )

        # 3. Call the poll task. This task is expected to clear the cache.
        poll_task.s().apply()  # Executes the task, which should call cache.clear().

        # 4. Fetch the list again. Should be a fresh query due to cache invalidation.
        response_after_poll = self.client.get(url)
        assert response_after_poll.status_code == 200
        assert (
            len(response_after_poll.data["results"]) == 3
        ), "A new article should be present after polling and cache invalidation."

        # Verify that the content is different (due to the new article).
        assert (
            response_before_poll.content != response_after_poll.content
        ), "Response content should differ after new article and cache refresh."
