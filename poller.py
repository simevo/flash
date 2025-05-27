# ruff: noqa: S603, C901, ASYNC210, PLR0912, FBT003

import asyncio
import copy
import datetime
import html
import http.cookiejar
import json
import logging
import subprocess
import time
import urllib
from typing import Any
from typing import TypedDict

import aiohttp
import feedparser
import lxml.html
import pytz
import requests
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import NavigableString
from bs4 import Tag

from news.models import Articles
from news.models import FeedPolling

logger = logging.getLogger(__name__)
time_format = "%Y-%m-%dT%H:%M:%SZ"
HTTP_SUCCESS_CODE = 200
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"


def last_day_of_month(date: datetime.datetime) -> datetime.datetime:
    """Calculate the last day of the given month."""
    next_month = date.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def sanitize_html(html_content: str, exclude: str | None = None) -> str:
    soup = BeautifulSoup(html_content, "lxml")
    for element in soup.find_all(True):
        if isinstance(element, Tag):
            if element.name in ["style", "script", "svg", "picture"]:
                element.extract()
    if exclude and exclude != "":
        for element in soup.select(exclude):
            element.extract()
    raw_bytes = soup.encode_contents()
    return raw_bytes.decode("utf-8")


async def download_content(
    client: aiohttp.ClientSession,
    entry: dict[str, Any],
    feed: Any,
    *,
    verbose: bool,
) -> tuple[bytes, int, int]:
    # use readability service to extract the content
    proxy = None
    try:
        async with client.get(url=entry["link"], proxy=proxy) as response:
            if verbose:
                logger.info(f"=== queueing {entry['link']}")
            html = await response.read()
            if response.status == HTTP_SUCCESS_CODE:
                retrieved = 1
                failed = 0
                decoded_html = html.decode("utf-8", "ignore")
                content_sanitized = sanitize_html(decoded_html, feed.exclude)
                headers = {"Content-Type": "text/html; charset=UTF-8"}
                r = requests.post(
                    "http://readability:8081?href=" + entry["link"],
                    headers=headers,
                    data=content_sanitized.encode("utf-8"),
                    timeout=30,
                )
                content = r.content
            else:
                content = ""
                retrieved = 0
                failed = 1
                logger.error(
                    f"=== url {entry['link']} returned error status {response.status}",
                )
                if verbose:
                    logger.info("f=== content: {html}")
    except Exception:
        logger.exception(
            f"=== exception while asynchronously retrieving {entry['link']}",
        )
        content = ""
        retrieved = 0
        failed = 1

    return (content, retrieved, failed)


async def retrieve(
    client: aiohttp.ClientSession,
    entry: dict[str, Any],
    feed: Any,
    *,
    verbose: bool,
) -> tuple[int, int, int]:
    retrieved = 0
    failed = 0
    stored = 0
    url = entry["link"]
    if feed.incomplete and entry["link"]:
        content, retrieved, failed = await download_content(
            client,
            entry,
            feed,
            verbose=verbose,
        )
    elif "content" in entry:
        content = b"" if isinstance(entry["content"][0], bytes) else ""
        for c in entry["content"]:
            content += c.value
    elif "summary" in entry:
        content = entry["summary"]
    else:
        failed += 1
        logger.error(f"=== url {url} has no content and no summary")
        return (retrieved, failed, stored)

    decoded_content = content.decode() if isinstance(content, bytes) else content

    if feed.salt_url:
        # add some cruft to the urls so that they are unique
        url = f"{url}#{int(time.time())}"
    if len(decoded_content) > 0:
        parsed_url = urllib.parse.urlparse(url)
        base_url = urllib.parse.urlunsplit(
            (parsed_url.scheme, parsed_url.netloc, "", "", ""),
        )
        author = clean(entry.get("author", "anonimo"))
        normalized_content = normalize_content(decoded_content, base_url, feed.exclude)
        title = clean(entry.get("title", ""))
        article: ArticleDict = {
            "author": author,
            "content": normalized_content,
            "feed_id": feed.id,
            "language": feed.language,
            "stamp": entry.get("stamp", 0),
            "title": title,
            "url": url,
        }
        article_id = await store_article(article)
        if article_id > 0:
            stored += 1
            if verbose:
                logger.info(
                    f"=== new article {entry["link"]} asynchronously stored with id {article_id}",  # noqa: E501
                )
        elif article_id < 0:
            failed += 1
    return (retrieved, failed, stored)


