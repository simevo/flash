#!/usr/bin/env python3

import datetime
import logging
import random
import sys
import time

import dateparser
import requests
from bs4 import BeautifulSoup

import poller
from news.models import Feeds

logger = logging.getLogger(__name__)

logger.info("== entering")

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
}

base_url = "https://www.doppiozero.com/"
feed_id = 39

feed = Feeds.objects.filter(id=feed_id).first()
if feed is None:
    logger.error(f"Feed {feed_id} not found")
    sys.exit(1)

html = requests.get(base_url, headers=headers, timeout=30).text
soup = BeautifulSoup(html, "lxml")
entries = []

for a in soup.select("article a"):
    url = a.get("href")
    if len(url) > 0:
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
    html = requests.get(e, headers=headers, timeout=30).text
    soup = BeautifulSoup(html, "lxml")
    stamps = soup.select("#block-mainpagecontent > article div.data-articolo")
    if len(stamps) == 1:
        stamp = dateparser.parse(stamps[0].get_text())
        title = soup.select("#block-mainpagecontent > article .titolo-articolo")[
            0
        ].get_text()
        author = soup.select("#block-mainpagecontent > article .autori")[0].get_text()
        content = soup.select("#block-mainpagecontent > article .text-formatted")[
            0
        ].prettify()
        if isinstance(content, bytes):
            content = content.decode()
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
            logger.info("f=== new article {e} stored with id {res}")
        for _i in range(random.randint(5, 20)):  # noqa: S311
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")

feed.last_polled = datetime.datetime.now(datetime.UTC)
feed.save()

logger.info(f"== done: {data["retrieved"]} {data["failed"]} {data["stored"]}")
