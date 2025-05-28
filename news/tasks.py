import datetime
import html
import logging
import os
import time

import psycopg
import torch
from bs4 import BeautifulSoup
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchQuery
from django.core.cache import cache
from pgvector.django import CosineDistance
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

import poller
from news.models import Articles
from news.models import Feeds
from news.models import UserArticleLists
from news.models import UserFeeds
from news.services import TextEmbeddingService

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
    cache.clear()


def precompute_user(user, start_timestamp, embedding_service):
    logger.info(f"= Precomputing user: {user.id}")
    newsfeed_list = UserArticleLists.objects.filter(
        user=user,
        name="newsfeed",
    ).first()
    if not newsfeed_list:
        newsfeed_list = UserArticleLists.objects.create(
            user=user,
            name="newsfeed",
            automatic=True,
        )
    newsfeed_list.articles.clear()

    qs = Articles.objects.filter(stamp__gte=start_timestamp)
    filtered = False

    ufe = UserFeeds.objects.filter(user=user, rating=-5)
    exclude_feeds = [o.feed_id for o in ufe]
    if len(exclude_feeds) > 0:
        logger.info(f"== filtering by excluded feeds: {exclude_feeds}")
        qs = qs.exclude(feed_id__in=exclude_feeds)
        filtered = True

    if len(user.profile.languages) > 0:
        logger.info(f"== filtering by languages: {user.profile.languages}")
        qs = qs.filter(language__in=user.profile.languages)
        filtered = True

    if len(user.profile.blacklist) > 0:
        terms = "|".join(user.profile.blacklist)
        logger.info(f"== filtering by blacklist: {terms}")
        query = SearchQuery(terms, search_type="raw", config="pg_catalog.simple")
        qs = qs.exclude(tsv=query)
        filtered = True

    if len(user.profile.whitelist) > 0:
        terms = " ".join(user.profile.whitelist)
        logger.info(f"== filtering by whitelist: {terms}")
        embedding = embedding_service.get_embedding(terms)
        qs = qs.order_by(
            CosineDistance(
                "use_cmlm_multilingual",
                embedding,
            ),
        )[:10000]
        filtered = True

    if filtered:
        sorted_articles = sorted(qs, key=lambda a: a.id, reverse=True)
        for article in list(sorted_articles)[:200]:
            newsfeed_list.articles.add(article.id)

    newsfeed_list.save()


@shared_task(time_limit=1750, soft_time_limit=1600)
def precompute():
    logger.info("Precomputing started")
    one_month_ago = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=30)
    embedding_service = TextEmbeddingService()
    users = get_user_model().objects.all()
    for user in users:
        precompute_user(user, one_month_ago, embedding_service)

    logger.info("Precomputing finished")


def clean_html(raw_html):
    # Remove HTML tags
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    # Convert HTML entities to characters
    return html.unescape(text)


