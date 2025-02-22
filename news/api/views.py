from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from news.api.serializers import ArticleReadSerializer
from news.api.serializers import ArticleSerializer
from news.api.serializers import ArticleSerializerFull
from news.api.serializers import FeedSerializer
from news.api.serializers import ProfileSerializer
from news.api.serializers import UserArticleListsSerializer
from news.api.serializers import UserArticleListsSerializerFull
from news.api.serializers import UserFeedSerializer
from news.models import ArticlesCombined
from news.models import FeedsCombined
from news.models import UserArticleLists
from news.models import UserFeeds


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


class UserFeedsView(viewsets.ModelViewSet):
    queryset = UserFeeds.objects.all()
    serializer_class = UserFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        feed_id = request.data["feed"]
        rating = request.data["rating"]
        uf = UserFeeds.objects.filter(user_id=user_id, feed_id=feed_id).first()
        if uf:
            uf.rating = rating
            uf.save()
            return Response(uf.id, status=status.HTTP_200_OK)
        uf = UserFeeds.objects.create(user_id=user_id, feed_id=feed_id, rating=rating)
        return Response(uf.id, status=status.HTTP_201_CREATED)


class UserArticleListsView(viewsets.ModelViewSet):
    queryset = UserArticleLists.objects.all()
    serializer_class = UserArticleListsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserArticleListsSerializerFull},
    )
    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = UserArticleListsSerializerFull(
            instance,
            context={"request": request},
        )
        return Response(serializer.data)

    @extend_schema(
        responses={201: UserArticleListsSerializerFull},
    )
    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        data["user"] = request.user.id
        serializer = UserArticleListsSerializerFull(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["PUT"])
    def add_article(self, request, pk=None):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article = request.data["article"]
        instance.articles.add(article)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["DELETE"])
    def remove_article(self, request, pk=None):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article = request.data["article"]
        instance.articles.remove(article)
        return Response(status=status.HTTP_200_OK)
