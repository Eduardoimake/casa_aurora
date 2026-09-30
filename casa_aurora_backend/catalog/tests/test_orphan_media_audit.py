"""Testes do inventário não destrutivo de mídias sem referência."""

from decimal import Decimal
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from catalog.models import Category, Product, Promotion, StoreSettings
from catalog.orphan_media_audit import inspect_orphan_media


class OrphanMediaAuditTests(TestCase):
    def setUp(self):
        self.temporary_media = TemporaryDirectory()
        self.addCleanup(self.temporary_media.cleanup)

        settings_override = override_settings(
            MEDIA_ROOT=self.temporary_media.name
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)

        self.storage = Product._meta.get_field(
            "main_image"
        ).storage

        category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=category,
            name="Produto demonstrativo",
            slug="produto-demonstrativo",
            short_description="Produto fictício.",
            description="Criado para testar o inventário.",
            price=Decimal("49.90"),
        )
        self.store = StoreSettings.objects.create(
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number="999999999999999",
        )
        self.promotion = Promotion.objects.create(
            title="Promoção de teste",
            description="Conteúdo fictício.",
        )

    def save_file(self, name):
        return self.storage.save(
            name,
            ContentFile(b"conteudo artificial de teste"),
        )

    def test_diretorios_ausentes_resultam_em_inventario_vazio(self):
        report = inspect_orphan_media()

        self.assertEqual(report.scanned_files, 0)
        self.assertEqual(report.candidates, ())
        self.assertEqual(report.issues, ())
        self.assertTrue(report.complete)

    def test_arquivo_referenciado_nao_e_candidato(self):
        stored_name = self.save_file("products/referenciado.png")
        self.product.main_image.name = stored_name
        self.product.save(update_fields=["main_image"])

        report = inspect_orphan_media()

        self.assertEqual(report.scanned_files, 1)
        self.assertEqual(report.candidates, ())
        self.assertEqual(report.issues, ())
        self.assertTrue(self.storage.exists(stored_name))

    def test_arquivo_sem_referencia_e_candidato_mas_nao_e_apagado(self):
        stored_name = self.save_file("products/candidato.png")

        report = inspect_orphan_media()

        self.assertEqual(report.scanned_files, 1)
        self.assertEqual(report.candidates, (stored_name,))
        self.assertTrue(self.storage.exists(stored_name))

    def test_inventario_considera_banner_e_imagem_da_promocao(self):
        banner_name = self.save_file("store/banner.png")
        promotion_name = self.save_file(
            "promotions/destaque.png"
        )

        self.store.banner_image.name = banner_name
        self.store.save(update_fields=["banner_image"])
        self.promotion.image.name = promotion_name
        self.promotion.save(update_fields=["image"])

        report = inspect_orphan_media()

        self.assertEqual(report.scanned_files, 2)
        self.assertEqual(report.candidates, ())
        self.assertEqual(report.issues, ())

    def test_storage_sem_listdir_retorna_inspecao_incompleta(self):
        with patch.object(
            self.storage,
            "listdir",
            side_effect=NotImplementedError(
                "Listagem não suportada"
            ),
        ):
            report = inspect_orphan_media()

        self.assertFalse(report.complete)
        self.assertEqual(report.candidates, ())
        self.assertTrue(report.issues)
        self.assertEqual(
            report.issues[0].kind,
            "listing_not_supported",
        )

    def test_modo_strict_falha_sem_excluir_candidato(self):
        stored_name = self.save_file("products/candidato.png")
        output = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "audit_orphan_media",
                strict=True,
                stdout=output,
            )

        self.assertIn(
            "Candidatos sem referência: 1",
            output.getvalue(),
        )
        self.assertTrue(self.storage.exists(stored_name))