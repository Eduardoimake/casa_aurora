import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Cria ou atualiza o administrador inicial a partir de variáveis de ambiente."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-password-reset",
            action="store_true",
            help="Redefine a senha do administrador existente.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "").strip()
        email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip()
        password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")

        missing = [
            name
            for name, value in {
                "BOOTSTRAP_ADMIN_USERNAME": username,
                "BOOTSTRAP_ADMIN_PASSWORD": password,
            }.items()
            if not value
        ]

        if missing:
            raise CommandError(
                "Variáveis obrigatórias ausentes: " + ", ".join(missing)
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed_fields = []

        if email and user.email != email:
            user.email = email
            changed_fields.append("email")

        if not user.is_active:
            user.is_active = True
            changed_fields.append("is_active")

        if not user.is_staff:
            user.is_staff = True
            changed_fields.append("is_staff")

        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append("is_superuser")

        if created or options["force_password_reset"]:
            user.set_password(password)
            changed_fields.append("password")

        if changed_fields:
            user.save(update_fields=list(set(changed_fields)))

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrador inicial criado: {username}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrador verificado: {username}"
                )
            )