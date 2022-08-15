from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Address API",
        default_version="v1",
    ),
    public=True,
    permission_classes=([AllowAny]),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("addresses/", include("address_book.urls")),
    path("authentication/", include("authentication.urls")),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-redoc"),
]
