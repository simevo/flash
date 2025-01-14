#!/usr/bin/env python3

import logging
import sys

import poller
from news.models import Feeds

urls = [
    "https://www.foreignaffairs.com/rss.xml",
    "https://www.foreignaffairs.com/feeds/region/Africa/rss.xml",
    "https://www.foreignaffairs.com/feeds/region/Americas/rss.xml",
    "https://www.foreignaffairs.com/feeds/region/Asia/rss.xml",
    "https://www.foreignaffairs.com/feeds/region/Europe/rss.xml",
    "https://www.foreignaffairs.com/feeds/region/World/rss.xml",
]
retrieved = 0
failed = 0
stored = 0

logger = logging.getLogger(__name__)

logger.info("== entering")

feed_id = 98
feed = Feeds.objects.filter(id=feed_id).first()
if feed is None:
    logger.error(f"Feed {feed_id} not found")
    sys.exit(1)

for url in urls:
    logger.info(f"=== processing url {url}")
    feed.url = url
    feed.script = ""
    p = poller.Poller(feed)
    p.poll()
    retrieved += p.__dict__["retrieved"]
    failed += p.__dict__["failed"]
    stored += p.__dict__["stored"]

logger.info(f"== done: {retrieved} {failed} {stored}")
