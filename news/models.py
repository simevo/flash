import datetime
import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from pgvector.django import HalfVectorField


class ArticleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .defer(
                "paraphrase_multilingual_mpnet_base_v2",
                "use_cmlm_multilingual",
                "tsv",
            )
        )


class Articles(models.Model):
    stamp = models.DateTimeField(default=datetime.datetime.now)
    author = models.TextField(blank=True, null=True)  # noqa: DJ001
    title_original = models.TextField(blank=True, null=True)  # noqa: DJ001
    title = models.TextField(blank=True, null=True)  # noqa: DJ001
    content_original = models.TextField(blank=True, null=True)  # noqa: DJ001
    content = models.TextField(blank=True, null=True)  # noqa: DJ001
    language = models.TextField(blank=True, null=True)  # noqa: DJ001
    url = models.TextField(unique=True, blank=True, null=True)
    feed = models.ForeignKey("Feeds", models.DO_NOTHING)
    paraphrase_multilingual_mpnet_base_v2 = HalfVectorField(dimensions=768)
    use_cmlm_multilingual = HalfVectorField(dimensions=768)
    tsv = SearchVectorField(null=True)

    objects = ArticleManager()

    class Meta:
        managed = False
        db_table = "articles"

    def __str__(self):
        return f"{self.id}"


class GuestArticles(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.OneToOneField(Articles, models.CASCADE)
    views = models.BigIntegerField()

    def __str__(self):
        return f"{self.id}"


class ArticlesData(models.Model):
    id = models.OneToOneField(
        "Articles",
        models.DO_NOTHING,
        primary_key=True,
        db_column="id",
    )
    views = models.BigIntegerField()
    rating = models.FloatField()
    to_reads = models.FloatField()
    length = models.IntegerField()
    excerpt = models.TextField(null=True)  # noqa: DJ001

    class Meta:
        managed = False
        db_table = "articles_data"

    def __str__(self):
        return f"{self.id}"


class ArticlesCombined(models.Model):
    id = models.BigIntegerField(primary_key=True)
    stamp = models.DateTimeField()
    author = models.TextField(blank=True, null=True)  # noqa: DJ001
    title_original = models.TextField(blank=True, null=True)  # noqa: DJ001
    title = models.TextField(blank=True, null=True)  # noqa: DJ001
    content_original = models.TextField(blank=True, null=True)  # noqa: DJ001
    content = models.TextField(blank=True, null=True)  # noqa: DJ001
    language = models.TextField(blank=True, null=True)  # noqa: DJ001
    url = models.TextField(unique=True, blank=True, null=True)
    feed = models.ForeignKey("Feeds", models.DO_NOTHING)
    views = models.BigIntegerField()
    rating = models.FloatField()
    to_reads = models.FloatField()
    length = models.IntegerField()
    excerpt = models.TextField(null=True)  # noqa: DJ001
    paraphrase_multilingual_mpnet_base_v2 = HalfVectorField(dimensions=768)
    use_cmlm_multilingual = HalfVectorField(dimensions=768)
    tsv = SearchVectorField(null=True)

    objects = ArticleManager()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "articles_combined"

    def __str__(self):
        return f"{self.id}"


class Feeds(models.Model):
    homepage = models.TextField()
    url = models.TextField(unique=True)
    language = models.TextField()
    title = models.TextField()
    license = models.TextField(blank=True, null=True)  # noqa: DJ001
    active = models.BooleanField(blank=True, null=True)
    last_polled = models.DateTimeField(blank=True, null=True)
    incomplete = models.BooleanField(blank=True, null=True)
    salt_url = models.BooleanField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    premium = models.BooleanField(blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)  # noqa: DJ001
    exclude = models.TextField(blank=True, null=True)  # noqa: DJ001
    main = models.TextField(blank=True, null=True)  # noqa: DJ001
    tor = models.BooleanField(blank=True, null=True)
    asy = models.BooleanField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)  # noqa: DJ001
    frequency = models.TextField(blank=True, null=True)  # noqa: DJ001
    tags = ArrayField(models.TextField(), blank=True, null=True)

    class Meta:
        managed = False
        db_table = "feeds"
        verbose_name_plural = "feeds"
        verbose_name = "feed"

    def __str__(self):
        return f"{self.id} - {self.title}"


