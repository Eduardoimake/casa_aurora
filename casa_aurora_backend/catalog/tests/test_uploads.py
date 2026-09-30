"""Testes de upload e validação de imagens pela API administrativa."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from catalog.models import Category, Product, Promotion, StoreSettings


class UploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="gestor_upload_teste",
            password="SenhaDeTesteForte-789!",
            is_staff=True,
        )
        cls.category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            is_active=True,
        )
        StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
        )

    def setUp(self):
        self.temporary_media = TemporaryDirectory()
        self.addCleanup(self.temporary_media.cleanup)

        media_override = override_settings(
            MEDIA_ROOT=self.temporary_media.name
        )
        media_override.enable()
        self.addCleanup(media_override.disable)

        self.client = APIClient()
        self.client.force_login(self.staff)

    def image_file(
        self,
        *,
        name="imagem.png",
        image_format="PNG",
        content_type="image/png",
    ):
        buffer = BytesIO()
        Image.new("RGB", (12, 12), color=(180, 140, 100)).save(
            buffer,
            format=image_format,
        )
        return SimpleUploadedFile(
            name,
            buffer.getvalue(),
            content_type=content_type,
        )

    def product_payload(self, image):
        return {
            "category": self.category.pk,
            "name": "Produto ilustrado",
            "slug": "produto-ilustrado",
            "short_description": "Produto fictício com imagem.",
            "description": "Criado exclusivamente para o teste.",
            "price": "59.90",
            "status": Product.Status.PUBLISHED,
            "main_image": image,
        }

    def test_upload_png_valido_em_produto(self):
        response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(self.image_file()),
            format="multipart",
        )

        self.assertEqual(response.status_code, 201, response.data)

        product = Product.objects.get(slug="produto-ilustrado")

        self.assertTrue(
            product.main_image.name.startswith("products/")
        )
        self.assertTrue(
            Path(product.main_image.path).is_file()
        )
        self.assertTrue(
            response.data["main_image"].endswith(
                product.main_image.url
            )
        )

    def test_arquivo_invalido_nao_cria_produto(self):
        invalid_file = SimpleUploadedFile(
            "falso.png",
            b"isto nao e uma imagem",
            content_type="image/png",
        )

        response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(invalid_file),
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("main_image", response.data)
        self.assertFalse(
            Product.objects.filter(
                slug="produto-ilustrado"
            ).exists()
        )

    def test_extensao_divergente_do_conteudo_e_rejeitada(self):
        mismatched_image = self.image_file(
            name="imagem.jpg",
            image_format="PNG",
            content_type="image/jpeg",
        )

        response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(mismatched_image),
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("main_image", response.data)
        self.assertEqual(Product.objects.count(), 0)

    @override_settings(MAX_IMAGE_UPLOAD_MB=1)
    def test_imagem_acima_do_limite_configurado_e_rejeitada(self):
        oversized_file = SimpleUploadedFile(
            "grande.png",
            b"x" * (1024 * 1024 + 1),
            content_type="image/png",
        )

        response = self.client.post(
            "/api/v1/admin/products/",
            self.product_payload(oversized_file),
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("main_image", response.data)
        self.assertEqual(Product.objects.count(), 0)

    def test_upload_de_banner_pela_configuracao_da_loja(self):
        response = self.client.patch(
            "/api/v1/admin/store/",
            {
                "banner_image": self.image_file(
                    name="banner.webp",
                    image_format="WEBP",
                    content_type="image/webp",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 200, response.data)

        store = StoreSettings.objects.get(pk=1)

        self.assertTrue(
            store.banner_image.name.startswith("store/")
        )
        self.assertTrue(
            Path(store.banner_image.path).is_file()
        )
        self.assertTrue(
            response.data["banner_image"].endswith(
                store.banner_image.url
            )
        )

    def test_upload_de_imagem_em_promocao(self):
        response = self.client.post(
            "/api/v1/admin/promotions/",
            {
                "title": "Promoção ilustrada",
                "description": "Destaque fictício com imagem.",
                "is_active": "true",
                "image": self.image_file(
                    name="promocao.jpeg",
                    image_format="JPEG",
                    content_type="image/jpeg",
                ),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201, response.data)

        promotion = Promotion.objects.get(
            title="Promoção ilustrada"
        )

        self.assertTrue(
            promotion.image.name.startswith("promotions/")
        )
        self.assertTrue(
            Path(promotion.image.path).is_file()
        )
        self.assertTrue(
            response.data["image"].endswith(
                promotion.image.url
            )
        )