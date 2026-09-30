"""Rotas da API de catálogo e gestão da Casa Aurora."""

from django.urls import path

from .views import (
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    AdminDashboardView,
    AdminProductDetailView,
    AdminProductListCreateView,
    AdminPromotionDetailView,
    AdminPromotionListCreateView,
    AdminStoreView,
    CsrfTokenView,
    LoginView,
    LogoutView,
    MeView,
    PublicCategoryListView,
    PublicProductDetailView,
    PublicProductListView,
    PublicPromotionListView,
    PublicStoreView,
)


urlpatterns = [
    path("public/store/", PublicStoreView.as_view(), name="public-store"),
    path(
        "public/categories/",
        PublicCategoryListView.as_view(),
        name="public-categories",
    ),
    path(
        "public/products/",
        PublicProductListView.as_view(),
        name="public-products",
    ),
    path(
        "public/products/<slug:slug>/",
        PublicProductDetailView.as_view(),
        name="public-product-detail",
    ),
    path(
        "public/promotions/",
        PublicPromotionListView.as_view(),
        name="public-promotions",
    ),
    path("auth/csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path(
        "admin/dashboard/",
        AdminDashboardView.as_view(),
        name="admin-dashboard",
    ),
    path(
        "admin/categories/",
        AdminCategoryListCreateView.as_view(),
        name="admin-categories",
    ),
    path(
        "admin/categories/<int:pk>/",
        AdminCategoryDetailView.as_view(),
        name="admin-category-detail",
    ),
    path(
        "admin/products/",
        AdminProductListCreateView.as_view(),
        name="admin-products",
    ),
    path(
        "admin/products/<int:pk>/",
        AdminProductDetailView.as_view(),
        name="admin-product-detail",
    ),
    path(
        "admin/store/",
        AdminStoreView.as_view(),
        name="admin-store",
    ),
    path(
        "admin/promotions/",
        AdminPromotionListCreateView.as_view(),
        name="admin-promotions",
    ),
    path(
        "admin/promotions/<int:pk>/",
        AdminPromotionDetailView.as_view(),
        name="admin-promotion-detail",
    ),
]