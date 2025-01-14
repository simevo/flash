# ruff: noqa: S603, PLR0913, C901, ASYNC210, S110, PLR0912, FBT003

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

import aiohttp
import feedparser
import lxml.html
import requests
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import NavigableString
from bs4 import Tag

from news.models import Articles

logger = logging.getLogger(__name__)
time_format = "%Y-%m-%dT%H:%M:%SZ"
HTTP_SUCCESS_CODE = 200


# https://stackoverflow.com/a/13565185
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(
        days=4,
    )  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)


def sanitize(html, exclude):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(True):
        if tag.name in ["style", "script", "svg", "picture"]:
            tag.extract()
    if exclude and exclude != "":
        for element in soup.select(exclude):
            element.extract()
    return soup.prettify()


async def download_content(client, e, feed, verbose):
    # use readability service to extract the content
    proxy = None
    try:
        async with client.get(url=e.link, proxy=proxy) as response:
            if verbose:
                logger.info(f"=== queueing {e.link}")
            html = await response.read()
            if response.status == HTTP_SUCCESS_CODE:
                retrieved = 1
                failed = 0
                html = html.decode("utf-8", "ignore")
                content_sanitized = sanitize(html, feed.exclude)
                headers = {"Content-Type": "text/html; charset=UTF-8"}
                r = requests.post(
                    "http://readability:8081?href=" + e.link,
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
                    f"=== url {e.link} returned error status {response.status}",
                )
                if verbose:
                    logger.info("f=== content: {html}")
    except Exception:
        logger.exception(f"=== exception while asynchronously retrieving {e.link}")
        content = ""
        retrieved = 0
        failed = 1

    return (content, retrieved, failed)


async def retrieve(client, e, feed, verbose):
    retrieved = 0
    failed = 0
    stored = 0
    content = ""
    url = e["link"]
    if feed.incomplete and e.link:
        content, retrieved, failed = await download_content(client, e, feed, verbose)
    elif "content" in e:
        for c in e["content"]:
            content += c.value
    elif "summary" in e:
        content = e["summary"]
    else:
        failed += 1
        logger.error(f"=== url {url} has no content and no summary")

    if isinstance(content, bytes):
        content = content.decode()

    if feed.salt_url:
        # add some cruft to the urls so that they are unique
        url = f"{url}#{int(time.time())}"
    if len(content) > 0:
        article_id = await store_article(
            author=e.get("author", "anonimo"),
            title=e.get("title", ""),
            url=url,
            content=content,
            feed_id=feed.id,
            language=feed.language,
            stamp=e.get("stamp", 0),
            salt_url=feed.salt_url,
            exclude=feed.exclude,
        )
        if article_id > 0:
            stored += 1
            if verbose:
                logger.info(
                    f"=== new article {e["link"]} asynchronously stored with id {article_id}",  # noqa: E501
                )
        elif article_id < 0:
            failed += 1
    return (retrieved, failed, stored)


async def main(loop, entries, feed, verbose):
    cookies = {}
    if feed.cookies and feed.cookies != "":
        cookies_file = feed.cookies.replace("/srv/calo.news/", "/app/")
        # find out if the file exists
        try:
            cj = http.cookiejar.MozillaCookieJar(cookies_file)
            cj.load()
            for c in cj:
                cookies[c.name] = c.value
        except Exception:
            logger.exception(f"=== could not load cookies from {cookies_file}")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
    }
    async with aiohttp.ClientSession(
        loop=loop,
        cookies=cookies,
        headers=headers,
    ) as client:
        return await asyncio.gather(
            *[retrieve(client, e, feed, verbose) for e in entries],
        )


def normalize(content, base_url=None, exclude=None):
    html = " ".join(line.strip() for line in content.split("\n"))
    soup = BeautifulSoup(html, "lxml")

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
        div.name = "p"

    # unpack graylisted tags
    for tag in soup.find_all(True):
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

    # normalize links
    if base_url:
        for a in soup.find_all("a", href=True):
            a["target"] = "_blank"
            parsed_link = urllib.parse.urlparse(a["href"])
            if parsed_link.scheme == "":
                a["href"] = urllib.parse.urljoin(base_url, a["href"])

    # remove duplicate br tags
    for br in soup.find_all("br"):
        if isinstance(br.next_sibling, Tag) and br.next_sibling.name.lower() == "br":
            br.extract()

    # remove comments
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
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
    for s in top.contents:
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
    pretty = soup.prettify(formatter="html5")
    # get rid of nbsp
    return pretty.replace("&nbsp;", " ")


def clean(s):
    t = html.unescape(s)
    u = lxml.html.fromstring(t)
    return u.text_content()


