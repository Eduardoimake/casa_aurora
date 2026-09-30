"""Migração inicial dos modelos de catálogo e configuração da loja."""

from decimal import Decimal

import catalog.validators
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=120,
                        verbose_name="nome",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=140,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "short_description",
                    models.CharField(
                        blank=True,
                        max_length=240,
                        verbose_name="descrição curta",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(
                        default=0,
                        verbose_name="ordem de exibição",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        verbose_name="ativa",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="data de criação",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="data de atualização",
                    ),
                ),
            ],
            options={
                "verbose_name": "categoria",
                "verbose_name_plural": "categorias",
                "ordering": ("display_order", "name", "id"),
            },
        ),
        migrations.CreateModel(
            name="StoreSettings",
            fields=[
                (
                    "id",
                    models.PositiveSmallIntegerField(
                        default=1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=180,
                        verbose_name="nome da loja",
                    ),
                ),
                (
                    "slogan",
                    models.CharField(
                        blank=True,
                        max_length=240,
                        verbose_name="slogan",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        verbose_name="apresentação",
                    ),
                ),
                (
                    "whatsapp_number",
                    models.CharField(
                        help_text=(
                            "Número internacional com 10 a 15 dígitos, "
                            "sem +, espaços ou pontuação."
                        ),
                        max_length=15,
                        validators=[
                            catalog.validators.validate_whatsapp_number
                        ],
                        verbose_name="WhatsApp",
                    ),
                ),
                (
                    "demo_address",
                    models.CharField(
                        blank=True,
                        max_length=240,
                        verbose_name="endereço demonstrativo",
                    ),
                ),
                (
                    "opening_hours",
                    models.CharField(
                        blank=True,
                        max_length=240,
                        verbose_name="horário de atendimento",
                    ),
                ),
                (
                    "banner_image",
                    models.ImageField(
                        blank=True,
                        upload_to=catalog.validators.store_banner_upload_to,
                        validators=[
                            catalog.validators.validate_uploaded_image
                        ],
                        verbose_name="imagem do banner",
                    ),
                ),
                (
                    "banner_text",
                    models.CharField(
                        blank=True,
                        max_length=280,
                        verbose_name="texto do banner",
                    ),
                ),
                (
                    "primary_button_text",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        verbose_name="texto do botão principal",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="data de criação",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="data de atualização",
                    ),
                ),
            ],
            options={
                "verbose_name": "configuração da loja",
                "verbose_name_plural": "configurações da loja",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("id", 1)),
                        name="catalog_store_settings_singleton_id",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=180,
                        verbose_name="nome",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=200,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "short_description",
                    models.CharField(
                        max_length=280,
                        verbose_name="descrição curta",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        verbose_name="descrição completa",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.00")
                            )
                        ],
                        verbose_name="preço",
                    ),
                ),
                (
                    "main_image",
                    models.ImageField(
                        blank=True,
                        upload_to=catalog.validators.product_image_upload_to,
                        validators=[
                            catalog.validators.validate_uploaded_image
                        ],
                        verbose_name="imagem principal",
                    ),
                ),
                (
                    "alt_text",
                    models.CharField(
                        blank=True,
                        max_length=180,
                        verbose_name="texto alternativo da imagem",
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(
                        default=False,
                        verbose_name="destaque na página inicial",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("published", "Publicado"),
                            ("hidden", "Oculto"),
                        ],
                        default="hidden",
                        max_length=10,
                        verbose_name="status",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(
                        default=0,
                        verbose_name="ordem de exibição",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="data de criação",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="data de atualização",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="catalog.category",
                        verbose_name="categoria",
                    ),
                ),
            ],
            options={
                "verbose_name": "produto",
                "verbose_name_plural": "produtos",
                "ordering": ("display_order", "name", "id"),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("price__gte", 0)),
                        name="catalog_product_price_nonnegative",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Promotion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=180,
                        verbose_name="título",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        verbose_name="descrição",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        upload_to=catalog.validators.promotion_image_upload_to,
                        validators=[
                            catalog.validators.validate_uploaded_image
                        ],
                        verbose_name="imagem",
                    ),
                ),
                (
                    "starts_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="data e hora de início",
                    ),
                ),
                (
                    "ends_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="data e hora de fim",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        verbose_name="ativa",
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(
                        default=0,
                        verbose_name="ordem de exibição",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="data de criação",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="data de atualização",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="promotions",
                        to="catalog.product",
                        verbose_name="produto vinculado",
                    ),
                ),
            ],
            options={
                "verbose_name": "promoção",
                "verbose_name_plural": "promoções",
                "ordering": ("display_order", "id"),
                "constraints": [
                    models.CheckConstraint(
                        condition=(
                            models.Q(("starts_at__isnull", True))
                            | models.Q(("ends_at__isnull", True))
                            | models.Q(
                                ("starts_at__lte", models.F("ends_at"))
                            )
                        ),
                        name="catalog_promotion_valid_period",
                    ),
                ],
            },
        ),
    ]