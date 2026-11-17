from rest_framework.routers import DefaultRouter
from .views import CustomerQueryViewSet

router = DefaultRouter()
router.register("queries", CustomerQueryViewSet, basename="query")
urlpatterns = router.urls
