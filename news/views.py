from rest_framework import pagination, permissions, viewsets
from news.models import Articles
from news.serializers import ArticleSerializer


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 31


class ArticlesView(viewsets.ModelViewSet):
    """
    API endpoint that allows W16 bulletins to be viewed or edited
    """

    queryset = Articles.objects.all().order_by("-id")
    serializer_class = ArticleSerializer
    permission_classes = [ReadOnly]
    pagination_class = StandardResultsSetPagination
