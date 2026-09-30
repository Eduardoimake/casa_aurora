"""Relata possíveis mídias órfãs sem excluir arquivos ou alterar o banco."""

from django.core.management.base import BaseCommand, CommandError

from catalog.orphan_media_audit import inspect_orphan_media


class Command(BaseCommand):
    help = (
        "Lista arquivos nas pastas de mídia do catálogo que não têm "
        "referência atual nos modelos. Não exclui arquivos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help=(
                "Retorna erro se houver candidatos ou se a inspeção "
                "de algum diretório estiver incompleta."
            ),
        )

    def handle(self, *args, **options):
        report = inspect_orphan_media()

        self.stdout.write("Inventário de mídias sem referência:")
        self.stdout.write(
            f"- Arquivos inspecionados: {report.scanned_files}"
        )
        self.stdout.write(
            f"- Candidatos sem referência: {len(report.candidates)}"
        )
        self.stdout.write(
            f"- Falhas de inspeção: {len(report.issues)}"
        )

        for name in report.candidates:
            self.stdout.write(
                self.style.WARNING(f"- CANDIDATO {name}")
            )

        for issue in report.issues:
            self.stdout.write(
                self.style.ERROR(
                    f"- ERRO {issue.directory}: "
                    f"{issue.kind} ({issue.detail})"
                )
            )

        if options["strict"] and (
            report.candidates or report.issues
        ):
            raise CommandError(
                "Foram encontrados candidatos sem referência ou "
                "o inventário não pôde ser concluído."
            )

        if not report.candidates and not report.issues:
            self.stdout.write(
                self.style.SUCCESS(
                    "Inventário concluído sem candidatos ou falhas."
                )
            )