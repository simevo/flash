from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from flash.users.api.views import UserViewSet
from news.api.views import ArticlesView
from news.api.views import FeedsView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticlesView, basename="articles")
router.register("feeds", FeedsView, basename="public-feeds")


app_name = "api"
urlpatterns = router.urls
