import logging

from celery import shared_task

import poller
from news.models import Feeds

logger = logging.getLogger(__name__)
time_format = "%Y-%m-%dT%H:%M:%SZ"


@shared_task(time_limit=3550, soft_time_limit=3500)
def poll():
    logger.info("Polling started")
    feeds = Feeds.objects.order_by("id").all()
    for feed in feeds:
        logger.info(f"= Polling feed: {feed.id}")
        p = poller.Poller(feed)
        p.poll()
    logger.info("Polling finished")
