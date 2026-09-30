"""Regressões de publicação de categorias, produtos e promoções."""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product, Promotion


class PublicationTransitionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Decoração",
            slug="decoracao-transicoes",
            is_active=True,
        )
        cls.product = Product.objects.create(
            category=cls.category,
            name="Vaso demonstrativo",
            slug="vaso-transicoes",
            short_description="Vaso fictício.",
            description="Produto criado para testar publicação.",
            price=Decimal("49.90"),
            status=Product.Status.PUBLISHED,
        )

    def setUp(self):
        self.client = APIClient()

    def public_product_slugs(self):
        response = self.client.get("/api/v1/public/products/")
        self.assertEqual(response.status_code, 200)
        return {
            item["slug"]
            for item in response.data["results"]
        }

    def public_promotion_titles(self):
        response = self.client.get("/api/v1/public/promotions/")
        self.assertEqual(response.status_code, 200)
        return {
            item["title"]
            for item in response.data
        }

    def test_desativar_categoria_oculta_produto_sem_exclui_lo(self):
        detail_url = "/api/v1/public/products/vaso-transicoes/"

        self.assertIn(
            self.product.slug,
            self.public_product_slugs(),
        )
        self.assertEqual(
            self.client.get(detail_url).status_code,
            200,
        )

        self.category.is_active = False
        self.category.save(update_fields=["is_active"])

        self.assertNotIn(
            self.product.slug,
            self.public_product_slugs(),
        )
        self.assertEqual(
            self.client.get(detail_url).status_code,
            404,
        )
        self.assertTrue(
            Product.objects.filter(pk=self.product.pk).exists()
        )

        self.category.is_active = True
        self.category.save(update_fields=["is_active"])

        self.assertIn(
            self.product.slug,
            self.public_product_slugs(),
        )
        self.assertEqual(
            self.client.get(detail_url).status_code,
            200,
        )

    def test_promocao_vinculada_ao_produto_segue_visibilidade(self):
        promotion = Promotion.objects.create(
            title="Destaque vinculado",
            description="Promoção fictícia de teste.",
            product=self.product,
            is_active=True,
        )

        self.assertIn(
            promotion.title,
            self.public_promotion_titles(),
        )

        self.product.status = Product.Status.HIDDEN
        self.product.save(update_fields=["status"])

        self.assertNotIn(
            promotion.title,
            self.public_promotion_titles(),
        )
        self.assertTrue(
            Promotion.objects.filter(pk=promotion.pk).exists()
        )

        self.product.status = Product.Status.PUBLISHED
        self.product.save(update_fields=["status"])

        self.assertIn(
            promotion.title,
            self.public_promotion_titles(),
        )

        self.category.is_active = False
        self.category.save(update_fields=["is_active"])

        self.assertNotIn(
            promotion.title,
            self.public_promotion_titles(),
        )

    def test_promocao_sem_produto_nao_depende_da_categoria(self):
        promotion = Promotion.objects.create(
            title="Destaque independente",
            description="Promoção fictícia sem produto vinculado.",
            product=None,
            is_active=True,
        )

        self.category.is_active = False
        self.category.save(update_fields=["is_active"])

        self.assertIn(
            promotion.title,
            self.public_promotion_titles(),
        )

    def test_periodo_e_ativacao_controlam_a_exibicao(self):
        now = timezone.now()

        visible = Promotion.objects.create(
            title="Promoção vigente",
            description="Promoção fictícia vigente.",
            is_active=True,
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção futura",
            description="Promoção fictícia futura.",
            is_active=True,
            starts_at=now + timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção encerrada",
            description="Promoção fictícia encerrada.",
            is_active=True,
            ends_at=now - timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção desativada",
            description="Promoção fictícia desativada.",
            is_active=False,
        )

        self.assertEqual(
            self.public_promotion_titles(),
            {visible.title},
        )