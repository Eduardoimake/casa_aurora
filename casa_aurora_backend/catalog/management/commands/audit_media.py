"""Relata referências de imagens ausentes sem alterar o catálogo."""

from django.core.management.base import BaseCommand, CommandError

from catalog.media_audit import inspect_media_references


class Command(BaseCommand):
    help = (
        "Verifica se imagens referenciadas pelos modelos existem "
        "no armazenamento, sem modificar dados ou arquivos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Retorna erro se houver referência ausente ou falha de inspeção.",
        )

    def handle(self, *args, **options):
        report = inspect_media_references()

        self.stdout.write("Auditoria de referências de mídia:")
        self.stdout.write(
            f"- Referências verificadas: {report.checked}"
        )
        self.stdout.write(
            f"- Arquivos ausentes: {len(report.missing)}"
        )
        self.stdout.write(
            f"- Erros de inspeção: {len(report.errors)}"
        )

        for issue in report.missing:
            self.stdout.write(
                self.style.WARNING(
                    f"- AUSENTE {issue.model} #{issue.object_id} "
                    f"{issue.field}: {issue.name}"
                )
            )

        for issue in report.errors:
            self.stdout.write(
                self.style.ERROR(
                    f"- ERRO {issue.model} #{issue.object_id} "
                    f"{issue.field}: {issue.name} "
                    f"({issue.reason})"
                )
            )

        if options["strict"] and not report.ok:
            raise CommandError(
                "A auditoria de mídia encontrou referências ausentes "
                "ou erros de inspeção."
            )

        if report.ok:
            self.stdout.write(
                self.style.SUCCESS(
                    "Auditoria de referências concluída sem pendências."
                )
            )