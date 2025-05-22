import os

import django
from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django.setup()

from news.tasks import embeddings  # noqa: E402
from news.tasks import poll  # noqa: E402
from news.tasks import precompute  # noqa: E402
from news.tasks import run_mastodon_bots # noqa: E402

app = Celery("flash")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="04"),
        poll.s(),
        name="poll feeds",
    )
    sender.add_periodic_task(
        crontab(minute="34"),
        precompute.s(),
        name="precompute",
    )
    sender.add_periodic_task(
        crontab(minute="44"),
        embeddings.s(),
        name="embeddings",
    )
    sender.add_periodic_task(
        crontab(minute='0', hour='*/1'), # Runs at the start of every hour
        run_mastodon_bots.s(),
        name="run mastodon bots hourly",
    )
    # Add logging to confirm task scheduling
    # Ensure logger is configured to see this message, or use print for simplicity if appropriate
    # For Celery, logging is generally preferred.
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Scheduled run_mastodon_bots task to run hourly.")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