# returns:
# - -1 on failure
# - a strictly positive integer (the id of the inserted article) on success
@sync_to_async
def store_article(
    author,
    title,
    url,
    content,
    feed_id,
    language,
    stamp=0,
    salt_url=None,
    exclude=None,
):
    parsed_url = urllib.parse.urlparse(url)
    base_url = urllib.parse.urlunsplit(
        (parsed_url.scheme, parsed_url.netloc, "", "", ""),
    )
    content = normalize(content, base_url, exclude)
    if author:
        author = clean(author)
    if title:
        title = clean(title)
    if stamp == 0:
        stamp = time.strftime(time_format, time.gmtime())

    base_language = "it"

    if language == base_language:
        article = Articles(
            author=author,
            title=title,
            url=url,
            content=content,
            feed_id=feed_id,
            language=language,
            stamp=stamp,
        )
        article.save()
        return article.id

    article = Articles(
        author=author,
        title_original=title,
        url=url,
        content_original=content,
        feed_id=feed_id,
        language=language,
        stamp=stamp,
    )
    article.save()
    return article.id


def frequency_skip(frequency_string, feed_id):
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


def prune_already_retrieved(entries):
    # prune from the feed the articles we already pulled
    # To remove elements from a list while iterating over it, you need to go backwards
    # http://stackoverflow.com/a/7573706
    pruned = 0
    for e in entries[-1::-1]:
        article = Articles.objects.filter(url=e["link"]).first()
        if article:
            logger.info(
                f"=== article {e["link"]} already retrieved with id = {article.id}",
            )
            entries.remove(e)
            pruned += 1

    return pruned


def poll_feed(feed):
    verbose = True
    try:
        response = requests.get(feed.url, timeout=30)
    except requests.ReadTimeout:
        logger.exception(f"== timeout when reading RSS {feed.url}")
        return (0, 0, 0)
    except Exception:
        logger.exception(f"== exception when reading RSS {feed.url}")
        return (0, 0, 0)
    if response.status_code != HTTP_SUCCESS_CODE:
        logger.error(f"== url {feed.url} returned error status {response.status_code}")
        return (0, 0, 0)
    rss = response.text
    rss_feed = feedparser.parse(rss)

    prune_already_retrieved(rss_feed["entries"])

    if verbose:
        for e in rss_feed["entries"]:
            logger.info(f"== to retrieve: {e['link']}")

    for e in rss_feed["entries"]:
        if e.get("published_parsed"):
            if e["published_parsed"] > time.gmtime():
                e["stamp"] = time.strftime(time_format, time.gmtime())
            else:
                e["stamp"] = time.strftime(time_format, e["published_parsed"])
        else:
            e["stamp"] = time.strftime(time_format, time.gmtime())

    entries = sorted(rss_feed["entries"], key=lambda e: e["stamp"])
    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(
        main(loop, entries, feed, verbose),
    )
    retrieved = failed = stored = 0
    for r in results:
        retrieved += r[0]
        failed += r[1]
        stored += r[2]

    return (retrieved, failed, stored)


class Poller:
    verbose = False

    def __init__(self, feed):
        self.stored = 0
        self.retrieved = 0
        self.failed = 0
        self.feed = feed

    def invoke(self, script):
        p = subprocess.Popen(
            script,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        try:
            output = p.communicate(timeout=200)
        except subprocess.TimeoutExpired:
            p.kill()
            logger.exception(f"== timeout while invoking script {script}")
            return (0, 0, 0)
        if p.returncode != 0:
            logger.error(f"== code {p.returncode} returned by script {script}")
            return (0, 0, 0)
        lines = output[0].decode().split("\n")
        last_line = lines[-1] if lines[-1] else lines[-2]
        return last_line.split(" ")

    def poll(self):
        if not self.feed.active:
            logger.info("== skipping feed {feed.id} because non-active")
            return

        if self.feed.frequency:
            skip_reason = frequency_skip(self.feed.frequency, self.feed.id)
            if skip_reason:
                logger.info(skip_reason)
                return

        logger.info(f"== polling feed {self.feed.id}")

        if self.feed.script:
            script = self.feed.script.replace("/srv/calo.news/py/", "/app/news/")
            logger.info(f"== using script {script}")
            results = self.invoke(script)
            if results and len(results) == 3:  # noqa: PLR2004
                self.retrieved += int(results[0])
                self.failed += int(results[1])
                self.stored += int(results[2])
        else:
            results = poll_feed(self.feed)
            self.retrieved += results[0]
            self.failed += results[1]
            self.stored += results[2]

        self.feed.last_polled = datetime.datetime.now(datetime.UTC)
        self.feed.save()