async def main(
    loop: asyncio.AbstractEventLoop,
    entries: list[dict[str, Any]],
    feed: Any,
    *,
    verbose: bool,
) -> list[tuple[int, int, int]]:
    cookies: dict[str, str] = {}
    if feed.cookies and feed.cookies != "":
        cookies_file = feed.cookies.replace("/srv/calo.news/", "/app/")
        # find out if the file exists
        try:
            cj = http.cookiejar.MozillaCookieJar(cookies_file)
            cj.load()
            for c in cj:
                if c.value:
                    cookies[c.name] = c.value
        except Exception:
            logger.exception(f"=== could not load cookies from {cookies_file}")
    headers = {
        "User-Agent": USER_AGENT,
    }
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(
        loop=loop,
        cookies=cookies,
        headers=headers,
        timeout=timeout,
    ) as client:
        return await asyncio.gather(
            *[retrieve(client, entry, feed, verbose=verbose) for entry in entries],
        )


def normalize_structure(soup, exclude):
    # remove blacklisted tags
    for name in [
        "img",
        "figcaption",
        "figure",
        "hr",
        "source",
        "object",
        "video",
        "audio",
        "track",
        "embed",
        "param",
        "map",
        "area",
        "form",
        "input",
        "button",
        "canvas",
        "style",
        "script",
        "svg",
        "picture",
    ]:
        for element in soup.find_all(name):
            element.extract()

    # remove excluded tags
    if exclude and exclude != "":
        for element in soup.select(exclude):
            element.extract()

    # turn divs into paragraphs
    for div in soup.find_all("div"):
        if isinstance(div, Tag):
            div.name = "p"

    # unpack graylisted tags
    for tag in soup.find_all(True):
        if isinstance(tag, Tag):
            if tag.name not in [
                "a",
                "p",
                "i",
                "strong",
                "b",
                "br",
                "table",
                "tr",
                "th",
                "td",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "pre",
                "hr",
                "blockquote",
                "ul",
                "ol",
                "li",
                "dl",
                "dt",
                "dd",
                "em",
                "small",
                "s",
                "cite",
                "code",
                "sub",
                "sup",
                "span",
                "tbody",
                "thead",
                "tfoot",
            ]:
                tag.replaceWithChildren()


def normalize_content(
    content: str,
    base_url: str | None = None,
    exclude: str | None = None,
) -> str:
    html = " ".join(line.strip() for line in content.split("\n"))
    soup = BeautifulSoup(html, "lxml")

    normalize_structure(soup, exclude)

    # normalize links
    if base_url:
        for a in soup.find_all("a", href=True):
            if isinstance(a, Tag):
                a["target"] = "_blank"
                href_value = a["href"]
                if isinstance(href_value, str):
                    parsed_link = urllib.parse.urlparse(href_value)
                    if parsed_link.scheme == "":
                        a["href"] = urllib.parse.urljoin(base_url, href_value)

    # remove duplicate br tags
    for br in soup.find_all("br"):
        if isinstance(br.next_sibling, Tag) and br.next_sibling.name.lower() == "br":
            br.extract()

    # remove comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    # identify top-level element
    if soup.body:
        top = soup.body
    elif soup.html:
        top = soup.html
    else:
        top = soup

    # normalize paragraphs
    new_soup = BeautifulSoup("", "lxml")
    current_paragraph = new_soup.new_tag("p")
    new_soup.append(current_paragraph)
    inline_tags = [
        "a",
        "b",
        "cite",
        "code",
        "em",
        "i",
        "s",
        "small",
        "span",
        "strong",
        "sub",
        "sup",
    ]
    for s in top.children:
        if isinstance(s, NavigableString) or s.name in inline_tags:
            current_paragraph.append(copy.copy(s))
        elif s.name == "p":
            current_paragraph = copy.copy(s)
            new_soup.append(current_paragraph)
        else:
            current_paragraph = new_soup.new_tag("p")
            t = copy.copy(s)
            new_soup.append(t)
            t.wrap(current_paragraph)

    # get rid of br's
    fragment = "".join(str(c) for c in new_soup.contents)
    html = fragment.replace("<br/>", "</p><p>")
    soup = BeautifulSoup(html, "lxml")

    # remove empty paragraphs
    for p in soup.find_all("p"):
        if len(p.get_text(strip=True)) == 0:
            p.extract()

    # flatten
    soup.html.body.unwrap()
    soup.html.unwrap()

    prettified = soup.prettify(formatter="html5")
    decoded = (
        prettified.decode("utf-8") if isinstance(prettified, bytes) else prettified
    )
    # get rid of nbsp
    return decoded.replace("&nbsp;", " ")


