"""Verifica se a demonstração pública possui os dados e rotas mínimos."""

from django.core.management.base import BaseCommand, CommandError
from django.test import Client

from catalog.prototype_readiness import evaluate_prototype_readiness


client = Client(SERVER_NAME="localhost")


class Command(BaseCommand):
    help = (
        "Verifica dados mínimos e respostas da API pública "
        "sem modificar o catálogo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Retorna erro caso alguma pendência seja encontrada.",
        )

    def handle(self, *args, **options):
        report = evaluate_prototype_readiness()

        self.stdout.write(
            "Verificação do protótipo Casa Aurora:"
        )
        self.stdout.write(
            f"- Configurações da loja: {report.store_count}"
        )
        self.stdout.write(
            "- Categorias ativas: "
            f"{report.active_categories_count}"
        )
        self.stdout.write(
            "- Produtos públicos: "
            f"{report.public_products_count}"
        )
        self.stdout.write(
            "- Promoções marcadas como ativas: "
            f"{report.active_promotions_count}"
        )

        if report.ready:
            self.stdout.write(
                self.style.SUCCESS(
                    "Pré-condições verificadas sem pendências."
                )
            )
            return

        self.stdout.write("")
        self.stdout.write(
            f"Pendências encontradas: {len(report.issues)}"
        )

        for issue in report.issues:
            self.stdout.write(
                self.style.WARNING(
                    f"- [{issue.code}] {issue.message}"
                )
            )

        if options["strict"]:
            raise CommandError(
                "O protótipo apresenta pendências. "
                "Corrija-as antes de considerar a demonstração pronta."
            )