from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from flash.users.api.views import UserViewSet
from news.api.views import ArticlesView
from news.api.views import FeedsView
from news.api.views import ProfileView
from news.api.views import UserArticleListsView
from news.api.views import UserFeedsView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticlesView, basename="articles")
router.register("feeds", FeedsView, basename="public-feeds")
router.register("profile", ProfileView, basename="profile")
router.register("user-feeds", UserFeedsView, basename="user-feeds")
router.register(
    "user-article-lists",
    UserArticleListsView,
    basename="user-article-lists",
)

app_name = "api"
urlpatterns = router.urls