def clean(s: str) -> str:
    if s:
        t = html.unescape(s)
        u = lxml.html.fromstring(t)
        return u.text_content()
    return s


class ArticleDict(TypedDict, total=False):
    author: str
    content: str
    feed_id: int
    language: str
    stamp: int
    title: str
    url: str


@sync_to_async
def store_article(
    article: ArticleDict,
) -> int:
    """
    Store an article in the database.
    returns:
    - None on failure
    - a strictly positive integer (the id of the inserted article) on success
    """
    base_language = "it"

    if article["language"] == base_language:
        instance = Articles(
            author=article["author"],
            title=article["title"],
            url=article["url"],
            content=article["content"],
            feed_id=article["feed_id"],
            language=article["language"],
            stamp=article["stamp"],
        )
        instance.save()
        return instance.id

    instance = Articles(
        author=article["author"],
        title_original=article["title"],
        url=article["url"],
        content_original=article["content"],
        feed_id=article["feed_id"],
        language=article["language"],
        stamp=article["stamp"],
    )
    instance.save()
    return instance.id


def frequency_skip(frequency_string: str, feed_id: int) -> str | None:
    # polling will happen only if the current UTC date and time satisfy all
    # conditions; frequency_string is in JSON format:
    #   { "day": [1, 2, 3], "hour": [12, 13], "weekday": [7] })
    # hours are 0-24 in UTC timezone
    # days are the day in the month (a negative number counts from the end)
    # weekdays are the day of the week, where Monday is 1 and Sunday is 7
    frequency = json.loads(frequency_string)
    now = datetime.datetime.now(datetime.UTC)
    hour = now.hour
    day = now.day
    weekday = (
        now.weekday() + 1
    )  # datetime.datetime.weekday returns Monday as 0 and Sunday as 6
    if "hour" in frequency and hour not in frequency["hour"]:
        return f"== skipping feed {feed_id} because frequency = {frequency_string} and hour = {hour}"  # noqa: E501
    if "weekday" in frequency and weekday not in frequency["weekday"]:
        return f"== skipping feed {feed_id} because frequency = {frequency_string} and weekday = {weekday}"  # noqa: E501
    if "day" in frequency:
        ldom = last_day_of_month(now).day
        for i, d in enumerate(frequency["day"]):
            if d < 0:
                frequency["day"][i] = d + ldom + 1
        if day not in frequency["day"]:
            return f"== skipping feed {feed_id} because frequency = {frequency_string} and day = {day}"  # noqa: E501

    return None


