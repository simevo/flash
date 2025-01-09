from django.shortcuts import get_object_or_404
from rest_framework import pagination, permissions, viewsets
from rest_framework.response import Response

from news.models import Articles, Feeds
from news.serializers import (
    ArticleSerializer,
    ArticleSerializerFull,
    ArticleSerializerSimple,
    FeedSerializer,
)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 31


class ArticlesSimpleView(viewsets.ModelViewSet):
    queryset = Articles.objects.all().order_by("-id")
    serializer_class = ArticleSerializerSimple
    permission_classes = [ReadOnly]
    pagination_class = StandardResultsSetPagination


class ArticlesView(viewsets.ModelViewSet):
    queryset = Articles.objects.all().order_by("-id")
    serializer_class = ArticleSerializer
    permission_classes = [ReadOnly, permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, pk=None):
        queryset = Articles.objects
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializerFull(article, context={"request": request})
        return Response(serializer.data)


class FeedsView(viewsets.ModelViewSet):
    queryset = Feeds.objects.all().order_by("-id")
    serializer_class = FeedSerializer
    permission_classes = [ReadOnly]