def embed(n):
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = os.environ["POSTGRES_PORT"]
    postgres_db = os.environ["POSTGRES_DB"]
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]

    with psycopg.connect(
        conninfo=f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}",
        row_factory=dict_row,
    ) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            logger.info(f"  ========== embedding {n} records")
            cur.execute(
                """
                SELECT COUNT(*)
                FROM articles
                WHERE use_cmlm_multilingual IS NOT NULL
                """,
            )
            before = cur.fetchone()
            logger.info(f"  processed articles before: {before['count']}")

            start_time = time.perf_counter()
            cur.execute(
                """
                SELECT
                    id,
                    (CASE
                        WHEN language = 'it' THEN title
                        ELSE title_original END
                    ) as title,
                    (CASE
                        WHEN language = 'it' THEN content
                        ELSE content_original END
                    ) AS content
                FROM articles
                WHERE use_cmlm_multilingual IS NULL
                ORDER BY id DESC
                LIMIT %(n)s
                """,
                {"n": n},
            )
            articles = cur.fetchall()

            sentences = [
                article["title"] + " - " + clean_html(article["content"])
                for article in articles
            ]
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.info(f"  DB reading took: {execution_time:.4f} seconds")

            start_time = time.perf_counter()

            embedding_service = TextEmbeddingService()
            embeddings_use_cmlm_multilingual = embedding_service.get_embedding(
                sentences,
            )

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.info(f"  model encode: {execution_time:.4f} seconds")

    start_time = time.perf_counter()

    with psycopg.connect(
        conninfo=f"postgresql://no_triggers:no_triggers@{postgres_host}:{postgres_port}/{postgres_db}",
    ) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TEMPORARY TABLE articles_temp (
                    id INTEGER,
                    use_cmlm_multilingual halfvec
                ) ON COMMIT DROP
            """,
            )

            with cur.copy(
                """
                COPY articles_temp (
                        id,
                        use_cmlm_multilingual
                    )
                FROM STDIN WITH (FORMAT BINARY)""",
            ) as copy:
                # use set_types for binary copy
                # https://www.psycopg.org/psycopg3/docs/basic/copy.html#binary-copy
                copy.set_types(["integer", "halfvec", "halfvec"])

                for index, article in enumerate(articles):
                    copy.write_row(
                        [
                            article["id"],
                            embeddings_use_cmlm_multilingual[index],
                        ],
                    )

            cur.execute(
                """
                UPDATE articles a
                SET use_cmlm_multilingual = t.use_cmlm_multilingual
                FROM articles_temp t
                WHERE a.id = t.id
                """,
            )

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.info(f"  DB writing: {execution_time:.4f} seconds")

            cur.execute(
                """
                SELECT COUNT(*)
                FROM articles
                WHERE use_cmlm_multilingual IS NOT NULL
                """,
            )
            after = cur.fetchone()
            logger.info(f"  processed articles after: {after[0]}")
            return len(articles)


@shared_task(time_limit=1750, soft_time_limit=1600)
def embeddings():
    logger.info(f"Embedding started at: {datetime.datetime.now(tz=datetime.UTC)}")
    logger.info(f"= PyTorch Version: {torch.__version__}")
    logger.info(f"= CPU Available: {torch.cpu.is_available()}")
    logger.info(f"= GPU Available: {torch.cuda.is_available()}")
    logger.info(
        f"= Apple M1 MPS available: {torch.backends.mps.is_available()}",
    )

    iterations = 1000
    articles_per_iterations = 1000
    for i in range(iterations):
        logger.info(f"= Loop {i}")
        try:
            updated = embed(articles_per_iterations)
            if updated < articles_per_iterations:
                break
        except ConnectionError:
            logging.exception("Database connection error")
        except Exception:
            logging.exception("Generic exception")

    logger.info(f"Embedding completed at: {datetime.datetime.now(tz=datetime.UTC)}")


@shared_task(time_limit=3550, soft_time_limit=3500)
def run_mastodon_bots():
    """
    Celery task to run the Mastodon bot for all configured bot users.
    """
    logger.info("Starting Mastodon bots run...")

    # Import here to avoid circular dependencies if models are initializing
    # and because this task is the primary user of these models in this file.
    from django.contrib.auth.models import User

    from flash.bots.mastodon_bot import main as run_bot_for_user

    # Filter users who are bot users and have all Mastodon credentials configured
    eligible_users = (
        User.objects.filter(
            profile__is_bot_user=True,
            profile__mastodon_client_id__isnull=False,
            profile__mastodon_client_secret__isnull=False,
            profile__mastodon_access_token__isnull=False,
            profile__mastodon_api_base_url__isnull=False,
        )
        .exclude(profile__mastodon_client_id__exact="")
        .exclude(profile__mastodon_client_secret__exact="")
        .exclude(profile__mastodon_access_token__exact="")
        .exclude(profile__mastodon_api_base_url__exact="")
    )

    if not eligible_users.exists():
        logger.info("No users configured for Mastodon bot. Exiting.")
        return

    logger.info(f"Found {eligible_users.count()} user(s) configured for Mastodon bot.")

    for user in eligible_users:
        logger.info(f"Running Mastodon bot for user: {user.username} (ID: {user.id})")
        try:
            run_bot_for_user(user.id)
            logger.info(f"Successfully ran Mastodon bot for user: {user.username}")
        except Exception:
            msg = f"Error running Mastodon bot for user {user.username}"
            logger.exception(msg)

    logger.info("Finished Mastodon bots run.")
