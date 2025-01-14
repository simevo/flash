#!/usr/bin/env python3

import datetime
import html
import http.cookiejar
import logging
import random
import sys
import time

import requests
from bs4 import BeautifulSoup

import poller
from news.models import Feeds

time_format = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)

logger.info("== entering")

base_url = "https://rep.repubblica.it/ws/cover.json"
feed_id = 96
length_threshold = 500  # minimum acceptable length for an article
language = "it"

feed = Feeds.objects.filter(id=feed_id).first()
if feed is None:
    logger.error(f"Feed {feed_id} not found")
    sys.exit(1)

cj = http.cookiejar.MozillaCookieJar(f"cookies_{feed_id}.txt")
cj.load()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
}

json = requests.get(base_url, headers=headers, timeout=30).json()
updated = json["feed"]["updated"]
# 2019-05-12T21:56:20Z
updated_dt = datetime.datetime.strptime(updated, time_format).astimezone(datetime.UTC)
entries = []
for z in json["feed"]["zones"]:
    for b in z["blocks"]:
        for e in b["entries"]:
            if "links" in e:
                for li in e["links"]:
                    if li["rel"] == "target-alternate-amp":
                        url = li["href"]
                author = e.get("author", "anonimo")
                if author[:3] == "di ":
                    author = author[3:]
                entries.append(
                    {"author": author, "title": html.unescape(e["title"]), "url": url},
                )
logger.info(f"== {len(entries)} candidates")
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
    logger.info(f"=== retrieving: {e["url"]}")
    html = requests.get(e["url"], cookies=cj, headers=headers, timeout=30).text
    soup = BeautifulSoup(html, "lxml")
    # remove unwanted stuff
    for el in soup.select("amp-analytics"):
        el.extract()
    for el in soup.select(".detail-tag_container"):
        el.extract()
    for el in soup.select("#detail-values_big"):
        el.extract()
    for el in soup.select(".detail-comment_big"):
        el.extract()
    for el in soup.select(".detail-problem"):
        el.extract()
    content = ""
    article_body = soup.select(".paywall")
    for b in article_body:
        content += b.prettify()
    if isinstance(content, bytes):
        content = content.decode()
    if len(content) > length_threshold:
        updated_dt += datetime.timedelta(seconds=1)
        res = poller.store_article(
            author=e["author"],
            title=e["title"],
            url=e["url"],
            content=content,
            feed_id=feed_id,
            language=language,
            stamp=updated_dt.strftime(time_format),
        )
        data["retrieved"] += 1
        if res > 0:
            logger.info("f=== new article {e} stored with id {res}")
            data["stored"] = +1
        else:
            data["failed"] = +1
        for _i in range(random.randint(5, 20)):  # noqa: S311
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")
    else:
        logger.error(f"=== skipping because lenght = {len(content)}")
        data["failed"] += 1

feed.last_polled = datetime.datetime.now(datetime.UTC)
feed.save()

logger.info(f"== done: {data["retrieved"]} {data["failed"]} {data["stored"]}")
