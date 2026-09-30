"""Serialização e validação dos dados expostos pela API Casa Aurora."""

from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Category, Product, Promotion, StoreSettings
from .validators import validate_uploaded_image, validate_whatsapp_number


def validate_model_field(validator, value):
    """Executa um validador Django e converte seu erro para o DRF."""
    try:
        validator(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages) from exc

    return value


class ValidatedImageField(serializers.ImageField):
    """Valida o conteúdo da imagem antes de permitir sua persistência."""

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return validate_model_field(validate_uploaded_image, value)


class PublicCategorySerializer(serializers.ModelSerializer):
    """Campos da categoria exibidos ao visitante."""

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "display_order",
        )
        read_only_fields = fields


class AdminCategorySerializer(serializers.ModelSerializer):
    """Leitura e edição de categorias pelo painel administrativo."""

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PublicProductListSerializer(serializers.ModelSerializer):
    """Representação resumida de um produto no catálogo público."""

    category = PublicCategorySerializer(read_only=True)
    main_image = serializers.ImageField(read_only=True, use_url=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "slug",
            "short_description",
            "price",
            "main_image",
            "alt_text",
            "is_featured",
        )
        read_only_fields = fields


class PublicProductDetailSerializer(PublicProductListSerializer):
    """Representação detalhada de um produto publicado."""

    class Meta(PublicProductListSerializer.Meta):
        fields = PublicProductListSerializer.Meta.fields + (
            "description",
        )
        read_only_fields = fields


class AdminProductSerializer(serializers.ModelSerializer):
    """Leitura, criação e atualização de produtos pelo painel."""

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
    )
    main_image = ValidatedImageField(
        required=False,
        allow_null=True,
        use_url=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "main_image",
            "alt_text",
            "is_featured",
            "status",
            "display_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "O preço não pode ser negativo."
            )

        return value


class PublicStoreSerializer(serializers.ModelSerializer):
    """Dados da loja disponíveis ao visitante."""

    banner_image = serializers.ImageField(read_only=True, use_url=True)

    class Meta:
        model = StoreSettings
        fields = (
            "name",
            "slogan",
            "description",
            "whatsapp_number",
            "demo_address",
            "opening_hours",
            "banner_image",
            "banner_text",
            "primary_button_text",
        )
        read_only_fields = fields


class AdminStoreSerializer(serializers.ModelSerializer):
    """Leitura e atualização da configuração única da loja."""

    banner_image = ValidatedImageField(
        required=False,
        allow_null=True,
        use_url=True,
    )

    class Meta:
        model = StoreSettings
        fields = (
            "id",
            "name",
            "slogan",
            "description",
            "whatsapp_number",
            "demo_address",
            "opening_hours",
            "banner_image",
            "banner_text",
            "primary_button_text",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_whatsapp_number(self, value):
        return validate_model_field(validate_whatsapp_number, value)


class PublicPromotionSerializer(serializers.ModelSerializer):
    """Promoção elegível exibida no site público."""

    image = serializers.ImageField(read_only=True, use_url=True)
    product = PublicProductListSerializer(read_only=True)

    class Meta:
        model = Promotion
        fields = (
            "id",
            "title",
            "description",
            "image",
            "product",
            "starts_at",
            "ends_at",
            "display_order",
        )
        read_only_fields = fields


class AdminPromotionSerializer(serializers.ModelSerializer):
    """Leitura, criação e atualização de promoções."""

    image = ValidatedImageField(
        required=False,
        allow_null=True,
        use_url=True,
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Promotion
        fields = (
            "id",
            "title",
            "description",
            "image",
            "product",
            "starts_at",
            "ends_at",
            "is_active",
            "display_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        starts_at = attrs.get(
            "starts_at",
            self.instance.starts_at if self.instance else None,
        )
        ends_at = attrs.get(
            "ends_at",
            self.instance.ends_at if self.instance else None,
        )

        if (
            starts_at is not None
            and ends_at is not None
            and starts_at > ends_at
        ):
            raise serializers.ValidationError(
                {
                    "ends_at": (
                        "A data e hora de fim não pode ser anterior "
                        "à data e hora de início."
                    )
                }
            )

        return attrs