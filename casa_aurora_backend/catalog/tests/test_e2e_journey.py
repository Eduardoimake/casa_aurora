"""Jornada integrada de sessão, CSRF, gestão e catálogo público."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product


class EndToEndJourneyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="gestor_jornada",
            password="SenhaDeTesteForte-789!",
            is_staff=True,
        )
        cls.category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            is_active=True,
        )

    def setUp(self):
        self.admin_client = APIClient(enforce_csrf_checks=True)
        self.public_client = APIClient()

    def csrf_token(self):
        response = self.admin_client.get(
            "/api/v1/auth/csrf/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.data)
        self.assertIn("csrftoken", self.admin_client.cookies)

        return response.data["csrfToken"]

    def login(self):
        token_before_login = self.csrf_token()

        response = self.admin_client.post(
            "/api/v1/auth/login/",
            {
                "username": "gestor_jornada",
                "password": "SenhaDeTesteForte-789!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=token_before_login,
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn("sessionid", self.admin_client.cookies)
        self.assertTrue(response.data["user"]["is_staff"])
        self.assertIn("csrfToken", response.data)

        return response.data["csrfToken"]

    def product_payload(self):
        return {
            "category": self.category.pk,
            "name": "Vaso da jornada",
            "slug": "vaso-da-jornada",
            "short_description": "Produto fictício para teste.",
            "description": (
                "Produto demonstrativo criado pela API administrativa."
            ),
            "price": "79.90",
            "status": Product.Status.PUBLISHED,
            "is_featured": True,
        }

    def test_criar_publicar_ocultar_e_encerrar_sessao(self):
        csrf_after_login = self.login()

        anonymous_write = self.public_client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )
        self.assertEqual(anonymous_write.status_code, 403)

        missing_csrf = self.admin_client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )
        self.assertEqual(missing_csrf.status_code, 403)
        self.assertFalse(
            Product.objects.filter(
                slug="vaso-da-jornada"
            ).exists()
        )

        created = self.admin_client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )
        self.assertEqual(created.status_code, 201, created.data)

        product_id = created.data["id"]
        public_url = "/api/v1/public/products/vaso-da-jornada/"
        admin_url = f"/api/v1/admin/products/{product_id}/"

        public_detail = self.public_client.get(public_url)
        self.assertEqual(public_detail.status_code, 200)
        self.assertEqual(
            public_detail.data["price"],
            "79.90",
        )

        hidden = self.admin_client.patch(
            admin_url,
            {"status": Product.Status.HIDDEN},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )
        self.assertEqual(hidden.status_code, 200, hidden.data)
        self.assertEqual(
            self.public_client.get(public_url).status_code,
            404,
        )

        logout = self.admin_client.post(
            "/api/v1/auth/logout/",
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )
        self.assertEqual(logout.status_code, 204)

        after_logout = self.admin_client.patch(
            admin_url,
            {"name": "Alteração não autorizada"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )
        self.assertEqual(after_logout.status_code, 403)

        product = Product.objects.get(pk=product_id)
        self.assertEqual(product.name, "Vaso da jornada")
        self.assertEqual(
            product.status,
            Product.Status.HIDDEN,
        )