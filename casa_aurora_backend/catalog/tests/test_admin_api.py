"""Testes das permissões e operações administrativas da API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product, Promotion, StoreSettings


class AdminAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.staff = user_model.objects.create_user(
            username="gestor_teste",
            password="SenhaDeTesteForte-456!",
            is_staff=True,
        )
        cls.common_user = user_model.objects.create_user(
            username="usuario_comum_teste",
            password="SenhaDeTesteForte-456!",
            is_staff=False,
        )
        cls.category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            is_active=True,
        )
        cls.store = StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
            banner_text="Banner inicial",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate_as_staff(self):
        self.client.force_login(self.staff)

    def product_payload(self, **overrides):
        payload = {
            "category": self.category.pk,
            "name": "Vaso demonstrativo",
            "slug": "vaso-demonstrativo",
            "short_description": "Vaso fictício.",
            "description": "Produto criado para testar a API.",
            "price": "79.90",
            "status": Product.Status.PUBLISHED,
        }
        payload.update(overrides)
        return payload

    def test_anonimo_nao_lista_nem_cria_produtos(self):
        list_response = self.client.get("/api/v1/admin/products/")
        create_response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(Product.objects.count(), 0)

    def test_usuario_comum_nao_lista_nem_cria_produtos(self):
        self.client.force_login(self.common_user)

        list_response = self.client.get("/api/v1/admin/products/")
        create_response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(Product.objects.count(), 0)

    def test_staff_cria_produto_que_aparece_publicamente(self):
        self.authenticate_as_staff()

        created = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )
        public = self.client.get("/api/v1/public/products/")

        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["price"], "79.90")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.data["count"], 1)
        self.assertEqual(
            public.data["results"][0]["slug"],
            "vaso-demonstrativo",
        )

    def test_staff_edita_e_oculta_produto(self):
        product = Product.objects.create(
            category=self.category,
            name="Vaso antes da edição",
            slug="vaso-antes-da-edicao",
            short_description="Produto fictício.",
            description="Descrição inicial.",
            price=Decimal("69.90"),
            status=Product.Status.PUBLISHED,
        )
        self.authenticate_as_staff()

        detail_url = f"/api/v1/admin/products/{product.pk}/"
        updated = self.client.patch(
            detail_url,
            {"name": "Vaso depois da edição", "price": "89.90"},
            format="json",
        )
        visible = self.client.get(
            "/api/v1/public/products/vaso-antes-da-edicao/"
        )
        hidden = self.client.patch(
            detail_url,
            {"status": Product.Status.HIDDEN},
            format="json",
        )
        no_longer_public = self.client.get(
            "/api/v1/public/products/vaso-antes-da-edicao/"
        )

        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(updated.data["price"], "89.90")
        self.assertEqual(visible.status_code, 200)
        self.assertEqual(
            visible.data["name"],
            "Vaso depois da edição",
        )
        self.assertEqual(hidden.status_code, 200, hidden.data)
        self.assertEqual(no_longer_public.status_code, 404)

    def test_staff_exclui_produto(self):
        product = Product.objects.create(
            category=self.category,
            name="Produto para exclusão",
            slug="produto-para-exclusao",
            short_description="Produto fictício.",
            description="Descrição de teste.",
            price=Decimal("29.90"),
            status=Product.Status.HIDDEN,
        )
        self.authenticate_as_staff()

        response = self.client.delete(
            f"/api/v1/admin/products/{product.pk}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Product.objects.filter(pk=product.pk).exists()
        )

    def test_preco_negativo_e_rejeitado_sem_criar_produto(self):
        self.authenticate_as_staff()

        response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(price="-0.01"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.data)
        self.assertEqual(Product.objects.count(), 0)

    def test_dashboard_retorna_contagens_do_catalogo(self):
        Product.objects.create(
            category=self.category,
            name="Produto de teste",
            slug="produto-dashboard",
            short_description="Produto fictício.",
            description="Descrição de teste.",
            price=Decimal("19.90"),
            status=Product.Status.PUBLISHED,
        )
        Promotion.objects.create(
            title="Promoção ativa",
            description="Promoção fictícia.",
            is_active=True,
        )
        Promotion.objects.create(
            title="Promoção inativa",
            description="Promoção fictícia.",
            is_active=False,
        )
        self.authenticate_as_staff()

        response = self.client.get("/api/v1/admin/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["products_count"], 1)
        self.assertEqual(response.data["categories_count"], 1)
        self.assertEqual(
            response.data["active_promotions_count"],
            1,
        )
        self.assertNotIn("sales", response.data)
        self.assertNotIn("revenue", response.data)

    def test_categoria_com_produto_nao_pode_ser_excluida(self):
        Product.objects.create(
            category=self.category,
            name="Produto vinculado",
            slug="produto-vinculado",
            short_description="Produto fictício.",
            description="Descrição de teste.",
            price=Decimal("29.90"),
        )
        self.authenticate_as_staff()

        response = self.client.delete(
            f"/api/v1/admin/categories/{self.category.pk}/"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("detail", response.data)
        self.assertTrue(
            Category.objects.filter(pk=self.category.pk).exists()
        )

    def test_staff_cria_e_altera_categoria(self):
        self.authenticate_as_staff()

        created = self.client.post(
            "/api/v1/admin/categories/",
            {
                "name": "Presentes",
                "slug": "presentes",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(created.status_code, 201, created.data)

        updated = self.client.patch(
            f"/api/v1/admin/categories/{created.data['id']}/",
            {"is_active": False},
            format="json",
        )

        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertFalse(updated.data["is_active"])

    def test_staff_altera_loja_e_edicao_fica_publica(self):
        self.authenticate_as_staff()

        updated = self.client.patch(
            "/api/v1/admin/store/",
            {"banner_text": "Novo banner demonstrativo"},
            format="json",
        )
        public = self.client.get("/api/v1/public/store/")

        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(public.status_code, 200)
        self.assertEqual(
            public.data["banner_text"],
            "Novo banner demonstrativo",
        )

    def test_staff_cria_e_edita_promocao(self):
        self.authenticate_as_staff()

        created = self.client.post(
            "/api/v1/admin/promotions/",
            {
                "title": "Promoção de teste",
                "description": "Destaque fictício.",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(created.status_code, 201, created.data)

        updated = self.client.patch(
            f"/api/v1/admin/promotions/{created.data['id']}/",
            {"is_active": False},
            format="json",
        )

        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertFalse(updated.data["is_active"])