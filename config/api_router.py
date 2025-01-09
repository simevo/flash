from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from flash.users.api.views import UserViewSet
from news.views import ArticlesSimpleView, ArticlesView, FeedsView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticlesView, basename="articles")
router.register("public/feeds", FeedsView, basename="public-feeds")
router.register("public/articles", ArticlesSimpleView, basename="public-articles")


app_name = "api"
urlpatterns = router.urls
