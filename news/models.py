import datetime

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
        return self.id


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
        return self.id


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
        return self.id
