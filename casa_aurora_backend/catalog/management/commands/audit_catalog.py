"""Audita a consistência do catálogo demonstrativo sem alterar dados."""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from catalog.models import Category, Product, Promotion, StoreSettings


DEMO_WHATSAPP_NUMBER = "999999999999999"


class Command(BaseCommand):
    help = (
        "Audita dados da loja, visibilidade do catálogo e conteúdo "
        "demonstrativo sem modificar registros."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Retorna erro caso a auditoria encontre avisos.",
        )

    def handle(self, *args, **options):
        warnings = []
        now = timezone.now()

        stores = StoreSettings.objects.all()
        store_count = stores.count()

        if store_count != 1:
            warnings.append(
                "Configuração da loja: esperado exatamente um registro; "
                f"encontrados {store_count}."
            )
        else:
            store = stores.first()

            if store.pk != 1:
                warnings.append(
                    "A configuração da loja não usa o identificador 1."
                )

            if store.whatsapp_number == DEMO_WHATSAPP_NUMBER:
                warnings.append(
                    "O WhatsApp da loja ainda é o número fictício do seed. "
                    "Substitua-o por um número autorizado antes de publicar."
                )

        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()

        if total_categories == 0:
            warnings.append("Não há categorias cadastradas.")
        elif active_categories == 0:
            warnings.append(
                "Não há categorias ativas para o site público."
            )

        total_products = Product.objects.count()
        public_products = Product.objects.filter(
            status=Product.Status.PUBLISHED,
            category__is_active=True,
        ).count()

        if total_products == 0:
            warnings.append("Não há produtos cadastrados.")
        elif public_products == 0:
            warnings.append(
                "Não há produtos visíveis no site público."
            )

        published_in_inactive_categories = Product.objects.filter(
            status=Product.Status.PUBLISHED,
            category__is_active=False,
        ).count()

        if published_in_inactive_categories:
            warnings.append(
                f"{published_in_inactive_categories} produto(s) marcado(s) "
                "como publicado(s) pertence(m) a categoria(s) inativa(s) "
                "e não aparecerá(ão) publicamente."
            )

        current_active_promotions = (
            Promotion.objects.filter(is_active=True)
            .filter(
                Q(starts_at__isnull=True)
                | Q(starts_at__lte=now)
            )
            .filter(
                Q(ends_at__isnull=True)
                | Q(ends_at__gte=now)
            )
        )

        invisible_linked_promotions = (
            current_active_promotions.filter(
                product__isnull=False,
            )
            .exclude(
                product__status=Product.Status.PUBLISHED,
                product__category__is_active=True,
            )
            .count()
        )

        if invisible_linked_promotions:
            warnings.append(
                f"{invisible_linked_promotions} promoção(ões) ativa(s) "
                "e dentro do período está(ão) vinculada(s) a produto(s) "
                "não visível(is) publicamente."
            )

        self.stdout.write("Auditoria do catálogo:")
        self.stdout.write(
            f"- Configurações da loja: {store_count}"
        )
        self.stdout.write(
            f"- Categorias: {total_categories}; ativas: {active_categories}"
        )
        self.stdout.write(
            f"- Produtos: {total_products}; públicos: {public_products}"
        )
        self.stdout.write(
            f"- Promoções: {Promotion.objects.count()}"
        )

        if warnings:
            self.stdout.write("")
            self.stdout.write(
                f"Avisos encontrados: {len(warnings)}"
            )

            for warning in warnings:
                self.stdout.write(
                    self.style.WARNING(f"- {warning}")
                )

            if options["strict"]:
                raise CommandError(
                    "A auditoria encontrou avisos. "
                    "Corrija-os ou execute sem --strict para apenas "
                    "inspecionar."
                )

            return

        self.stdout.write(
            self.style.SUCCESS(
                "Auditoria concluída sem avisos."
            )
        )