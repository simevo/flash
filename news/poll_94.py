#!/usr/bin/env python3

import datetime
import logging
import sys
import time
from pathlib import Path

import requests

import poller
from news.models import Feeds


def secret():
    if secret.cached == "":
        try:
            with Path.open("secrets/94.jwt") as secret_file:
                secret.cached = secret_file.read().strip("\n")
        except OSError:
            return ""
    return secret.cached


secret.cached = ""

logger = logging.getLogger(__name__)

logger.info("== entering")

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://app.goodmorningitalia.it/briefing/",
    "Authorization": f"Bearer {secret()}",
    "Origin": "https://app.goodmorningitalia.it",
}

feed_id = 94
length_threshold = 2000  # minimum acceptable length for an article
language = "it"

feed = Feeds.objects.filter(id=feed_id).first()
if feed is None:
    logger.error(f"Feed {feed_id} not found")
    sys.exit(1)

date = time.strftime("%Y-%m-%d", time.gmtime())
url = f"https://api.goodmorningitalia.it/sync-news/?date_published[$gt]={date}00:00:00%20&date_published[$lt]={date}%2023:59:59"
json = requests.get(url, headers=headers, timeout=30).json()
url = json["data"]["url"]
title = json["data"]["title"]
content = json["data"]["content_html"]
data = {
    "feed_id": feed_id,
    "count": 1,
    "to_retrieve": "?",
    "non_articles": 0,
    "retrieved": 0,
    "failed": 0,
    "stored": 0,
}
if len(content) > length_threshold:
    data["retrieved"] = 1
    res = poller.store_article(
        author="redazione",
        title=title,
        url=url,
        content=content,
        feed_id=feed_id,
        language=language,
    )
    if res > 0:
        logger.info("f=== new article {e} stored with id {res}")
        data["stored"] = 1
    else:
        data["failed"] = 1
else:
    data["failed"] = 1
    logger.error(f"=== skipping because lenght = {len(content)}")

feed.last_polled = datetime.datetime.now(datetime.UTC)
feed.save()

logger.info(f"== done: {data["retrieved"]} {data["failed"]} {data["stored"]}")
