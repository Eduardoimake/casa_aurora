"""Testes de login por sessão e proteção CSRF da API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, Product


class SessionAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.staff = user_model.objects.create_user(
            username="administrador_teste",
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

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def csrf_token(self):
        response = self.client.get("/api/v1/auth/csrf/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.data)
        self.assertIn("csrftoken", self.client.cookies)

        return response.data["csrfToken"]

    def staff_login(self):
        token_before_login = self.csrf_token()

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "administrador_teste",
                "password": "SenhaDeTesteForte-456!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=token_before_login,
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn("sessionid", self.client.cookies)
        self.assertTrue(response.data["user"]["is_staff"])
        self.assertIn("csrfToken", response.data)

        return response.data["csrfToken"]

    def product_payload(self):
        return {
            "category": self.category.pk,
            "name": "Produto do teste CSRF",
            "slug": "produto-teste-csrf",
            "short_description": "Produto fictício.",
            "description": "Criado para verificar a sessão e o CSRF.",
            "price": "49.90",
            "status": Product.Status.PUBLISHED,
        }

    def test_token_csrf_pode_ser_obtido_antes_do_login(self):
        self.csrf_token()

    def test_login_sem_csrf_e_rejeitado(self):
        self.csrf_token()

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "administrador_teste",
                "password": "SenhaDeTesteForte-456!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_staff_cria_sessao_e_permite_consultar_me(self):
        self.staff_login()

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["username"],
            "administrador_teste",
        )
        self.assertTrue(response.data["is_staff"])

    def test_usuario_comum_nao_obtem_sessao_administrativa(self):
        token = self.csrf_token()

        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "usuario_comum_teste",
                "password": "SenhaDeTesteForte-456!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("sessionid", self.client.cookies)
        self.assertEqual(
            self.client.get("/api/v1/admin/dashboard/").status_code,
            403,
        )

    def test_escrita_exige_csrf_apos_login(self):
        csrf_after_login = self.staff_login()

        missing_csrf = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
        )

        self.assertEqual(missing_csrf.status_code, 403)
        self.assertFalse(
            Product.objects.filter(
                slug="produto-teste-csrf"
            ).exists()
        )

        created = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(),
            format="json",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )

        self.assertEqual(created.status_code, 201, created.data)
        self.assertTrue(
            Product.objects.filter(
                slug="produto-teste-csrf"
            ).exists()
        )

    def test_logout_exige_csrf_e_encerra_sessao(self):
        csrf_after_login = self.staff_login()

        logout_without_csrf = self.client.post(
            "/api/v1/auth/logout/"
        )
        self.assertEqual(logout_without_csrf.status_code, 403)

        logout = self.client.post(
            "/api/v1/auth/logout/",
            HTTP_X_CSRFTOKEN=csrf_after_login,
        )

        self.assertEqual(logout.status_code, 204)
        self.assertEqual(
            self.client.get("/api/v1/auth/me/").status_code,
            403,
        )