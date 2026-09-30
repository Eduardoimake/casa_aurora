"""Regressões de validação em escritas administrativas."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product, Promotion, StoreSettings


class AdminValidationRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="gestor_validacao_teste",
            password="SenhaDeTesteForte-456!",
            is_staff=True,
        )
        cls.category = Category.objects.create(
            name="Decoração",
            slug="decoracao-validacao",
            is_active=True,
        )
        cls.product = Product.objects.create(
            category=cls.category,
            name="Vaso demonstrativo",
            slug="vaso-validacao",
            short_description="Peça fictícia.",
            description="Produto usado nos testes de validação.",
            price=Decimal("49.90"),
            status=Product.Status.PUBLISHED,
        )
        cls.store = StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.staff)

    def test_patch_de_preco_negativo_nao_altera_produto(self):
        original_price = self.product.price

        response = self.client.patch(
            f"/api/v1/admin/products/{self.product.pk}/",
            {"price": "-0.01"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.data)

        self.product.refresh_from_db()
        self.assertEqual(self.product.price, original_price)

    def test_patch_de_whatsapp_invalido_nao_altera_loja(self):
        original_number = self.store.whatsapp_number

        response = self.client.patch(
            "/api/v1/admin/store/",
            {"whatsapp_number": "numero-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("whatsapp_number", response.data)

        self.store.refresh_from_db()
        self.assertEqual(
            self.store.whatsapp_number,
            original_number,
        )

    def test_patch_de_fim_anterior_ao_inicio_nao_altera_promocao(self):
        now = timezone.now()
        promotion = Promotion.objects.create(
            title="Promoção com período",
            description="Regressão de PATCH parcial.",
            starts_at=now,
            ends_at=now + timedelta(days=3),
            is_active=True,
        )
        original_end = promotion.ends_at

        response = self.client.patch(
            f"/api/v1/admin/promotions/{promotion.pk}/",
            {
                "ends_at": (
                    now - timedelta(days=1)
                ).isoformat()
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("ends_at", response.data)

        promotion.refresh_from_db()
        self.assertEqual(promotion.ends_at, original_end)

    def test_patch_de_inicio_posterior_ao_fim_nao_altera_promocao(self):
        now = timezone.now()
        promotion = Promotion.objects.create(
            title="Outra promoção com período",
            description="Regressão de PATCH parcial.",
            starts_at=now,
            ends_at=now + timedelta(days=3),
            is_active=True,
        )
        original_start = promotion.starts_at

        response = self.client.patch(
            f"/api/v1/admin/promotions/{promotion.pk}/",
            {
                "starts_at": (
                    now + timedelta(days=4)
                ).isoformat()
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("ends_at", response.data)

        promotion.refresh_from_db()
        self.assertEqual(
            promotion.starts_at,
            original_start,
        )

    def test_patch_valido_de_promocao_preserva_campo_omitido(self):
        now = timezone.now()
        promotion = Promotion.objects.create(
            title="Promoção válida",
            description="Atualização parcial válida.",
            starts_at=now,
            ends_at=now + timedelta(days=3),
            is_active=True,
        )
        original_start = promotion.starts_at
        new_end = now + timedelta(days=5)

        response = self.client.patch(
            f"/api/v1/admin/promotions/{promotion.pk}/",
            {"ends_at": new_end.isoformat()},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)

        promotion.refresh_from_db()
        self.assertEqual(promotion.starts_at, original_start)
        self.assertEqual(promotion.ends_at, new_end)