class FeedPolling(models.Model):
    feed = models.ForeignKey(
        Feeds,
        on_delete=models.CASCADE,
        related_name="polling_stats",
    )
    poll_start_time = models.DateTimeField()
    poll_end_time = models.DateTimeField()
    http_status_code = models.IntegerField()
    articles_retrieved = models.IntegerField()
    articles_failed = models.IntegerField()
    articles_stored = models.IntegerField()

    class Meta:
        managed = True

    def __str__(self):
        return f"{self.feed.title} - {self.poll_start_time}"


class FeedIcons(models.Model):
    id = models.AutoField(primary_key=True)
    feed = models.OneToOneField(Feeds, models.CASCADE)
    image = models.ImageField(
        upload_to="icons/",
    )
    stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


class FeedsCombined(models.Model):
    id = models.IntegerField(primary_key=True)
    homepage = models.TextField()
    url = models.TextField()
    language = models.TextField()
    title = models.TextField()
    license = models.TextField(blank=True, null=True)  # noqa: DJ001
    active = models.BooleanField(blank=True, null=True)
    last_polled = models.DateTimeField(blank=True, null=True)
    incomplete = models.BooleanField(blank=True, null=True)
    salt_url = models.BooleanField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    premium = models.BooleanField(blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)  # noqa: DJ001
    exclude = models.TextField(blank=True, null=True)  # noqa: DJ001
    main = models.TextField(blank=True, null=True)  # noqa: DJ001
    tor = models.BooleanField(blank=True, null=True)
    asy = models.BooleanField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)  # noqa: DJ001
    frequency = models.TextField(blank=True, null=True)  # noqa: DJ001
    tags = ArrayField(models.TextField(), blank=True, null=True)
    last_polled_epoch = models.FloatField(blank=True, null=True)
    article_count = models.BigIntegerField(blank=True, null=True)
    average_time_from_last_post = models.IntegerField(blank=True, null=True)
    image = models.TextField(blank=False, null=False)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "feeds_combined"

    def __str__(self):
        return f"{self.id}"


class FeedsData(models.Model):
    id = models.IntegerField(primary_key=True)
    last_polled_epoch = models.FloatField(blank=True, null=True)
    article_count = models.BigIntegerField(blank=True, null=True)
    average_time_from_last_post = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "feeds_data"

    def __str__(self):
        return f"{self.id}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    newsletter = models.BooleanField(default=False)
    list_email = models.TextField(blank=True)
    list_frequency = models.TextField(default="daily")
    list_news = models.IntegerField(default=10)
    list_format = models.TextField(default="pdf")
    whitelist = ArrayField(models.TextField(), default=list, blank=True)
    whitelist_authors = ArrayField(models.TextField(), default=list, blank=True)
    blacklist = ArrayField(models.TextField(), default=list, blank=True)
    blacklist_authors = ArrayField(models.TextField(), default=list, blank=True)
    sociality_weight = models.IntegerField(default=0)
    gravity = models.FloatField(default=2.0)
    age_divider = models.FloatField(default=100.0)
    feed_weight = models.IntegerField(default=0)
    list_weight = models.IntegerField(default=0)
    last_access = models.DateTimeField(blank=True, null=True)
    bow = models.JSONField(default=dict)
    tags = ArrayField(models.TextField(), default=list, blank=True)
    languages = ArrayField(models.TextField(), default=list, blank=True)
    list_hour = models.IntegerField(default=7)
    list_fulltext = models.BooleanField(default=False)
    is_bot_user = models.BooleanField(default=False)
    mastodon_client_id = models.TextField(blank=True)
    mastodon_client_secret = models.TextField(blank=True)
    mastodon_access_token = models.TextField(blank=True)
    mastodon_api_base_url = models.TextField(blank=True)
    mastodon_list_name = models.TextField(
        blank=True,
        default="newsfeed",
        help_text="The name of the UserArticleList to publish to Mastodon.",
    )

    def __str__(self):
        return f"{self.id}"


class UserArticleLists(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.TextField()
    articles = models.ManyToManyField(Articles, through="ArticleLists")
    automatic = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "name"),)

    def __str__(self):
        return f"{self.id}"


class ArticleLists(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Articles, models.CASCADE)
    list = models.ForeignKey(UserArticleLists, models.CASCADE)

    def __str__(self):
        return f"{self.id}"


class UserArticles(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    article = models.ForeignKey(Articles, models.CASCADE)
    read = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    dismissed = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "article"),)

    def __str__(self):
        return f"{self.id}"


class UserFeeds(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    feed = models.ForeignKey(Feeds, models.CASCADE)
    rating = models.IntegerField(default=0)

    class Meta:
        unique_together = (("user", "feed"),)

    def __str__(self):
        return f"{self.id}"
