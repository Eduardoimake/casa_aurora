"""Modelos de catálogo e conteúdo administrável da Casa Aurora."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .validators import (
    product_image_upload_to,
    promotion_image_upload_to,
    store_banner_upload_to,
    validate_uploaded_image,
    validate_whatsapp_number,
)


class Category(models.Model):
    """Agrupamento de produtos exibido no catálogo."""

    name = models.CharField(
        "nome",
        max_length=120,
    )
    slug = models.SlugField(
        "slug",
        max_length=140,
        unique=True,
    )
    short_description = models.CharField(
        "descrição curta",
        max_length=240,
        blank=True,
    )
    display_order = models.PositiveIntegerField(
        "ordem de exibição",
        default=0,
    )
    is_active = models.BooleanField(
        "ativa",
        default=True,
    )
    created_at = models.DateTimeField(
        "data de criação",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "data de atualização",
        auto_now=True,
    )

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ("display_order", "name", "id")

    def __str__(self):
        return self.name


class Product(models.Model):
    """Produto administrável, com publicação independente da categoria."""

    class Status(models.TextChoices):
        PUBLISHED = "published", "Publicado"
        HIDDEN = "hidden", "Oculto"

    category = models.ForeignKey(
        Category,
        verbose_name="categoria",
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        "nome",
        max_length=180,
    )
    slug = models.SlugField(
        "slug",
        max_length=200,
        unique=True,
    )
    short_description = models.CharField(
        "descrição curta",
        max_length=280,
    )
    description = models.TextField(
        "descrição completa",
    )
    price = models.DecimalField(
        "preço",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    main_image = models.ImageField(
        "imagem principal",
        upload_to=product_image_upload_to,
        validators=[validate_uploaded_image],
        blank=True,
    )
    alt_text = models.CharField(
        "texto alternativo da imagem",
        max_length=180,
        blank=True,
    )
    is_featured = models.BooleanField(
        "destaque na página inicial",
        default=False,
    )
    status = models.CharField(
        "status",
        max_length=10,
        choices=Status.choices,
        default=Status.HIDDEN,
    )
    display_order = models.PositiveIntegerField(
        "ordem de exibição",
        default=0,
    )
    created_at = models.DateTimeField(
        "data de criação",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "data de atualização",
        auto_now=True,
    )

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ("display_order", "name", "id")
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="catalog_product_price_nonnegative",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_public(self):
        """Indica elegibilidade; a API também filtrará isso no banco."""
        return (
            self.status == self.Status.PUBLISHED
            and self.category.is_active
        )


class StoreSettings(models.Model):
    """Configuração única da loja demonstrativa."""

    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )
    name = models.CharField(
        "nome da loja",
        max_length=180,
    )
    slogan = models.CharField(
        "slogan",
        max_length=240,
        blank=True,
    )
    description = models.TextField(
        "apresentação",
        blank=True,
    )
    whatsapp_number = models.CharField(
        "WhatsApp",
        max_length=15,
        validators=[validate_whatsapp_number],
        help_text=(
            "Número internacional com 10 a 15 dígitos, "
            "sem +, espaços ou pontuação."
        ),
    )
    demo_address = models.CharField(
        "endereço demonstrativo",
        max_length=240,
        blank=True,
    )
    opening_hours = models.CharField(
        "horário de atendimento",
        max_length=240,
        blank=True,
    )
    banner_image = models.ImageField(
        "imagem do banner",
        upload_to=store_banner_upload_to,
        validators=[validate_uploaded_image],
        blank=True,
    )
    banner_text = models.CharField(
        "texto do banner",
        max_length=280,
        blank=True,
    )
    primary_button_text = models.CharField(
        "texto do botão principal",
        max_length=80,
        blank=True,
    )
    created_at = models.DateTimeField(
        "data de criação",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "data de atualização",
        auto_now=True,
    )

    class Meta:
        verbose_name = "configuração da loja"
        verbose_name_plural = "configurações da loja"
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name="catalog_store_settings_singleton_id",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        if self.pk != 1:
            raise ValidationError(
                {"id": "A configuração da loja deve usar o identificador 1."}
            )


class Promotion(models.Model):
    """Destaque promocional opcionalmente associado a um produto."""

    title = models.CharField(
        "título",
        max_length=180,
    )
    description = models.TextField(
        "descrição",
    )
    image = models.ImageField(
        "imagem",
        upload_to=promotion_image_upload_to,
        validators=[validate_uploaded_image],
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="produto vinculado",
        related_name="promotions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField(
        "data e hora de início",
        null=True,
        blank=True,
    )
    ends_at = models.DateTimeField(
        "data e hora de fim",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        "ativa",
        default=True,
    )
    display_order = models.PositiveIntegerField(
        "ordem de exibição",
        default=0,
    )
    created_at = models.DateTimeField(
        "data de criação",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "data de atualização",
        auto_now=True,
    )

    class Meta:
        verbose_name = "promoção"
        verbose_name_plural = "promoções"
        ordering = ("display_order", "id")
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(starts_at__isnull=True)
                    | Q(ends_at__isnull=True)
                    | Q(starts_at__lte=models.F("ends_at"))
                ),
                name="catalog_promotion_valid_period",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if (
            self.starts_at is not None
            and self.ends_at is not None
            and self.starts_at > self.ends_at
        ):
            raise ValidationError(
                {
                    "ends_at": (
                        "A data e hora de fim não pode ser anterior "
                        "à data e hora de início."
                    )
                }
            )

    def is_currently_eligible(self, at=None):
        """Verifica a elegibilidade, inclusive do produto vinculado."""
        at = at or timezone.now()

        if not self.is_active:
            return False

        if self.starts_at is not None and self.starts_at > at:
            return False

        if self.ends_at is not None and self.ends_at < at:
            return False

        if self.product_id is not None and not self.product.is_public:
            return False

        return True