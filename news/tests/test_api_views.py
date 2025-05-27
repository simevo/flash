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
        cls.feed1 = Feeds.objects.create(
            title="Test Feed 1",
            url="http://example.com/rss1",
            active=True,
        )
        cls.feed2 = Feeds.objects.create(
            title="Test Feed 2",
            url="http://example.com/rss2",
            active=True,
        )

        cls.articles_feed1 = []
        cls.articles_feed2 = []

        # Need to import ArticlesData
        from news.models import ArticlesData

        # StandardResultsSetPagination.page_size is 200. Create 410 articles for feed1.
        for i in range(410):
            article = Articles.objects.create(
                feed=cls.feed1,
                title=f"Article F1 {i+1}",
                content_original=f"Content F1 {i+1}",
                url=f"http://example.com/article_f1_{i+1}",
                stamp=timezone.now() - timezone.timedelta(days=410 - i),
            )
            # Create corresponding ArticlesData with varied length
            # Length values from 100 to 100 + 409*10 = 4190, varying by 10
            ArticlesData.objects.create(
                id=article,  # Link to the article instance
                views=i * 10,  # Dummy data
                rating=(i % 5) + 1,  # Dummy data
                to_reads=0,  # Dummy data
                length=100 + (i * 10),  # Varied length
            )
            cls.articles_feed1.append(article)

        # Create 10 articles for feed2 for filtering tests
        for i in range(10):
            article = Articles.objects.create(
                feed=cls.feed2,
                title=f"Article F2 {i+1}",
                content_original=f"Content F2 {i+1}",
                url=f"http://example.com/article_f2_{i+1}",
                stamp=timezone.now() - timezone.timedelta(days=10 - i),
            )
            # Create corresponding ArticlesData with varied length
            # Length values from 200 to 200 + 9*5 = 245, varying by 5
            ArticlesData.objects.create(
                id=article,
                views=i * 5,
                rating=(i % 3) + 1,
                to_reads=0,
                length=200 + (i * 5),  # Varied length
            )
            cls.articles_feed2.append(article)

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
        page_size = 200  # from StandardResultsSetPagination
        # Should initially have {page_size} articles on page 1
        assert len(response_before_poll.data["results"]) == page_size

        # 2. Simulate a new article being added (as if by a successful poll run).
        Articles.objects.create(
            feed=self.feed1,  # Was self.feed
            title="Article New",
            content_original="Content New",
            url="http://example.com/article_new",
            stamp=timezone.now() + timezone.timedelta(seconds=1),  # Ensure it's newer
        )

        # 3. Call the poll task. This task is expected to clear the cache.
        poll_task.s().apply()  # Executes the task, which should call cache.clear().

        # 4. Fetch the list again. Should be a fresh query due to cache invalidation.
        response_after_poll = self.client.get(url)
        assert response_after_poll.status_code == 200
        # A full page of articles ({page_size}) should still be present after polling
        assert len(response_after_poll.data["results"]) == page_size

        # Response content should differ after new article and cache refresh, due to
        # re-randomization
        assert response_before_poll.content != response_after_poll.content

    def test_articles_list_perturbed_chronological_order_stability(self):
        """
        Test that the articles list endpoint returns articles in a stable,
        perturbed chronological order.
        """
        try:
            url = reverse("api:articles-list")
        except NoReverseMatch:
            url = reverse("api:articlescombined-list")

        # Fetch the article list twice
        response1 = self.client.get(url)
        assert response1.status_code == 200
        response1_ids = [article["id"] for article in response1.data["results"]]

        # Clear cache to ensure the view re-queries the database
        cache.clear()

        response2 = self.client.get(url)
        assert response2.status_code == 200
        response2_ids = [article["id"] for article in response2.data["results"]]

        # Need multiple articles to test order stability
        assert len(response1_ids) > 1

        # Responses should have the same number of articles (page_size)
        assert len(response1_ids) == len(response2_ids)

        # Article IDs should be in the SAME order on subsequent requests (after cache
        # clear) due to deterministic perturbation
        assert response1_ids == response2_ids

    def test_articles_list_is_actually_perturbed(self):
        """
        Test that the perturbed order is different from simple chronological order.
        """
        from news.models import ArticlesCombined  # For direct model query

        try:
            url = reverse("api:articles-list")
        except NoReverseMatch:
            url = reverse("api:articlescombined-list")

        response_perturbed = self.client.get(url)
        assert response_perturbed.status_code == 200
        perturbed_ids_page1 = [
            article["id"] for article in response_perturbed.data["results"]
        ]

        # Fetch all article IDs ordered chronologically directly from the model
        # This assumes all test articles are relevant; if filters are applied by
        # default by the view even without query params, this comparison needs to
        # be more nuanced.
        # The view's default queryset is ArticlesCombined.objects.all(), filters are
        # applied later.
        # So, we are comparing against the full unfiltered set.
        page_size = 200  # StandardResultsSetPagination.page_size
        chronological_articles = ArticlesCombined.objects.all().order_by("-id")[
            :page_size
        ]
        chronological_ids_page1 = [article.id for article in chronological_articles]

        # Perturbed list should have a full page
        assert len(perturbed_ids_page1) == page_size

        # Chronological list should have a full page for comparison
        assert len(chronological_ids_page1) == page_size

        # This assertion depends on the perturbation being strong enough
        # and data having enough variance in feed_id and length.
        # Perturbed order of article IDs on page 1 should be different from simple
        # chronological (-id) order
        assert perturbed_ids_page1 != chronological_ids_page1

    def test_articles_list_pagination_with_perturbed_order(self):
        """
        Test pagination works correctly with perturbed chronological article order.
        """
        try:
            url_base = reverse("api:articles-list")
        except NoReverseMatch:
            url_base = reverse("api:articlescombined-list")

        page_size = 200  # StandardResultsSetPagination.page_size

        # Fetch page 1
        response_page1 = self.client.get(url_base, {"page": 1})
        assert response_page1.status_code == 200
        page1_ids = [article["id"] for article in response_page1.data["results"]]
        # Page 1 should contain page_size articles
        assert len(page1_ids) == page_size

        # Fetch page 1 again (after cache clear) to check if its order is stable
        cache.clear()
        response_page1_again = self.client.get(url_base, {"page": 1})
        assert response_page1_again.status_code == 200
        page1_again_ids = [
            article["id"] for article in response_page1_again.data["results"]
        ]
        assert len(page1_again_ids) == page_size
        # Page 1 fetched twice (after cache clear) should have the SAME order
        assert page1_ids == page1_again_ids

    def test_articles_list_filtering_with_perturbed_order(self):
        """
        Test filtering works correctly with perturbed chronological article order.
        """
        try:
            url = reverse("api:articles-list")
        except NoReverseMatch:
            url = reverse("api:articlescombined-list")

        # Filter by feed2, which has 10 articles
        feed2_id = self.feed2.id
        num_feed2_articles = len(self.articles_feed2)  # Should be 10

        response1 = self.client.get(url, {"feed_id": feed2_id})
        assert response1.status_code == 200
        response1_ids = [article["id"] for article in response1.data["results"]]
        # Should get all {num_feed2_articles} articles for feed_id feed2_id
        assert len(response1_ids) == num_feed2_articles

        for article_data in response1.data["results"]:
            # All articles should belong to the filtered feed
            assert article_data["feed"]["id"] == feed2_id
