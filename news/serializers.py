from rest_framework import serializers

from news.models import Articles


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        exclude = ["content", "content_original"]
