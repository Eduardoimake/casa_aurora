"""Ponto de entrada WSGI do projeto Casa Aurora."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "casa_aurora.settings",
)

application = get_wsgi_application()