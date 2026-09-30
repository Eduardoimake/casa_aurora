"""Testes de visibilidade, filtros e paginação da API pública."""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Category, Product, Promotion, StoreSettings


class PublicAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            display_order=1,
            is_active=True,
        )
        cls.inactive_category = Category.objects.create(
            name="Categoria inativa",
            slug="inativa",
            display_order=2,
            is_active=False,
        )

        cls.visible_product = Product.objects.create(
            category=cls.active_category,
            name="Vaso Aurora",
            slug="vaso-aurora",
            short_description="Vaso demonstrativo de cerâmica.",
            description="Descrição completa de um produto fictício.",
            price=Decimal("89.90"),
            is_featured=True,
            status=Product.Status.PUBLISHED,
        )
        cls.hidden_product = Product.objects.create(
            category=cls.active_category,
            name="Produto oculto",
            slug="produto-oculto",
            short_description="Não deve aparecer.",
            description="Produto demonstrativo oculto.",
            price=Decimal("49.90"),
            status=Product.Status.HIDDEN,
        )
        cls.inactive_category_product = Product.objects.create(
            category=cls.inactive_category,
            name="Produto de categoria inativa",
            slug="produto-categoria-inativa",
            short_description="Não deve aparecer.",
            description="Produto demonstrativo não exibível.",
            price=Decimal("59.90"),
            status=Product.Status.PUBLISHED,
        )

        StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
            banner_text="Catálogo demonstrativo",
        )

    def setUp(self):
        self.client = APIClient()

    def test_categoria_publica_inclui_apenas_ativas(self):
        response = self.client.get("/api/v1/public/categories/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(
            [item["slug"] for item in response.data],
            ["decoracao"],
        )

    def test_loja_publica_retorna_banner_e_contato(self):
        response = self.client.get("/api/v1/public/store/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["name"],
            "Casa Aurora — Presentes e Decoração",
        )
        self.assertEqual(
            response.data["banner_text"],
            "Catálogo demonstrativo",
        )
        self.assertEqual(
            response.data["whatsapp_number"],
            "999999999999999",
        )
        self.assertIsNone(response.data["banner_image"])

    def test_loja_nao_configurada_retorna_404(self):
        StoreSettings.objects.all().delete()

        response = self.client.get("/api/v1/public/store/")

        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.data)

    def test_listagem_mostra_somente_produtos_publicaveis(self):
        response = self.client.get("/api/v1/public/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data),
            {"count", "next", "previous", "results"},
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            [item["slug"] for item in response.data["results"]],
            ["vaso-aurora"],
        )

    def test_detalhe_publico_retorna_produto_e_preco_decimal(self):
        response = self.client.get(
            "/api/v1/public/products/vaso-aurora/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["price"], "89.90")
        self.assertEqual(
            response.data["category"]["slug"],
            "decoracao",
        )
        self.assertEqual(
            response.data["description"],
            "Descrição completa de um produto fictício.",
        )

    def test_detalhe_nao_revela_produto_oculto(self):
        response = self.client.get(
            "/api/v1/public/products/produto-oculto/"
        )
        self.assertEqual(response.status_code, 404)

    def test_detalhe_nao_revela_produto_de_categoria_inativa(self):
        response = self.client.get(
            "/api/v1/public/products/produto-categoria-inativa/"
        )
        self.assertEqual(response.status_code, 404)

    def test_busca_por_nome_e_descricao_curta(self):
        by_name = self.client.get(
            "/api/v1/public/products/",
            {"search": "Aurora"},
        )
        by_description = self.client.get(
            "/api/v1/public/products/",
            {"search": "cerâmica"},
        )

        self.assertEqual(by_name.status_code, 200)
        self.assertEqual(by_description.status_code, 200)
        self.assertEqual(by_name.data["count"], 1)
        self.assertEqual(by_description.data["count"], 1)
        self.assertEqual(
            by_name.data["results"][0]["slug"],
            "vaso-aurora",
        )

    def test_filtro_por_slug_da_categoria(self):
        visible = self.client.get(
            "/api/v1/public/products/",
            {"category": "decoracao"},
        )
        inactive = self.client.get(
            "/api/v1/public/products/",
            {"category": "inativa"},
        )

        self.assertEqual(visible.status_code, 200)
        self.assertEqual(visible.data["count"], 1)
        self.assertEqual(inactive.status_code, 200)
        self.assertEqual(inactive.data["count"], 0)

    def test_filtro_de_destaque(self):
        featured = self.client.get(
            "/api/v1/public/products/",
            {"featured": "true"},
        )

        self.assertEqual(featured.status_code, 200)
        self.assertEqual(featured.data["count"], 1)
        self.assertTrue(featured.data["results"][0]["is_featured"])

        self.visible_product.is_featured = False
        self.visible_product.save(update_fields=["is_featured"])

        no_featured = self.client.get(
            "/api/v1/public/products/",
            {"featured": "true"},
        )
        self.assertEqual(no_featured.data["count"], 0)

    def test_filtro_de_destaque_invalido_retorna_400(self):
        response = self.client.get(
            "/api/v1/public/products/",
            {"featured": "false"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("featured", response.data)

    def test_ordenacao_permitida_e_rejeicao_de_ordenacao_invalida(self):
        Product.objects.create(
            category=self.active_category,
            name="Almofada demonstrativa",
            slug="almofada-demonstrativa",
            short_description="Peça fictícia.",
            description="Descrição de teste.",
            price=Decimal("39.90"),
            status=Product.Status.PUBLISHED,
        )

        ordered = self.client.get(
            "/api/v1/public/products/",
            {"ordering": "price"},
        )
        invalid = self.client.get(
            "/api/v1/public/products/",
            {"ordering": "created_at"},
        )

        self.assertEqual(ordered.status_code, 200)
        self.assertEqual(
            [item["slug"] for item in ordered.data["results"]],
            ["almofada-demonstrativa", "vaso-aurora"],
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("ordering", invalid.data)

    def test_paginacao_publica(self):
        for number in range(13):
            Product.objects.create(
                category=self.active_category,
                name=f"Peça demonstrativa {number:02d}",
                slug=f"peca-demonstrativa-{number:02d}",
                short_description="Produto fictício.",
                description="Criado para verificar a paginação.",
                price=Decimal("19.90"),
                status=Product.Status.PUBLISHED,
            )

        first_page = self.client.get(
            "/api/v1/public/products/",
            {"page": 1},
        )
        second_page = self.client.get(
            "/api/v1/public/products/",
            {"page": 2},
        )

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(first_page.data["count"], 14)
        self.assertEqual(len(first_page.data["results"]), 12)
        self.assertEqual(len(second_page.data["results"]), 2)
        self.assertIsNotNone(first_page.data["next"])
        self.assertIsNotNone(second_page.data["previous"])

    def test_promocoes_exibem_apenas_registros_elegiveis(self):
        now = timezone.now()

        Promotion.objects.create(
            title="Promoção visível",
            description="Promoção fictícia atual.",
            product=self.visible_product,
            is_active=True,
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção inativa",
            description="Não deve aparecer.",
            is_active=False,
        )
        Promotion.objects.create(
            title="Promoção futura",
            description="Não deve aparecer.",
            is_active=True,
            starts_at=now + timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção expirada",
            description="Não deve aparecer.",
            is_active=True,
            ends_at=now - timedelta(days=1),
        )
        Promotion.objects.create(
            title="Promoção de produto oculto",
            description="Não deve aparecer.",
            product=self.hidden_product,
            is_active=True,
        )
        Promotion.objects.create(
            title="Promoção de categoria inativa",
            description="Não deve aparecer.",
            product=self.inactive_category_product,
            is_active=True,
        )

        response = self.client.get("/api/v1/public/promotions/")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(
            [item["title"] for item in response.data],
            ["Promoção visível"],
        )