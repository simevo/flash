import datetime

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


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

    class Meta:
        managed = False
        db_table = "articles"

    def __str__(self):
        return f"{self.id}"


class ArticlesData(models.Model):
    id = models.OneToOneField(
        "Articles",
        models.DO_NOTHING,
        primary_key=True,
        db_column="id",
    )
    feed_id = models.IntegerField(blank=True, null=True)
    epoch = models.FloatField(blank=True, null=True)
    views = models.BigIntegerField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    to_reads = models.BigIntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "articles_data"

    def __str__(self):
        return f"{self.id}"


class Feeds(models.Model):
    id = models.IntegerField(primary_key=True)
    homepage = models.TextField()
    url = models.TextField(unique=True)
    language = models.TextField()
    title = models.TextField()
    license = models.TextField(blank=True, null=True)  # noqa: DJ001
    icon = models.TextField()
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
    iconblob = models.BinaryField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)  # noqa: DJ001
    frequency = models.TextField(blank=True, null=True)  # noqa: DJ001
    tags = ArrayField(models.TextField(), blank=True, null=True)

    class Meta:
        managed = False
        db_table = "feeds"

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
    whitelist = ArrayField(models.TextField(), default=list)
    whitelist_authors = ArrayField(models.TextField(), default=list)
    blacklist = ArrayField(models.TextField(), default=list)
    blacklist_authors = ArrayField(models.TextField(), default=list)
    sociality_weight = models.IntegerField(default=0)
    gravity = models.FloatField(default=2.0)
    age_divider = models.FloatField(default=100.0)
    feed_weight = models.IntegerField(default=0)
    list_weight = models.IntegerField(default=0)
    last_access = models.DateTimeField(blank=True, null=True)
    bow = models.JSONField(default=dict)
    tags = ArrayField(models.TextField(), default=list)
    languages = ArrayField(models.TextField(), default=list)
    list_hour = models.IntegerField(default=7)
    list_fulltext = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"


class UserArticleLists(models.Model):
    id = models.AutoField(primary_key=True)
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
