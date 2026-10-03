"""Rotas principais do projeto Casa Aurora."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .frontend import FrontendAppView


frontend_view = FrontendAppView.as_view()

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/", include("catalog.urls")),

    path("", frontend_view, name="frontend-home"),
    path("catalogo", frontend_view, name="frontend-catalog"),
    path("produto/<slug:slug>", frontend_view, name="frontend-product"),
    path("painel", frontend_view, name="frontend-admin"),
    path("painel/login", frontend_view, name="frontend-admin-login"),
    path("painel/categorias", frontend_view, name="frontend-admin-categories"),
    path("painel/produtos", frontend_view, name="frontend-admin-products"),
    path("painel/loja", frontend_view, name="frontend-admin-store"),
    path("painel/promocoes", frontend_view, name="frontend-admin-promotions"),
    path("sobre", frontend_view, name="frontend-about"),
]

if settings.DEBUG and not settings.R2_ENABLED:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )