from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from news.models import Articles
from news.models import ArticlesCombined
from news.models import Feeds
from news.models import FeedsCombined
from news.models import Profile
from news.models import UserArticleLists
from news.models import UserFeeds


class FeedSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Feeds
        fields = ["id", "title", "icon", "license"]


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedsCombined
        exclude = [
            "iconblob",
            "rating",
            "premium",
            "tor",
            "asy",
        ]


class FeedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feeds
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = "__all__"


class ArticleReadSerializer(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    class Meta:
        model = ArticlesCombined
        exclude = ["content", "content_original"]


class ArticleSerializerFull(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    class Meta:
        model = ArticlesCombined
        fields = "__all__"
        depth = 1


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user"]


class UserFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeeds
        fields = ["feed_id", "rating"]


class UserArticleListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserArticleLists
        exclude = ["user", "articles"]


class UserArticleListsSerializerFull(serializers.ModelSerializer):
    class Meta:
        model = UserArticleLists
        fields = "__all__"
