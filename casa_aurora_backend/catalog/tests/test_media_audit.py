"""Testes da auditoria não destrutiva de referências de imagens."""

from io import BytesIO, StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from PIL import Image

from catalog.media_audit import inspect_media_references
from catalog.models import Category, Product, Promotion, StoreSettings


class MediaAuditTests(TestCase):
    def setUp(self):
        self.temporary_media = TemporaryDirectory()
        self.addCleanup(self.temporary_media.cleanup)

        media_override = override_settings(
            MEDIA_ROOT=self.temporary_media.name
        )
        media_override.enable()
        self.addCleanup(media_override.disable)

        self.category = Category.objects.create(
            name="Decoração",
            slug="decoracao-auditoria",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            name="Produto demonstrativo",
            slug="produto-auditoria",
            short_description="Produto fictício.",
            description="Usado somente nos testes.",
            price="49.90",
        )
        self.store = StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
        )
        self.promotion = Promotion.objects.create(
            title="Promoção de teste",
            description="Conteúdo fictício.",
        )

    def image_bytes(self):
        buffer = BytesIO()
        Image.new(
            "RGB",
            (8, 8),
            color=(140, 120, 100),
        ).save(buffer, format="PNG")
        return buffer.getvalue()

    def test_referencias_vazias_nao_sao_erros(self):
        report = inspect_media_references()

        self.assertEqual(report.checked, 0)
        self.assertEqual(report.missing, ())
        self.assertEqual(report.errors, ())
        self.assertTrue(report.ok)

    def test_arquivo_existente_e_contabilizado_sem_pendencias(self):
        self.product.main_image.save(
            "existente.png",
            ContentFile(self.image_bytes()),
            save=True,
        )

        report = inspect_media_references()

        self.assertEqual(report.checked, 1)
        self.assertEqual(report.missing, ())
        self.assertEqual(report.errors, ())
        self.assertTrue(report.ok)

    def test_arquivo_ausente_e_reportado_sem_modificar_registro(self):
        self.product.main_image.name = "products/ausente.png"
        self.product.save(update_fields=["main_image"])

        report = inspect_media_references()

        self.assertEqual(report.checked, 1)
        self.assertEqual(len(report.missing), 1)
        self.assertEqual(report.missing[0].field, "main_image")
        self.assertEqual(
            report.missing[0].name,
            "products/ausente.png",
        )
        self.assertFalse(report.ok)

        self.product.refresh_from_db()
        self.assertEqual(
            self.product.main_image.name,
            "products/ausente.png",
        )

    def test_tres_campos_de_imagem_sao_inspecionados(self):
        self.product.main_image.name = "products/ausente.png"
        self.product.save(update_fields=["main_image"])
        self.store.banner_image.name = "store/ausente.png"
        self.store.save(update_fields=["banner_image"])
        self.promotion.image.name = "promotions/ausente.png"
        self.promotion.save(update_fields=["image"])

        report = inspect_media_references()

        self.assertEqual(report.checked, 3)
        self.assertEqual(len(report.missing), 3)
        self.assertEqual(report.errors, ())

    def test_erro_do_storage_nao_e_confundido_com_arquivo_ausente(self):
        self.product.main_image.name = "products/indisponivel.png"
        self.product.save(update_fields=["main_image"])

        with patch.object(
            self.product.main_image.storage,
            "exists",
            side_effect=OSError("storage indisponível"),
        ):
            report = inspect_media_references()

        self.assertEqual(report.checked, 1)
        self.assertEqual(report.missing, ())
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0].reason, "OSError")

    def test_modo_strict_retorna_erro_sem_apagar_arquivo(self):
        self.product.main_image.name = "products/ausente.png"
        self.product.save(update_fields=["main_image"])

        output = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "audit_media",
                strict=True,
                stdout=output,
            )

        self.assertIn(
            "Arquivos ausentes: 1",
            output.getvalue(),
        )
        self.product.refresh_from_db()
        self.assertEqual(
            self.product.main_image.name,
            "products/ausente.png",
        )