def prune_duplicates(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Removes entries with duplicate 'link' values from a list of dictionaries.
    Preserves the first occurrence of each link.
    """
    seen_links = set()
    result = []
    for entry in entries:
        if entry["link"] not in seen_links:
            result.append(entry)
            seen_links.add(entry["link"])
    return result


def prune_already_retrieved(entries: list[dict[str, Any]]) -> int:
    """
    prune in-place the articles we already stored in the DB
    To remove elements from a list while iterating over it, you need to go backwards
    http://stackoverflow.com/a/7573706
    """
    pruned = 0
    for entry in entries[-1::-1]:
        article = Articles.objects.filter(url=entry["link"]).first()
        if article:
            logger.info(
                f"=== article {entry["link"]} already retrieved with id = {article.id}",
            )
            entries.remove(entry)
            pruned += 1

    return pruned


def generate_rss(json_data):
    # Create the RSS header
    rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>News Feed</title>
<link>https://example.com</link>
<description>A collection of news articles</description>
"""

    # Process each item in the JSON data
    for item in json_data:
        # Convert published_at to RSS format if available
        pub_date = ""
        if item.get("published_at"):
            dt = datetime.datetime.strptime(
                item["published_at"],
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ).astimezone(datetime.UTC)
            pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
        else:
            # Use current date/time if none provided
            dt = datetime.datetime.now(pytz.UTC)
            pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")

        # Extract author information
        author = (
            item.get("author_name") or item.get("provider_name") or "Unknown Author"
        )

        # Add the item to the RSS feed
        rss += f"""
<item>
<title>{item['title']}</title>
<link>{item['url']}</link>
<description>{item['description']}</description>
<pubDate>{pub_date}</pubDate>
<author>{author}</author>
"""

        # Add image if available
        if item.get("image"):
            rss += f"""<enclosure url="{item['image']}" type="image/jpeg"/>"""

        rss += "</item>\n"

    # Close the RSS structure
    rss += """
</channel>
</rss>
"""
    return rss


def _fetch_feed_response(feed_url):
    """
    Fetch the feed response with error handling.

    Returns:
        tuple: (response, status_code)
        response will be None if an error occurred
    """
    # -100: unextractable HTTP error status
    # -40: generic exception
    # -30: generic request exception
    # -20: connection error
    # -10: timeout
    # -5: invalid feed
    # 0: default status code
    # 200-5xx: HTTP status code
    try:
        response = requests.get(
            feed_url,
            timeout=60,
            headers={"User-Agent": USER_AGENT},
        )
        status_code = response.status_code
    except requests.exceptions.HTTPError as e:
        logger.exception(f"== http error when reading RSS {feed_url}:")
        status_code = e.response.status_code if e.response is not None else -100
        return None, status_code
    except requests.exceptions.ConnectionError:
        logger.exception(f"== connection error when reading RSS {feed_url}")
        return None, -20
    except requests.exceptions.Timeout:
        logger.exception(f"== timeout when reading RSS {feed_url}")
        return None, -10
    except requests.exceptions.RequestException:
        logger.exception(
            f"== generic request exception when reading RSS {feed_url}",
        )
        return None, -30
    except Exception:  # Catching broader exceptions
        logger.exception(f"== generic exception when reading RSS {feed_url}")
        return None, -40
    else:
        return response, status_code


def _parse_feed_content(feed, response):
    """Parse feed content and handle special cases."""
    if feed.url[-29:] == "/api/v1/trends/links?limit=20":
        json_data = json.loads(response.text)
        rss = generate_rss(json_data)
    else:
        rss = response.text

    return feedparser.parse(rss)


def _process_feed_entries(entries, *, verbose=True):
    """Process, filter and sort feed entries."""
    # Prune duplicate and already retrieved entries
    entries = prune_duplicates(entries)
    prune_already_retrieved(entries)

    if verbose:
        for entry in entries:
            logger.info(f"== to retrieve: {entry['link']}")

    # Add timestamps to entries
    for entry in entries:
        if entry.get("published_parsed"):
            if entry["published_parsed"] > time.gmtime():
                entry["stamp"] = time.strftime(time_format, time.gmtime())
            else:
                entry["stamp"] = time.strftime(
                    time_format,
                    entry["published_parsed"],
                )
        else:
            entry["stamp"] = time.strftime(time_format, time.gmtime())

    # Sort entries by timestamp
    return sorted(entries, key=lambda entry: entry["stamp"])


def _retrieve_and_process_entries(sorted_entries, feed, *, verbose=True):
    """Retrieve and process entries using async."""
    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(
        main(loop, sorted_entries, feed, verbose=verbose),
    )

    retrieved, failed, stored = 0, 0, 0
    for r_item in results:
        retrieved += r_item[0]
        failed += r_item[1]
        stored += r_item[2]

    return retrieved, failed, stored


def _poll_feed(feed):
    verbose = True

    # Initialize variables that will be saved in FeedPoller
    retrieved, failed, stored = 0, 0, 0

    # Fetch feed response with error handling
    response, status_code = _fetch_feed_response(feed.url)

    # If response is None, return early with error status
    if not response:
        return retrieved, failed, stored, status_code

    # Check for HTTP error status code
    if response.status_code != HTTP_SUCCESS_CODE:
        logger.error(f"== url {feed.url} returned error status {response.status_code}")
        return retrieved, failed, stored, status_code

    # Parse feed content
    rss_feed = _parse_feed_content(feed, response)

    # Process feed entries
    sorted_entries = _process_feed_entries(rss_feed["entries"], verbose=verbose)

    # Retrieve and process entries
    retrieved, failed, stored = _retrieve_and_process_entries(
        sorted_entries,
        feed,
        verbose=verbose,
    )

    return retrieved, failed, stored, status_code


class Poller:
    def __init__(self, feed):
        self.stored = 0
        self.retrieved = 0
        self.failed = 0
        self.feed = feed
        self.p = None

    def invoke(self, script):
        self.p = subprocess.Popen(
            script,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        try:
            output = self.p.communicate(timeout=200)
        except subprocess.TimeoutExpired:
            self.p.kill()
            logger.exception(f"== timeout while invoking script {script}")
            return (None, "timeout")
        if self.p.returncode != 0:
            logger.error(f"== code {self.p.returncode} returned by script {script}")
            return (None, "error")
        lines = output[0].decode().split("\n")
        last_line = lines[-1] if lines[-1] else lines[-2]
        return (
            last_line.split(" "),
            None,
        )

    def _should_skip_polling(self):
        """Check if polling should be skipped."""
        if not self.feed.active:
            logger.info(f"== skipping feed {self.feed.id} because non-active")
            return True

        if self.feed.frequency:
            skip_reason = frequency_skip(self.feed.frequency, self.feed.id)
            if skip_reason:
                logger.info(skip_reason)
                return True

        return False

    def _handle_script_polling(self, script_path):
        """Handle script-based polling and return polling results."""
        feed_polling_retrieved_count = 0
        feed_polling_failed_count = 0
        feed_polling_stored_count = 0
        http_status_code = 0

        logger.info(f"== using script {script_path}")
        results, script_status_indicator = self.invoke(script_path)

        if script_status_indicator == "timeout":
            http_status_code = -1  # Script timeout
            # counts remain 0
        elif script_status_indicator == "error":
            # self.p should have been set in invoke
            http_status_code = (
                self.p.returncode if self.p and self.p.returncode is not None else -2
            )
            # counts remain 0
        elif results and len(results) == 3:  # noqa: PLR2004
            try:
                feed_polling_retrieved_count = int(results[0])
                feed_polling_failed_count = int(results[1])
                feed_polling_stored_count = int(results[2])
                if self.p and self.p.returncode == 0:
                    http_status_code = 200
                elif self.p and self.p.returncode is not None:
                    http_status_code = self.p.returncode
                else:  # Should not happen if invoke logic is correct
                    http_status_code = -2  # Generic script error
            except ValueError:
                logger.exception(
                    f"== [{script_path}] output not in integer format: {results}",
                )
                http_status_code = -3  # Script output format error
                # counts remain 0 or partially set if error in later int()
                feed_polling_retrieved_count = 0  # Reset to be safe
                feed_polling_failed_count = 0
                feed_polling_stored_count = 0
        else:
            logger.error(
                f"== [{script_path}] did not return expected output: {results}",
            )
            http_status_code = (
                self.p.returncode if self.p and self.p.returncode is not None else -2
            )  # Generic script error or actual code

        return (
            feed_polling_retrieved_count,
            feed_polling_failed_count,
            feed_polling_stored_count,
            http_status_code,
        )

    def poll(self):
        poll_start_time = datetime.datetime.now(datetime.UTC)
        http_status_code = 0
        # Using new names for counts for this specific poll run
        feed_polling_retrieved_count = 0
        feed_polling_failed_count = 0
        feed_polling_stored_count = 0

        # Check if polling should be skipped
        if self._should_skip_polling():
            return

        logger.info(f"== polling feed {self.feed.id}")

        # Handle either script-based or direct feed polling
        if self.feed.script:
            script_path = self.feed.script.replace("/srv/calo.news/py/", "/app/news/")
            (
                feed_polling_retrieved_count,
                feed_polling_failed_count,
                feed_polling_stored_count,
                http_status_code,
            ) = self._handle_script_polling(script_path)
        else:
            retrieved, failed, stored, status_from_poll = _poll_feed(self.feed)
            feed_polling_retrieved_count = retrieved
            feed_polling_failed_count = failed
            feed_polling_stored_count = stored
            http_status_code = status_from_poll

        poll_end_time = datetime.datetime.now(datetime.UTC)

        # Update database with polling results

        # Update the main Poller instance cumulative counts
        self.retrieved += feed_polling_retrieved_count
        self.failed += feed_polling_failed_count
        self.stored += feed_polling_stored_count

        FeedPolling.objects.create(
            feed=self.feed,
            poll_start_time=poll_start_time,
            poll_end_time=poll_end_time,
            http_status_code=http_status_code,
            articles_retrieved=feed_polling_retrieved_count,
            articles_failed=feed_polling_failed_count,
            articles_stored=feed_polling_stored_count,
        )

        self.feed.last_polled = poll_end_time  # Use poll_end_time for consistency
        self.feed.save()
