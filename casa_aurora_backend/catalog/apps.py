"""Configuração da aplicação de catálogo."""

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"
    verbose_name = "Catálogo Casa Aurora"

    def ready(self):
        """Registra verificações específicas da implantação."""
        from . import deployment_checks  # noqa: F401