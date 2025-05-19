from django.db import migrations

from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_feedicons'),
    ]

    operations = [
        VectorExtension()
    ]
