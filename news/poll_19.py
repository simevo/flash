#!/usr/bin/env python3

import logging
import sys

import poller
from news.models import Feeds

urls = [
    "http://www.piemonteparchi.it/cms/index.php/parchi-piemontesi?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/parchi-altrove?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/territorio?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/natura?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/ambiente?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/altri-argomenti?format=feed",
    "http://www.piemonteparchi.it/cms/cms/index.php/rubriche?format=feed",
    "http://www.piemonteparchi.it/cms/index.php/news?format=feed",
]
retrieved = 0
failed = 0
stored = 0

logger = logging.getLogger(__name__)

logger.info("== entering")

feed = Feeds.objects.filter(id=19).first()
if feed is None:
    logger.error("Feed 19 not found")
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
