import xml.etree.ElementTree as ET

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from news.models import Feeds  # Assuming Feeds model is in news.models


class OPMLExportTests(APITestCase):
    # Define constants for better clarity
    SETUP_FEED_COUNT = 2

    def setUp(self):
        # Create some sample Feeds objects for testing
        Feeds.objects.create(
            title="Feed 1",
            url="http://example.com/feed1",
            homepage="http://example.com/feed1",
            language="en",
        )
        Feeds.objects.create(
            title="Feed 2",
            url="http://example.com/feed2",
            homepage="http://example.com/feed2",
            language="en",
        )

    def test_opml_export_returns_200_ok(self):
        # Test that the endpoint returns a 200 OK status code
        url = reverse(
            "api:opml-export",
        )  # Ensure 'opml-export' is the name given in urls.py
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_opml_export_content_type_is_xml(self):
        # Test that the response content type is application/xml
        url = reverse("api:opml-export")
        response = self.client.get(url)
        assert response["Content-Type"] == "application/xml; charset=utf-8"

    def test_opml_export_content_structure_and_data(self):
        # Test the structure and content of the OPML XML
        url = reverse("api:opml-export")
        response = self.client.get(url)
        content = response.content.decode("utf-8")

        # Parse the XML content
        try:
            root = ET.fromstring(content)  # noqa: S314
        except ET.ParseError as e:
            msg = f"Failed to parse XML: {e}\nXML content was:\n{content}"
            raise AssertionError(msg) from e

        # Check OPML version
        assert root.tag == "opml"
        assert root.get("version") == "2.0"

        # Check head and title
        head = root.find("head")
        assert head is not None
        title = head.find("title")
        assert title is not None
        assert title.text == "Flash Feeds"

        # Check body and outlines
        body = root.find("body")
        assert body is not None
        outlines = body.findall("outline")
        assert len(outlines) == self.SETUP_FEED_COUNT

        # Check attributes of each outline (order might not be guaranteed,
        # so check specific attributes)
        expected_feeds_data = [
            {"title": "Feed 1", "xmlUrl": "http://example.com/feed1"},
            {"title": "Feed 2", "xmlUrl": "http://example.com/feed2"},
        ]

        actual_feeds_data = [
            {
                "title": outline.get("text"),
                "xmlUrl": outline.get("xmlUrl"),
                "type": outline.get("type"),
            }
            for outline in outlines
        ]

        for expected_feed in expected_feeds_data:
            found = False
            for actual_feed in actual_feeds_data:
                if (
                    actual_feed["title"] == expected_feed["title"]
                    and actual_feed["xmlUrl"] == expected_feed["xmlUrl"]
                    and actual_feed["type"] == "rss"
                ):
                    found = True
                    break
            assert found, f"Expected feed {expected_feed} not found or type is not \
                rss in actual data {actual_feeds_data}"

    def test_opml_export_empty_feeds(self):
        # Test with no feeds in the database
        Feeds.objects.all().delete()
        url = reverse("api:opml-export")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/xml; charset=utf-8"

        try:
            root = ET.fromstring(response.content.decode("utf-8"))  # noqa: S314
        except ET.ParseError as e:
            msg = f"Failed to parse XML: {e}\nXML content was:\n\
                {response.content.decode('utf-8')}"
            raise AssertionError(msg) from e

        body = root.find("body")
        assert body is not None
        outlines = body.findall("outline")
        assert len(outlines) == 0

    def test_opml_export_feed_with_special_chars(self):
        # Test with feed titles/URLs that need escaping
        Feeds.objects.create(
            title="Feed with <&>",
            url="http://example.com/feed?a=1&b=2",
            homepage="http://example.com/feed",
            language="en",
        )
        url = reverse("api:opml-export")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        try:
            root = ET.fromstring(response.content.decode("utf-8"))  # noqa: S314
        except ET.ParseError as e:
            msg = f"Failed to parse XML: {e}\nXML content was:\n\
                {response.content.decode('utf-8')}"
            raise AssertionError(msg) from e

        body = root.find("body")
        assert body is not None
        outlines = body.findall("outline")

        # Check the feed with special characters
        # The title should be "Feed with <&>" and URL "http://example.com/feed?a=1&b=2"
        # This count includes the 2 from setUp and 1 from this test
        expected_outline_count = (
            self.SETUP_FEED_COUNT + 1
        )  # Feeds from setUp + 1 feed from this test
        assert len(outlines) == expected_outline_count

        # Correcting the check to see if the *original* unescaped values are present
        # in the parsed XML attributes
        # This implies that the escaping was done correctly to form valid XML,
        # and ET.fromstring could parse it.
        special_feed_title = "Feed with <&>"
        special_feed_url = "http://example.com/feed?a=1&b=2"

        found_special_char_feed_in_parsed_xml = any(
            outline.get("text") == special_feed_title
            and outline.get("xmlUrl") == special_feed_url
            and outline.get("type") == "rss"
            for outline in outlines
        )
        assert (
            found_special_char_feed_in_parsed_xml
        ), "Feed with special characters not found or attributes incorrect."
