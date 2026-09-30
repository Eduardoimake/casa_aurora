"""Django Admin auxiliar para os dados da Casa Aurora.

O painel administrativo personalizado consome a API em /api/v1/admin/.
Este módulo apenas facilita inspeção e manutenção local dos modelos.
"""

from django.contrib import admin

from .models import Category, Product, Promotion, StoreSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Consulta e manutenção auxiliar das categorias."""

    list_display = (
        "name",
        "slug",
        "is_active",
        "display_order",
        "updated_at",
    )
    list_display_links = ("name",)
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "short_description")
    ordering = ("display_order", "name", "id")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "name",
                    "slug",
                    "short_description",
                )
            },
        ),
        (
            "Exibição",
            {
                "fields": (
                    "is_active",
                    "display_order",
                )
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Consulta e manutenção auxiliar dos produtos."""

    list_display = (
        "name",
        "category",
        "price",
        "status",
        "is_featured",
        "display_order",
        "updated_at",
    )
    list_display_links = ("name",)
    list_filter = (
        "status",
        "is_featured",
        "category",
    )
    search_fields = (
        "name",
        "slug",
        "short_description",
        "category__name",
    )
    ordering = ("display_order", "name", "id")
    list_select_related = ("category",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Produto",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_description",
                    "description",
                    "price",
                )
            },
        ),
        (
            "Imagem",
            {
                "fields": (
                    "main_image",
                    "alt_text",
                )
            },
        ),
        (
            "Publicação",
            {
                "fields": (
                    "status",
                    "is_featured",
                    "display_order",
                )
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    """Mantém, no máximo, a configuração única da loja."""

    list_display = (
        "name",
        "whatsapp_number",
        "updated_at",
    )
    list_display_links = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Apresentação",
            {
                "fields": (
                    "name",
                    "slogan",
                    "description",
                )
            },
        ),
        (
            "Contato demonstrativo",
            {
                "fields": (
                    "whatsapp_number",
                    "demo_address",
                    "opening_hours",
                )
            },
        ),
        (
            "Banner",
            {
                "fields": (
                    "banner_image",
                    "banner_text",
                    "primary_button_text",
                )
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        """Permite criar a loja somente enquanto não existir um registro."""
        return (
            super().has_add_permission(request)
            and not StoreSettings.objects.exists()
        )

    def has_delete_permission(self, request, obj=None):
        """Evita remover a configuração única pelo Django Admin."""
        return False


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Consulta e manutenção auxiliar dos destaques promocionais."""

    list_display = (
        "title",
        "product",
        "is_active",
        "starts_at",
        "ends_at",
        "display_order",
    )
    list_display_links = ("title",)
    list_filter = ("is_active",)
    search_fields = (
        "title",
        "description",
        "product__name",
    )
    ordering = ("display_order", "id")
    list_select_related = ("product",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Promoção",
            {
                "fields": (
                    "title",
                    "description",
                    "image",
                    "product",
                )
            },
        ),
        (
            "Exibição",
            {
                "fields": (
                    "is_active",
                    "starts_at",
                    "ends_at",
                    "display_order",
                )
            },
        ),
        (
            "Registro",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )