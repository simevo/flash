import re

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from news.models import Articles
from news.models import Feeds


class FeedSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Feeds
        fields = ["id", "title", "icon", "premium", "license"]


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feeds
        exclude = ["iconblob"]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = "__all__"


class ArticleReadSerializer(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_length(self, obj):
        if obj.content:
            return obj.content.__len__()
        return obj.content_original.__len__()

    def get_excerpt(self, obj):
        if obj.content:
            stripped_content = re.sub(r"[\s]+", " ", re.sub(r"<.+?>", "", obj.content))
        else:
            stripped_content = re.sub(
                r"[\s]+",
                " ",
                re.sub(r"<.+?>", "", obj.content_original),
            )
        return stripped_content[:400]

    class Meta:
        model = Articles
        exclude = ["content", "content_original"]


class ArticleSerializerFull(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    class Meta:
        model = Articles
        fields = "__all__"
        depth = 1
