from django.conf import settings
from rest_framework.routers import BaseRouter, DefaultRouter, SimpleRouter

from flash.users.api.views import UserViewSet
from news.views import ArticlesSimpleView, ArticlesView, FeedsView

router: BaseRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticlesView, basename="articles")
router.register("public/feeds", FeedsView, basename="public-feeds")
router.register("public/articles", ArticlesSimpleView, basename="public-articles")


app_name = "api"
urlpatterns = router.urls
