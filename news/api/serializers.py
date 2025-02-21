from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from news.models import Articles
from news.models import ArticlesCombined
from news.models import Feeds
from news.models import FeedsCombined
from news.models import Profile
from news.models import UserFeeds


class FeedSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Feeds
        fields = ["id", "title", "icon", "premium", "license"]


class FeedSerializer(serializers.ModelSerializer):
    my_rating = serializers.SerializerMethodField()

    class Meta:
        model = FeedsCombined
        exclude = ["iconblob"]

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_my_rating(self, obj):
        user = self.context["request"].user
        uf = UserFeeds.objects.filter(feed_id=obj.id, user_id=user.id).first()
        if uf:
            return uf.rating
        else:
            return None


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
