from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from news.models import Articles
from news.models import ArticlesCombined
from news.models import Feeds
from news.models import FeedsCombined
from news.models import Profile
from news.models import FeedPolling
from news.models import UserArticleLists
from news.models import UserFeeds


class FeedSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = FeedsCombined
        fields = ["id", "title", "image", "license"]


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedsCombined
        exclude = [
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
        exclude = [
            "paraphrase_multilingual_mpnet_base_v2",
            "use_cmlm_multilingual",
            "tsv",
        ]


class ArticleReadSerializer(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    class Meta:
        model = ArticlesCombined
        exclude = [
            "content",
            "content_original",
            "paraphrase_multilingual_mpnet_base_v2",
            "use_cmlm_multilingual",
            "tsv",
        ]


class ArticleSerializerFull(serializers.ModelSerializer):
    stamp = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_stamp(self, obj):
        return int(obj.stamp.timestamp())

    class Meta:
        model = ArticlesCombined
        exclude = [
            "paraphrase_multilingual_mpnet_base_v2",
            "use_cmlm_multilingual",
            "tsv",
        ]


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


class FeedPollingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedPolling
        fields = "__all__"
