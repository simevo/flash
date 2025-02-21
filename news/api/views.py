from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response

from news.api.serializers import ArticleReadSerializer
from news.api.serializers import ArticleSerializer
from news.api.serializers import ArticleSerializerFull
from news.api.serializers import FeedSerializer
from news.api.serializers import ProfileSerializer
from news.models import ArticlesCombined
from news.models import FeedsCombined


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 200


class ArticlesFilter(filters.FilterSet):
    search_author = filters.CharFilter(
        method="filter_search_author",
        field_name="author",
    )

    def filter_search_author(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("author")).filter(search=value)

    class Meta:
        model = ArticlesCombined
        fields = ["feed_id"]


class ArticlesView(viewsets.ModelViewSet, mixins.CreateModelMixin):
    queryset = ArticlesCombined.objects.all().order_by("-id")
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ArticlesFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return ArticleReadSerializer
        return ArticleSerializer

    @extend_schema(
        responses={200: ArticleSerializerFull},
    )
    def retrieve(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializerFull(article, context={"request": request})
        user = request.user
        user_articles = user.userarticles_set.filter(article_id=article.id)
        if user_articles.exists():
            user_article = user_articles.first()
            user_article.read = True
            user_article.save()
        else:
            user.userarticles_set.create(article_id=article.id, read=True)
        return Response(serializer.data)


class FeedsView(viewsets.ModelViewSet):
    queryset = FeedsCombined.objects.all().order_by("id")
    serializer_class = FeedSerializer
    permission_classes = [ReadOnly, permissions.IsAuthenticated]


class ProfileView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
