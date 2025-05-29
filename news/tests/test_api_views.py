# ruff: noqa: PLR2004, S106

from unittest import mock

from django.core.cache import cache
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from flash.users.models import User
from news.models import Articles
from news.models import ArticlesData
from news.models import Feeds
from news.tasks import poll as poll_task


def create_articles(feed, n):
    articles = []
    for i in range(n):
        article = Articles.objects.create(
            feed=feed,
            title=f"Article F1 {i+1}",
            content_original=f"Content F1 {i+1}",
            url=f"http://example.com/article_f1_{i+1}",
            stamp=timezone.now() - timezone.timedelta(hours=410 - i),
        )
        article_data = ArticlesData.objects.get(id=article)
        # ArticlesData is created by the trogger; tweak data:
        # Length values from 100 to 1000 + 200*20 = 5000, varying by 20
        article_data.views = i * 10  # Dummy data
        article_data.rating = (i % 5) + 1  # Dummy data
        article_data.to_reads = 0  # Dummy data
        article_data.length = 1000 + (i * 20)  # Varied length
        article_data.save()
        articles.append(article)

    return articles


class ArticleAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
        )
        cls.feed1 = Feeds.objects.get(pk=1)
        cls.feed2 = Feeds.objects.get(pk=2)

        # Create 100 articles for each feed.
        cls.articles_feed1 = create_articles(cls.feed1, 100)
        cls.articles_feed2 = create_articles(cls.feed2, 100)

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
            len(response1.data["results"]) == 200
        ), "Initial number of articles should be 200."

    @mock.patch(
        "news.tasks.poller.Poller",
    )  # Mock the Poller class used within the poll_task
    def test_articles_list_cache_invalidation_after_polling(self, mock_poller_class):
        """
        Test cache invalidation: new articles appear in the list after polling.
        Assumes poll_task clears the cache and new data is available.
        """
        url = reverse("api:articles-list")

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
        url = reverse("api:articles-list")

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

        url = reverse("api:articles-list")

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
        url = reverse("api:articles-list")

        # Filter by feed2, which has 100 articles
        feed2_id = self.feed2.id
        num_feed2_articles = len(self.articles_feed2)

        response1 = self.client.get(url, {"feed_id": feed2_id})
        assert response1.status_code == 200
        response1_ids = [article["id"] for article in response1.data["results"]]
        # Should get all {num_feed2_articles} articles for feed_id feed2_id
        assert len(response1_ids) == num_feed2_articles

        for article_data in response1.data["results"]:
            # All articles should belong to the filtered feed
            assert article_data["feed"] == feed2_id


class UserArticleListsExportTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="exportuser",
            password="testpassword",
            email="export@example.com",
        )
        cls.feed = Feeds.objects.create(
            name="Test Feed for Export",
            url="http://example.com/feed_export",
            is_active=True,
        )

        # Create articles with varying lengths
        cls.article1 = Articles.objects.create(
            feed=cls.feed,
            title="Export Article 1",
            content_original="Content 1",
            url="http://example.com/export_article_1",
            stamp=timezone.now(),
            length=1200,  # 1 minute reading time (1200 / (6*200))
        )
        cls.article2 = Articles.objects.create(
            feed=cls.feed,
            title="Export Article 2",
            content_original="Content 2",
            url="http://example.com/export_article_2",
            stamp=timezone.now(),
            length=2400,  # 2 minutes reading time
        )
        cls.article3 = Articles.objects.create(
            feed=cls.feed,
            title="Export Article 3",
            content_original="Content 3",
            url="http://example.com/export_article_3",
            stamp=timezone.now(),
            length=3600,  # 3 minutes reading time
        )

        cls.user_list = cls.user.userarticlelists_set.create(
            name="Test Export List",
            user=cls.user,
        )
        cls.user_list.articles.add(cls.article1, cls.article2, cls.article3)

        cls.expected_article_count = 3
        cls.expected_total_reading_time = (1200 + 2400 + 3600) // (
            6 * 200
        )  # 1 + 2 + 3 = 6

    def setUp(self):
        self.client.login(username="exportuser", password="testpassword")

    def test_html_export(self):
        url = reverse(
            "api:userarticlelists-html",
            kwargs={"pk": self.user_list.pk},
        )
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(
            response,
            f"Total articles: {self.expected_article_count}",
        )
        self.assertContains(
            response,
            f"Estimated total reading time: {self.expected_total_reading_time} minutes",
        )
        self.assertContains(response, self.user_list.name)  # Check list name

    @mock.patch("news.api.views.pisa.pisaDocument")
    def test_pdf_export(self, mock_pisa_document):
        # Mock the PDF generation to avoid actual PDF creation
        mock_pdf = mock.Mock()
        mock_pdf.err = False
        mock_pisa_document.return_value = mock_pdf

        url = reverse("api:userarticlelists-pdf", kwargs={"pk": self.user_list.pk})
        response = self.client.get(url)
        assert response.status_code == 200

        # Check that pisaDocument was called
        mock_pisa_document.assert_called_once()

        # Verify the context passed to the template for PDF generation

        # Let's verify the context passed to `render` inside the view method.
        # We can mock `django.shortcuts.render` for this specific test.
        with mock.patch("news.api.views.render") as mock_render:
            # Re-call the view
            self.client.get(url)
            mock_render.assert_called()
            # The context is the third argument to render
            context = mock_render.call_args[0][2]
            assert context["article_count"], self.expected_article_count
            assert (
                context["total_estimated_reading_time"]
                == self.expected_total_reading_time
            )
            assert context["list_name"] == self.user_list.name

    @mock.patch("news.api.views.get_epub")
    def test_epub_export_get_epub_called_correctly(self, mock_get_epub):
        # Mock get_epub to check its arguments
        mock_book = mock.Mock()
        mock_get_epub.return_value = mock_book

        url = reverse(
            "api:userarticlelists-epub",
            kwargs={"pk": self.user_list.pk},
        )
        response = self.client.get(url)
        assert response.status_code == 200

        # Check that get_epub was called once
        mock_get_epub.assert_called_once()

        # Verify the arguments passed to get_epub
        args, kwargs = mock_get_epub.call_args
        assert len(args[0]) == self.expected_article_count  # Check number of articles
        assert args[1] == self.user_list.name
        assert args[2] == self.expected_article_count
        assert args[3] == self.expected_total_reading_time

    def test_actual_epub_content_summary(self):
        # This test will call the actual get_epub function
        url = reverse("api:userarticlelists-epub", kwargs={"pk": self.user_list.pk})
        response = self.client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/epub+zip"

    def test_me_action_with_counts_and_reading_time(self):
        # Create an additional empty list for the same user
        empty_list = self.user.userarticlelists_set.create(
            name="Empty Test List",
            user=self.user,
        )

        url = reverse("api:userarticlelists-me")
        response = self.client.get(url)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) >= 2  # At least the two lists we care about

        found_export_list = False
        found_empty_list = False

        for lst_data in response_data:
            if lst_data["id"] == self.user_list.id:  # This is "Test Export List"
                found_export_list = True
                assert lst_data["name"] == "Test Export List"
                assert lst_data["article_count"] == self.expected_article_count
                assert (
                    lst_data["total_estimated_reading_time"]
                    == self.expected_total_reading_time
                )

                # Check that 'articles' field contains the correct number of IDs
                assert len(lst_data["articles"]) == self.expected_article_count
                # And that the IDs match
                assert len(lst_data["articles"]) == len(
                    [self.article1.id, self.article2.id, self.article3.id],
                )

            elif lst_data["id"] == empty_list.id:
                found_empty_list = True
                assert lst_data["name"] == "Empty Test List"
                assert lst_data["article_count"] == 0
                assert lst_data["total_estimated_reading_time"] == 0
                assert lst_data["articles"] == []  # Should be an empty list

        assert found_export_list  # Test Export List not found in 'me' action response
        assert found_empty_list  # Empty Test List not found in 'me' action response
