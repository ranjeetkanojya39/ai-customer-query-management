from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import RedirectView
urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("queries.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
