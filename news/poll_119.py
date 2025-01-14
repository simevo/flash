#!/usr/bin/env python3

import datetime
import http.cookiejar
import locale
import logging
import random
import sys
import time

import requests
import rewire
from bs4 import BeautifulSoup
from bs4 import NavigableString

import poller
from news.models import Feeds

logger = logging.getLogger(__name__)

logger.info("== entering")

cj = http.cookiejar.MozillaCookieJar("cookies_119.txt")
cj.load()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",  # noqa: E501
    "Accept": "text/html,application/xhtml+xml,aplication/xml;q=0.9,*/*;q=0.8",
}

feed_id = 119

feed = Feeds.objects.filter(id=feed_id).first()
if feed is None:
    logger.error(f"Feed {feed_id} not found")
    sys.exit(1)

loc = locale.getlocale()
locale.setlocale(locale.LC_TIME, "it_IT.utf8")
base_url = "https://www.lindiceonline.com"
my = datetime.datetime.now(datetime.UTC).strftime("%B-%Y")
url0 = f"{base_url}/l-indice/sommario/{my}/"
logger.info("== url0 = {url0}")
locale.setlocale(locale.LC_TIME, loc)

html = requests.get(url0, cookies=cj, headers=headers, timeout=30).text
soup = BeautifulSoup(html, "lxml")
entries = [url0]

for a in soup.select("div.post-content > .p2 a"):
    url = a.get("href")
    if url[0] == "/":
        url = base_url + url
    entries.append(url)
unique_entries = set(entries)
entries = sorted(unique_entries)

data = {}
data["feed_id"] = feed_id
data["count"] = len(entries)

poller.prune_already_retrieved(entries)

data["to_retrieve"] = len(entries)
data["non_articles"] = 0
data["retrieved"] = 0
data["failed"] = 0
data["stored"] = 0
for e in entries:
    logger.info(f"== to retrieve: {e}")
    html = requests.get(e, cookies=cj, headers=headers, timeout=30).text

    soup = BeautifulSoup(html, "lxml")

    try:
        stamp = soup.select('meta[property="article:published_time"]')[0].get("content")
        logger.info("f=== stamp = {stamp}")
        title = soup.select("h1.post-title")[0].get_text().strip()
        logger.info("f=== title = {title}")
        try:
            author = (
                soup.select(
                    "div.post-container.cf > div > div > p:nth-of-type(2) > strong",
                )[0]
                .get_text()
                .strip()
            )
        except IndexError:
            author = "Redazione"
        logger.info(f"=== author = {author}")
        contents = soup.select("div[itemprop=articleBody]")[0].contents[6:]
        content = ""
        for c in contents:
            c1 = c if isinstance(c, NavigableString) else c.prettify()
            if isinstance(c1, bytes):
                c1 = c1.decode()
            content += c1
        logger.info(f"=== {content[:100]}")

        MIN_CONTENT_LENGTH = 50

        if len(content) > MIN_CONTENT_LENGTH:
            res = poller.store_article(
                author=author,
                title=title,
                url=e,
                content=content,
                feed_id=feed_id,
                language="it",
                stamp=stamp,
            )
            data["retrieved"] += 1
            if res > 0:
                logger.info(f"=== new article {e} stored with id {res}")
                data["stored"] = +1
            else:
                data["failed"] = +1
            for _i in range(random.randint(5, 20)):  # noqa: S311
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\n")
        else:
            logger.info(f"=== skipping because length = {len(content)}")
            data["failed"] += 1
    except IndexError:
        logger.exception("=== skipping because could not find required keys")
        data["failed"] += 1
    except Exception:
        logger.exception(f"=== skipping because of exception: {e}")
        data["failed"] += 1

id0 = rewire.lookup(url0)
rewire.rewire_article(id0)

feed.last_polled = datetime.datetime.now(datetime.UTC)
feed.save()

logger.info(f"== done: {data["retrieved"]} {data["failed"]} {data["stored"]}")
