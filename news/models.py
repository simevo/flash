import datetime

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

    class Meta:
        managed = False
        db_table = "feeds"

    def __str__(self):
        return self.id


class Precomputed(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    view = models.TextField()
    articles = models.TextField(blank=True, null=True)  # noqa: DJ001  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "precomputed"
        unique_together = (("user", "view"),)

    def __str__(self):
        return self.user


class UserArticles(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    article = models.ForeignKey(Articles, models.DO_NOTHING)
    read = models.BooleanField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    to_read = models.BooleanField(blank=True, null=True)
    dismissed = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_articles"
        unique_together = (("user", "article"),)

    def __str__(self):
        return self.user


class UserFeeds(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    feed = models.ForeignKey(Feeds, models.DO_NOTHING)
    rating = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_feeds"
        unique_together = (("user", "feed"),)

    def __str__(self):
        return self.user


class UserTransactions(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    date = models.DateField()
    amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_transactions"
        unique_together = (("user", "date"),)

    def __str__(self):
        return self.user


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    newsletter = models.BooleanField(blank=True, null=True)
    list_email = models.TextField(blank=True, null=True)  # noqa: DJ001
    list_frequency = models.TextField(blank=True, null=True)  # noqa: DJ001
    list_news = models.IntegerField(blank=True, null=True)
    list_format = models.TextField(blank=True, null=True)  # noqa: DJ001
    whitelist = models.TextField(blank=True, null=True)  # noqa: DJ001
    whitelist_authors = models.TextField(blank=True, null=True)  # noqa: DJ001
    blacklist = models.TextField(blank=True, null=True)  # noqa: DJ001
    blacklist_authors = models.TextField(blank=True, null=True)  # noqa: DJ001
    sociality_weight = models.IntegerField(blank=True, null=True)
    gravity = models.FloatField(blank=True, null=True)
    comment_factor = models.FloatField(blank=True, null=True)
    age_divider = models.FloatField(blank=True, null=True)
    feed_weight = models.IntegerField(blank=True, null=True)
    list_weight = models.IntegerField(blank=True, null=True)
    last_access = models.DateTimeField(blank=True, null=True)
    bow = models.JSONField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # noqa: DJ001  # This field type is a guess.
    languages = models.TextField(blank=True, null=True)  # noqa: DJ001  # This field type is a guess.
    list_hour = models.IntegerField(blank=True, null=True)
    filter2 = models.TextField(blank=True, null=True)  # noqa: DJ001
    list_fulltext = models.BooleanField(blank=True, null=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    username = models.TextField(blank=True, null=True)  # noqa: DJ001
    email = models.TextField(blank=True, null=True)  # noqa: DJ001
    inactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.id
