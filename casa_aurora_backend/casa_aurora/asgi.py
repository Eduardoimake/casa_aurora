"""Ponto de entrada ASGI do projeto Casa Aurora."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "casa_aurora.settings",
)

application = get_asgi_application()