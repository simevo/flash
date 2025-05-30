# Generated by Django 5.0.10 on 2025-04-20 08:31

import django.db.models.deletion
from django.db import migrations, models


def modify_articles_data_view(apps, schema_editor):

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP VIEW IF EXISTS articles_data_view")
        cursor.execute("""
                       CREATE VIEW articles_data_view AS
                            SELECT
                                articles.id,
                                COALESCE(COUNT(CASE WHEN news_userarticles.read THEN 1 END), 0) + COALESCE(news_guestarticles.views, 0) AS views,
                                COALESCE(AVG(news_userarticles.rating), 0) AS rating,
                                COALESCE(AVG(articlelists_count_view.count), 0) AS to_reads,
                                COALESCE(LENGTH(articles.content), LENGTH(articles.content_original)) as length,
                                SUBSTRING((CASE WHEN LENGTH(TRIM(articles.content))>0 THEN articles.content ELSE articles.content_original END) FOR 500) AS excerpt
                            FROM
                                articles
                                LEFT OUTER JOIN news_userarticles ON articles.id = news_userarticles.article_id
                                LEFT OUTER JOIN articlelists_count_view ON articles.id = articlelists_count_view.article_id
                                LEFT OUTER JOIN news_guestarticles ON articles.id = news_guestarticles.article_id
                            GROUP BY articles.id, news_guestarticles.views""")
        cursor.execute("CREATE TRIGGER update_articles_data3 AFTER INSERT OR UPDATE ON news_guestarticles FOR EACH ROW EXECUTE FUNCTION uad2()")


def restore_articles_data_view(apps, schema_editor):

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP VIEW IF EXISTS articles_data_view")
        cursor.execute("""
                       CREATE VIEW articles_data_view AS
                            SELECT
                                articles.id,
                                COALESCE(COUNT(CASE WHEN news_userarticles.read THEN 1 END), 0) AS views,
                                COALESCE(AVG(news_userarticles.rating), 0) AS rating,
                                COALESCE(AVG(articlelists_count_view.count), 0) AS to_reads,
                                COALESCE(LENGTH(articles.content), LENGTH(articles.content_original)) as length,
                                SUBSTRING((CASE WHEN LENGTH(TRIM(articles.content))>0 THEN articles.content ELSE articles.content_original END) FOR 500) AS excerpt
                            FROM
                                articles
                                LEFT OUTER JOIN news_userarticles ON articles.id = news_userarticles.article_id
                                LEFT OUTER JOIN articlelists_count_view ON articles.id = articlelists_count_view.article_id
                            GROUP BY articles.id""")
        cursor.execute("DROP TRIGGER IF EXISTS update_articles_data3 ON news_guestarticles")


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_feedscombined_feedsdata_alter_feeds_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestArticles',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('views', models.BigIntegerField()),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='news.articles')),
            ],
        ),
        migrations.RunPython(modify_articles_data_view, reverse_code=restore_articles_data_view),
    ]
