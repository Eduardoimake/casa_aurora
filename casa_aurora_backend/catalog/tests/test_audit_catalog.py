"""Testes do comando de auditoria não destrutiva do catálogo."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from catalog.models import Category, Product, Promotion, StoreSettings


class AuditCatalogTests(TestCase):
    def run_audit(self, *, strict=False):
        output = StringIO()
        call_command(
            "audit_catalog",
            strict=strict,
            stdout=output,
        )
        return output.getvalue()

    def create_store(self, whatsapp_number="5511999999999"):
        return StoreSettings.objects.create(
            name="Loja demonstrativa",
            whatsapp_number=whatsapp_number,
        )

    def create_category(self, *, active=True, slug="decoracao"):
        return Category.objects.create(
            name="Decoração",
            slug=slug,
            is_active=active,
        )

    def create_product(
        self,
        category,
        *,
        status=Product.Status.PUBLISHED,
        slug="vaso-demonstrativo",
    ):
        return Product.objects.create(
            category=category,
            name="Vaso demonstrativo",
            slug=slug,
            short_description="Peça fictícia.",
            description="Produto criado para os testes.",
            price=Decimal("49.90"),
            status=status,
        )

    def test_catalogo_visivel_sem_numero_do_seed_nao_gera_avisos(self):
        self.create_store()
        category = self.create_category()
        self.create_product(category)

        output = self.run_audit(strict=True)

        self.assertIn(
            "Auditoria concluída sem avisos.",
            output,
        )
        self.assertIn(
            "Produtos: 1; públicos: 1",
            output,
        )

    def test_catalogo_vazio_gera_avisos_sem_alterar_o_banco(self):
        output = self.run_audit()

        self.assertIn("Configuração da loja", output)
        self.assertIn(
            "Não há categorias cadastradas.",
            output,
        )
        self.assertIn(
            "Não há produtos cadastrados.",
            output,
        )
        self.assertEqual(StoreSettings.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)

    def test_modo_strict_falha_quando_ha_avisos(self):
        output = StringIO()

        with self.assertRaises(CommandError):
            call_command(
                "audit_catalog",
                strict=True,
                stdout=output,
            )

        self.assertIn(
            "Avisos encontrados",
            output.getvalue(),
        )

    def test_alerta_numero_demonstrativo_sem_sobrescrever_valor(self):
        store = self.create_store(
            whatsapp_number="999999999999999",
        )
        category = self.create_category()
        self.create_product(category)

        output = self.run_audit()

        self.assertIn(
            "WhatsApp da loja ainda é o número fictício",
            output,
        )
        store.refresh_from_db()
        self.assertEqual(
            store.whatsapp_number,
            "999999999999999",
        )

    def test_produto_publicado_em_categoria_inativa_gera_aviso(self):
        self.create_store()
        category = self.create_category(active=False)
        product = self.create_product(category)

        output = self.run_audit()

        self.assertIn(
            "pertence(m) a categoria(s) inativa(s)",
            output,
        )
        self.assertIn(
            "Produtos: 1; públicos: 0",
            output,
        )

        product.refresh_from_db()
        self.assertEqual(
            product.status,
            Product.Status.PUBLISHED,
        )
        self.assertFalse(product.category.is_active)

    def test_promocao_atual_ligada_a_produto_oculto_gera_aviso(self):
        self.create_store()
        category = self.create_category()
        self.create_product(
            category,
            status=Product.Status.PUBLISHED,
        )
        hidden_product = self.create_product(
            category,
            status=Product.Status.HIDDEN,
            slug="produto-oculto",
        )
        promotion = Promotion.objects.create(
            title="Promoção não exibível",
            description="Exemplo fictício.",
            product=hidden_product,
            is_active=True,
        )

        output = self.run_audit()

        self.assertIn(
            "vinculada(s) a produto(s) não visível(is)",
            output,
        )
        promotion.refresh_from_db()
        self.assertTrue(promotion.is_active)