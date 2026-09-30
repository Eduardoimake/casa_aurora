"""Regressões dos parâmetros públicos de consulta ao catálogo."""

from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product


class CatalogQueryRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_category = Category.objects.create(
            name="Decoração",
            slug="decoracao-consultas",
            is_active=True,
        )
        cls.other_category = Category.objects.create(
            name="Presentes",
            slug="presentes-consultas",
            is_active=True,
        )
        cls.inactive_category = Category.objects.create(
            name="Reservados",
            slug="reservados-consultas",
            is_active=False,
        )

        product_data = (
            (
                cls.active_category,
                "vaso-escuro",
                "Vaso escuro",
                "Peça de cerâmica fictícia.",
                "79.90",
                True,
                Product.Status.PUBLISHED,
            ),
            (
                cls.active_category,
                "vaso-claro",
                "Vaso claro",
                "Peça clara demonstrativa.",
                "89.90",
                False,
                Product.Status.PUBLISHED,
            ),
            (
                cls.other_category,
                "caneca-presente",
                "Caneca presente",
                "Presente fictício.",
                "39.90",
                True,
                Product.Status.PUBLISHED,
            ),
            (
                cls.active_category,
                "produto-oculto-consultas",
                "Produto oculto",
                "Não deve aparecer.",
                "19.90",
                True,
                Product.Status.HIDDEN,
            ),
            (
                cls.inactive_category,
                "produto-reservado-consultas",
                "Produto reservado",
                "Não deve aparecer.",
                "29.90",
                True,
                Product.Status.PUBLISHED,
            ),
        )

        for (
            category,
            slug,
            name,
            short_description,
            price,
            featured,
            publication_status,
        ) in product_data:
            Product.objects.create(
                category=category,
                slug=slug,
                name=name,
                short_description=short_description,
                description="Produto fictício para teste de consulta.",
                price=Decimal(price),
                is_featured=featured,
                status=publication_status,
            )

    def setUp(self):
        self.client = APIClient()

    def list_products(self, params=None):
        response = self.client.get(
            "/api/v1/public/products/",
            params or {},
        )
        self.assertEqual(response.status_code, 200, response.data)
        return response.data

    def test_busca_ignora_produtos_nao_publicaveis(self):
        data = self.list_products({"search": "Vaso"})

        self.assertEqual(
            {item["slug"] for item in data["results"]},
            {"vaso-escuro", "vaso-claro"},
        )
        self.assertEqual(data["count"], 2)

    def test_filtro_de_categoria_nao_expõe_categoria_inativa(self):
        visible = self.list_products(
            {"category": "decoracao-consultas"}
        )
        inactive = self.list_products(
            {"category": "reservados-consultas"}
        )

        self.assertEqual(visible["count"], 2)
        self.assertEqual(inactive["count"], 0)

    def test_destaque_pode_ser_combinado_com_categoria(self):
        data = self.list_products(
            {
                "category": "decoracao-consultas",
                "featured": "true",
            }
        )

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["slug"],
            "vaso-escuro",
        )

    def test_ordenacao_por_preco_exclui_registros_ocultos(self):
        data = self.list_products({"ordering": "price"})

        self.assertEqual(
            [item["slug"] for item in data["results"]],
            [
                "caneca-presente",
                "vaso-escuro",
                "vaso-claro",
            ],
        )
        self.assertEqual(data["count"], 3)

    def test_ordenacao_nao_permitida_retorna_400(self):
        response = self.client.get(
            "/api/v1/public/products/",
            {"ordering": "created_at"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("ordering", response.data)

    def test_paginacao_mantem_filtros_e_ordenacao(self):
        first = self.list_products(
            {
                "category": "decoracao-consultas",
                "page_size": 1,
                "page": 1,
                "ordering": "price",
            }
        )
        second = self.list_products(
            {
                "category": "decoracao-consultas",
                "page_size": 1,
                "page": 2,
                "ordering": "price",
            }
        )

        self.assertEqual(first["count"], 2)
        self.assertEqual(second["count"], 2)
        self.assertEqual(
            first["results"][0]["slug"],
            "vaso-escuro",
        )
        self.assertEqual(
            second["results"][0]["slug"],
            "vaso-claro",
        )
        self.assertIsNotNone(first["next"])
        self.assertIsNotNone(second["previous"])

    def test_pagina_inexistente_retorna_404(self):
        response = self.client.get(
            "/api/v1/public/products/",
            {"page": 99},
        )

        self.assertEqual(response.status_code, 404)

    def test_page_size_acima_do_maximo_e_limitado(self):
        data = self.list_products({"page_size": 999})

        self.assertEqual(data["count"], 3)
        self.assertEqual(len(data["results"]), 3)