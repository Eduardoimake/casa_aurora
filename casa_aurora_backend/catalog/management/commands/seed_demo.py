"""Dados fictícios reproduzíveis para a loja Casa Aurora."""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product, Promotion, StoreSettings


CATEGORY_DATA = (
    {
        "slug": "decoracao",
        "name": "Decoração",
        "short_description": "Peças demonstrativas para compor ambientes.",
        "display_order": 1,
        "is_active": True,
    },
    {
        "slug": "presentes",
        "name": "Presentes",
        "short_description": "Ideias demonstrativas para presentear.",
        "display_order": 2,
        "is_active": True,
    },
    {
        "slug": "organizacao",
        "name": "Organização",
        "short_description": "Itens demonstrativos para organizar espaços.",
        "display_order": 3,
        "is_active": True,
    },
)

PRODUCT_DATA = (
    (
        "decoracao",
        "vaso-ceramico-aurora",
        "Vaso cerâmico Aurora",
        "Vaso decorativo de cerâmica para composição de ambientes.",
        "Peça fictícia de cerâmica para decoração de mesas e estantes. "
        "Não acompanha plantas.",
        "89.90",
        True,
        1,
    ),
    (
        "decoracao",
        "almofada-trama-suave",
        "Almofada Trama Suave",
        "Almofada decorativa de textura suave.",
        "Produto demonstrativo para compor sofás e poltronas; medidas e "
        "materiais finais deverão ser definidos antes de uma venda real.",
        "69.90",
        False,
        2,
    ),
    (
        "decoracao",
        "porta-retrato-horizonte",
        "Porta-retrato Horizonte",
        "Porta-retrato decorativo para lembranças.",
        "Modelo fictício para apoiar sobre mesa ou estante; "
        "foto ilustrativa não incluída.",
        "49.90",
        False,
        3,
    ),
    (
        "presentes",
        "caneca-amanhecer",
        "Caneca Amanhecer",
        "Caneca demonstrativa para presentear.",
        "Caneca fictícia de uso cotidiano apresentada somente para "
        "demonstrar o catálogo.",
        "39.90",
        True,
        1,
    ),
    (
        "presentes",
        "kit-cartoes-afeto",
        "Kit Cartões Afeto",
        "Conjunto demonstrativo de cartões.",
        "Conjunto fictício de cartões para mensagens pessoais; "
        "imagens e embalagem não incluídas.",
        "29.90",
        False,
        2,
    ),
    (
        "presentes",
        "vela-noite-serena",
        "Vela Noite Serena",
        "Vela decorativa demonstrativa.",
        "Item fictício para apresentação do site; fragrância e "
        "composição devem ser definidas antes de comercialização.",
        "54.90",
        False,
        3,
    ),
    (
        "organizacao",
        "cesto-tecido-leve",
        "Cesto Tecido Leve",
        "Cesto decorativo para organizar pequenos objetos.",
        "Peça fictícia para organização de acessórios e objetos leves.",
        "79.90",
        False,
        1,
    ),
    (
        "organizacao",
        "caixa-memorias",
        "Caixa Memórias",
        "Caixa organizadora demonstrativa.",
        "Caixa fictícia para guardar papéis e pequenas recordações.",
        "59.90",
        False,
        2,
    ),
    (
        "organizacao",
        "suporte-mesa-clara",
        "Suporte Mesa Clara",
        "Suporte de mesa demonstrativo.",
        "Acessório fictício para organizar objetos de uso diário "
        "em uma mesa.",
        "44.90",
        False,
        3,
    ),
)

STORE_DEFAULTS = {
    "name": "Casa Aurora — Presentes e Decoração",
    "slogan": "Ideias fictícias para acolher e presentear",
    "description": (
        "Loja fictícia criada exclusivamente para demonstração de um "
        "catálogo e de seu painel administrativo."
    ),
    "whatsapp_number": "999999999999999",
    "demo_address": "Endereço não disponível — estabelecimento fictício",
    "opening_hours": "Atendimento demonstrativo: horários não definidos",
    "banner_text": "Conheça a coleção demonstrativa da Casa Aurora",
    "primary_button_text": "Explorar produtos",
}

PROMOTION_TITLE = "Destaque demonstrativo Casa Aurora"

PROMOTION_DEFAULTS = {
    "description": (
        "Promoção fictícia de demonstração, sem desconto, prazo ou "
        "condições comerciais reais."
    ),
    "is_active": True,
    "display_order": 1,
}


class Command(BaseCommand):
    help = (
        "Cria dados fictícios da Casa Aurora sem sobrescrever "
        "registros existentes."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        counts = {
            "store": 0,
            "categories": 0,
            "products": 0,
            "promotions": 0,
        }

        _, created = StoreSettings.objects.get_or_create(
            pk=1,
            defaults=STORE_DEFAULTS,
        )
        counts["store"] += int(created)

        categories = {}

        for data in CATEGORY_DATA:
            slug = data["slug"]
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    key: value
                    for key, value in data.items()
                    if key != "slug"
                },
            )
            categories[slug] = category
            counts["categories"] += int(created)

        for (
            category_slug,
            slug,
            name,
            short_description,
            description,
            price,
            featured,
            order,
        ) in PRODUCT_DATA:
            _, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": categories[category_slug],
                    "name": name,
                    "short_description": short_description,
                    "description": description,
                    "price": Decimal(price),
                    "is_featured": featured,
                    "status": Product.Status.PUBLISHED,
                    "display_order": order,
                },
            )
            counts["products"] += int(created)

        _, created = Promotion.objects.get_or_create(
            title=PROMOTION_TITLE,
            defaults=PROMOTION_DEFAULTS,
        )
        counts["promotions"] += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                "Seed demonstrativo concluído. Novos registros: "
                f"loja={counts['store']}, "
                f"categorias={counts['categories']}, "
                f"produtos={counts['products']}, "
                f"promoções={counts['promotions']}. "
                "Registros existentes não foram alterados."
            )
        )