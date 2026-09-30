"""Rotas principais do projeto Casa Aurora."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/", include("catalog.urls")),
]

# Somente para desenvolvimento local.
# Em produção, sirva mídia enviada por usuários separadamente.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )