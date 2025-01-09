# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Articles(models.Model):
    stamp = models.DateTimeField()
    author = models.TextField(blank=True, null=True)
    title_original = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    content_original = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    url = models.TextField(unique=True, blank=True, null=True)
    # comments = models.IntegerField(blank=True, null=True)
    feed = models.ForeignKey("Feeds", models.DO_NOTHING, blank=True, null=True)
    # topic_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "articles"


class ArticlesData(models.Model):
    id = models.OneToOneField("Articles", models.DO_NOTHING, primary_key=True, db_column="id")
    feed_id = models.IntegerField(blank=True, null=True)
    epoch = models.FloatField(blank=True, null=True)
    views = models.BigIntegerField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    to_reads = models.BigIntegerField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "articles_data"


class Feeds(models.Model):
    id = models.IntegerField(primary_key=True)
    homepage = models.TextField()
    url = models.TextField(unique=True)
    language = models.TextField()
    title = models.TextField()
    license = models.TextField(blank=True, null=True)
    icon = models.TextField()
    active = models.BooleanField(blank=True, null=True)
    last_polled = models.DateTimeField(blank=True, null=True)
    incomplete = models.BooleanField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # This field type is a guess.
    salt_url = models.BooleanField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    premium = models.BooleanField(blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)
    exclude = models.TextField(blank=True, null=True)
    main = models.TextField(blank=True, null=True)
    tor = models.BooleanField(blank=True, null=True)
    asy = models.BooleanField(blank=True, null=True)
    iconblob = models.BinaryField(blank=True, null=True)
    script = models.TextField(blank=True, null=True)
    frequency = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "feeds"


class Precomputed(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    view = models.TextField()
    articles = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "precomputed"
        unique_together = (("user", "view"),)


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


class UserFeeds(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    feed = models.ForeignKey(Feeds, models.DO_NOTHING)
    rating = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_feeds"
        unique_together = (("user", "feed"),)


class UserTransactions(models.Model):
    user = models.OneToOneField("Users", models.DO_NOTHING, primary_key=True)
    date = models.DateField()
    amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_transactions"
        unique_together = (("user", "date"),)


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    newsletter = models.BooleanField(blank=True, null=True)
    list_email = models.TextField(blank=True, null=True)
    list_frequency = models.TextField(blank=True, null=True)
    list_news = models.IntegerField(blank=True, null=True)
    list_format = models.TextField(blank=True, null=True)
    whitelist = models.TextField(blank=True, null=True)
    whitelist_authors = models.TextField(blank=True, null=True)
    blacklist = models.TextField(blank=True, null=True)
    blacklist_authors = models.TextField(blank=True, null=True)
    sociality_weight = models.IntegerField(blank=True, null=True)
    gravity = models.FloatField(blank=True, null=True)
    comment_factor = models.FloatField(blank=True, null=True)
    age_divider = models.FloatField(blank=True, null=True)
    feed_weight = models.IntegerField(blank=True, null=True)
    list_weight = models.IntegerField(blank=True, null=True)
    last_access = models.DateTimeField(blank=True, null=True)
    bow = models.JSONField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # This field type is a guess.
    languages = models.TextField(blank=True, null=True)  # This field type is a guess.
    list_hour = models.IntegerField(blank=True, null=True)
    filter2 = models.TextField(blank=True, null=True)
    list_fulltext = models.BooleanField(blank=True, null=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    inactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"
