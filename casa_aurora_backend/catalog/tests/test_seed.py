"""Testes do seed demonstrativo e de sua idempotência."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from catalog.models import Category, Product, Promotion, StoreSettings


class SeedDemoTests(TestCase):
    def run_seed(self):
        output = StringIO()
        call_command("seed_demo", stdout=output)
        return output.getvalue()

    def test_seed_cria_catalogo_e_banner_demonstrativos(self):
        output = self.run_seed()

        self.assertIn("Seed demonstrativo concluído", output)
        self.assertEqual(StoreSettings.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 9)
        self.assertEqual(Promotion.objects.count(), 1)

        store = StoreSettings.objects.get(pk=1)
        self.assertEqual(
            store.name,
            "Casa Aurora — Presentes e Decoração",
        )
        self.assertTrue(store.banner_text)
        self.assertFalse(bool(store.banner_image))

        self.assertEqual(
            Product.objects.filter(
                status=Product.Status.PUBLISHED
            ).count(),
            9,
        )
        self.assertFalse(
            Product.objects.exclude(
                category__is_active=True
            ).exists()
        )
        self.assertTrue(Promotion.objects.get().is_active)

    def test_reexecutar_nao_duplica_nem_sobrescreve_edicao(self):
        self.run_seed()

        edited_product = Product.objects.get(
            slug="vaso-ceramico-aurora"
        )
        edited_product.name = "Nome definido pela administração"
        edited_product.status = Product.Status.HIDDEN
        edited_product.save(update_fields=["name", "status"])

        store = StoreSettings.objects.get(pk=1)
        store.banner_text = "Banner personalizado"
        store.save(update_fields=["banner_text"])

        self.run_seed()

        edited_product.refresh_from_db()
        store.refresh_from_db()

        self.assertEqual(StoreSettings.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 9)
        self.assertEqual(Promotion.objects.count(), 1)
        self.assertEqual(
            edited_product.name,
            "Nome definido pela administração",
        )
        self.assertEqual(
            edited_product.status,
            Product.Status.HIDDEN,
        )
        self.assertEqual(store.banner_text, "Banner personalizado")

    def test_nao_cria_usuarios(self):
        self.run_seed()
        self.assertEqual(get_user_model().objects.count(), 0)