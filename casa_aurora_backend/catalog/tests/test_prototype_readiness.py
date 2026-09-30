"""Testes do diagnóstico não destrutivo do protótipo."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from catalog.models import Category, Product, Promotion, StoreSettings
from catalog.prototype_readiness import evaluate_prototype_readiness


class PrototypeReadinessTests(TestCase):
    def create_public_catalog(self, *, whatsapp_number):
        store = StoreSettings.objects.create(
            pk=1,
            name="Casa Aurora — Presentes e Decoração",
            whatsapp_number=whatsapp_number,
            banner_text="Conheça o catálogo demonstrativo",
        )
        category = Category.objects.create(
            name="Decoração",
            slug="decoracao",
            is_active=True,
        )
        product = Product.objects.create(
            category=category,
            name="Vaso demonstrativo",
            slug="vaso-demonstrativo",
            short_description="Peça decorativa fictícia.",
            description="Produto usado exclusivamente no teste.",
            price=Decimal("49.90"),
            status=Product.Status.PUBLISHED,
        )
        promotion = Promotion.objects.create(
            title="Destaque demonstrativo",
            description="Conteúdo fictício para teste.",
            is_active=True,
        )
        return store, category, product, promotion

    def test_catalogo_publico_configurado_passa_no_modo_strict(self):
        self.create_public_catalog(
            whatsapp_number="5511999999999"
        )
        output = StringIO()

        call_command(
            "check_prototype",
            strict=True,
            stdout=output,
        )

        self.assertIn(
            "Pré-condições verificadas sem pendências.",
            output.getvalue(),
        )

    @override_settings(
        ALLOWED_HOSTS=["localhost", "127.0.0.1"]
    )
    def test_cliente_interno_usa_host_autorizado_no_ambiente_local(self):
        self.create_public_catalog(
            whatsapp_number="5511999999999"
        )

        report = evaluate_prototype_readiness()

        http_issues = [
            issue
            for issue in report.issues
            if issue.code.startswith("public_")
        ]
        self.assertEqual(http_issues, [])

    def test_catalogo_vazio_retorna_pendencias_sem_criar_dados(self):
        report = evaluate_prototype_readiness()

        self.assertFalse(report.ready)
        self.assertIn(
            "store_count",
            {issue.code for issue in report.issues},
        )
        self.assertIn(
            "active_categories",
            {issue.code for issue in report.issues},
        )
        self.assertIn(
            "public_products",
            {issue.code for issue in report.issues},
        )
        self.assertEqual(StoreSettings.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Promotion.objects.count(), 0)

    def test_numero_do_seed_e_identificado_sem_modificar_loja(self):
        store, _, _, _ = self.create_public_catalog(
            whatsapp_number="999999999999999"
        )

        report = evaluate_prototype_readiness()
        store.refresh_from_db()

        self.assertFalse(report.ready)
        self.assertIn(
            "demo_whatsapp",
            {issue.code for issue in report.issues},
        )
        self.assertEqual(
            store.whatsapp_number,
            "999999999999999",
        )

    def test_modo_strict_retorna_erro_com_pendencias(self):
        output = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "check_prototype",
                strict=True,
                stdout=output,
            )

        self.assertIn(
            "Pendências encontradas:",
            output.getvalue(),
        )

    def test_comando_nao_altera_contagens(self):
        self.create_public_catalog(
            whatsapp_number="5511999999999"
        )
        before = (
            StoreSettings.objects.count(),
            Category.objects.count(),
            Product.objects.count(),
            Promotion.objects.count(),
        )

        call_command(
            "check_prototype",
            stdout=StringIO(),
        )

        after = (
            StoreSettings.objects.count(),
            Category.objects.count(),
            Product.objects.count(),
            Promotion.objects.count(),
        )

        self.assertEqual(after, before)