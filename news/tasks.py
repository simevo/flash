import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import connection

import poller
from news.models import Feeds
from news.models import UserArticleLists

logger = logging.getLogger(__name__)
time_format = "%Y-%m-%dT%H:%M:%SZ"
newsfeed_query = """
    WITH u AS (
        SELECT
            whitelist,
            blacklist,
            tags AS my_tags,
            languages AS my_languages
        FROM
            news_profile
        WHERE
            user_id=%s),
    uf AS (
        SELECT
            feed_id,
            rating
        FROM
            news_userfeeds
        WHERE
            user_id=%s),
    f AS (
        SELECT
            id AS feed_id,
            uf.rating AS my_feed_rating
        FROM
            u,
            feeds LEFT JOIN uf ON feeds.id = uf.feed_id
        WHERE
            (
                uf.rating IS NULL OR
                uf.rating >= -4
            ) AND (
                u.my_tags IS NULL
                OR u.my_tags = array[]::text[]
                OR feeds.tags && u.my_tags
            )),
    aaa AS (
        SELECT
            articles.id,
            articles.tsv,
            articles.tsv_simple,
            articles.stamp,
            f.*
        FROM
            u,
            f INNER JOIN articles ON articles.feed_id = f.feed_id
        WHERE
            u.my_languages IS NULL
            OR u.my_languages = array[]::text[]
            OR articles.language = ANY(u.my_languages)
            OR ('it' = ANY(u.my_languages) AND articles.title IS NOT NULL)
        ORDER BY id DESC
        LIMIT 8000),
    ua AS (
        SELECT
            article_id,
            rating,
            read
        FROM
            news_userarticles
        WHERE
            user_id=%s),
    aa AS (
        SELECT
            aaa.*,
            COALESCE(ua.rating, 0) AS my_rating,
            COALESCE(ua.read, FALSE) AS read
        FROM
            aaa
            LEFT JOIN ua ON aaa.id = ua.article_id)
    SELECT
        aa.id,
        aa.stamp,
        COALESCE(
            (
                1 +
                10 * (
                    articles_data.views +
                    articles_data.to_reads +
                    GREATEST(0, articles_data.rating)
                ) +
                10 * (
                    GREATEST(
                        0,
                        aa.my_rating +
                            CASE WHEN feeds.premium THEN 2 ELSE 0 END +
                            COALESCE(my_feed_rating, COALESCE(feeds.rating, 0))
                    )
                )
            ) /
            POWER(
                GREATEST(
                    1.0,
                    EXTRACT(EPOCH FROM (NOW() - aa.stamp))
                ) / (1000 * SQRT(1 + feeds_data.average_time_from_last_post)) -
                LEAST(
                    0,
                    10 * (
                        articles_data.rating +
                        CASE WHEN feeds.premium THEN 2 ELSE 0 END
                    ) +
                    10 * (
                        aa.my_rating +
                        COALESCE(my_feed_rating, COALESCE(feeds.rating, 0))
                    )
                ),
                1.5
            ),
            0
        ) AS score
    FROM
        u,
        aa
        INNER JOIN articles_data ON articles_data.id = aa.id
        INNER JOIN feeds ON aa.feed_id = feeds.id
        INNER JOIN feeds_data ON feeds.id = feeds_data.id
    WHERE
        NOT read
        AND (
                tsv @@
                to_tsquery('pg_catalog.italian', array_to_string(whitelist, '|'))
            OR
                tsv_simple @@
                to_tsquery('pg_catalog.simple', array_to_string(whitelist, '|'))
        )
        AND NOT tsv @@
            to_tsquery('pg_catalog.italian', array_to_string(blacklist, '|'))
        AND NOT tsv_simple @@
            to_tsquery('pg_catalog.simple', array_to_string(blacklist, '|'))
    ORDER BY score DESC, stamp DESC
    LIMIT 100;
"""


@shared_task(time_limit=3550, soft_time_limit=3500)
def poll():
    logger.info("Polling started")
    feeds = Feeds.objects.order_by("id").all()
    for feed in feeds:
        logger.info(f"= Polling feed: {feed.id}")
        p = poller.Poller(feed)
        p.poll()
    logger.info("Polling finished")


@shared_task(time_limit=3550, soft_time_limit=3500)
def precompute():
    logger.info("Precomputing started")
    users = get_user_model().objects.all()
    for user in users:
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
        with connection.cursor() as cursor:
            cursor.execute(newsfeed_query, [user.id, user.id, user.id])
            rows = cursor.fetchall()
            for row in rows:
                article_id = row[0]
                newsfeed_list.articles.add(article_id)
        newsfeed_list.save()
    logger.info("Precomputing finished")
