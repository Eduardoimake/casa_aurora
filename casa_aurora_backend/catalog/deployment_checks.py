"""Verificações estáticas de implantação específicas da Casa Aurora."""

from django.conf import settings
from django.core.checks import Warning, register


@register(deploy=True)
def check_casa_aurora_deployment(app_configs, **kwargs):
    """Relata configurações que exigem revisão antes da publicação."""
    issues = []

    if settings.DEBUG:
        issues.append(
            Warning(
                "DJANGO_DEBUG deve estar desativado na implantação.",
                id="catalog.W001",
            )
        )

    if settings.SECRET_KEY == (
        "django-insecure-local-only-change-before-deployment"
    ):
        issues.append(
            Warning(
                "A chave local de desenvolvimento não deve ser "
                "utilizada na implantação.",
                id="catalog.W002",
            )
        )

    if not settings.SESSION_COOKIE_SECURE:
        issues.append(
            Warning(
                "SESSION_COOKIE_SECURE deve estar ativado em HTTPS.",
                id="catalog.W003",
            )
        )

    if not settings.CSRF_COOKIE_SECURE:
        issues.append(
            Warning(
                "CSRF_COOKIE_SECURE deve estar ativado em HTTPS.",
                id="catalog.W004",
            )
        )

    if not settings.SESSION_COOKIE_HTTPONLY:
        issues.append(
            Warning(
                "O cookie de sessão deve permanecer HttpOnly.",
                id="catalog.W005",
            )
        )

    if not settings.CORS_ALLOW_CREDENTIALS:
        issues.append(
            Warning(
                "Revise CORS_ALLOW_CREDENTIALS: a estratégia de "
                "desenvolvimento entre portas usa cookies de sessão.",
                id="catalog.W006",
            )
        )

    if getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False):
        issues.append(
            Warning(
                "Não libere CORS indiscriminadamente para todas "
                "as origens.",
                id="catalog.W007",
            )
        )

    required_middleware = (
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    )
    missing_middleware = [
        name
        for name in required_middleware
        if name not in settings.MIDDLEWARE
    ]

    if missing_middleware:
        issues.append(
            Warning(
                "Middlewares essenciais de sessão, autenticação "
                "ou CSRF estão ausentes: "
                + ", ".join(missing_middleware),
                id="catalog.W008",
            )
        )

    if settings.SECURE_PROXY_SSL_HEADER is not None:
        issues.append(
            Warning(
                "SECURE_PROXY_SSL_HEADER está configurado: confirme "
                "fora do Django que somente o proxy confiável define "
                "o cabeçalho correspondente.",
                id="catalog.W009",
            )
        )

    return issues