from django.conf import settings
from rest_framework.routers import BaseRouter, DefaultRouter, SimpleRouter

from flash.users.api.views import UserViewSet

from news.views import ArticlesView

router: BaseRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register(r"articles", ArticlesView)


app_name = "api"
urlpatterns = router.urls
