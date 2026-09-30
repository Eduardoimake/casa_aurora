"""Diagnóstico não destrutivo da demonstração pública da Casa Aurora."""

from dataclasses import dataclass

from django.test import Client

from catalog.models import Category, Product, Promotion, StoreSettings


DEMO_WHATSAPP_NUMBER = "999999999999999"


@dataclass(frozen=True)
class ReadinessIssue:
    """Pendência identificada durante a verificação."""

    code: str
    message: str


@dataclass(frozen=True)
class ReadinessReport:
    """Contagens e pendências da demonstração."""

    store_count: int
    active_categories_count: int
    public_products_count: int
    active_promotions_count: int
    issues: tuple[ReadinessIssue, ...]

    @property
    def ready(self) -> bool:
        return not self.issues


def _public_endpoint_issue(client, *, path, code, expected_type):
    """Verifica status e tipo JSON básico de um endpoint público."""
    try:
        response = client.get(
            path,
            HTTP_ACCEPT="application/json",
        )
    except Exception as exc:
        return ReadinessIssue(
            code=code,
            message=(
                f"{path} gerou {type(exc).__name__}; "
                "consulte o log da aplicação para localizar a causa."
            ),
        )

    if response.status_code != 200:
        return ReadinessIssue(
            code=code,
            message=(
                f"{path} retornou HTTP {response.status_code}, "
                "esperado 200."
            ),
        )

    try:
        payload = response.json()
    except ValueError:
        return ReadinessIssue(
            code=code,
            message=f"{path} não retornou JSON válido.",
        )

    if not isinstance(payload, expected_type):
        return ReadinessIssue(
            code=code,
            message=(
                f"{path} retornou um formato JSON inesperado."
            ),
        )

    return None


def evaluate_prototype_readiness(*, client=None) -> ReadinessReport:
    """Avalia dados mínimos e leituras públicas sem alterar o catálogo."""
    # O .env.example local autoriza localhost, não testserver.
    client = client or Client(HTTP_HOST="localhost")
    issues = []

    store_count = StoreSettings.objects.count()
    active_categories_count = Category.objects.filter(
        is_active=True
    ).count()
    public_products_count = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        category__is_active=True,
    ).count()
    active_promotions_count = Promotion.objects.filter(
        is_active=True
    ).count()

    if store_count != 1:
        issues.append(
            ReadinessIssue(
                code="store_count",
                message=(
                    "É necessária exatamente uma configuração da loja; "
                    f"encontradas {store_count}."
                ),
            )
        )
    else:
        store = StoreSettings.objects.first()

        if store.pk != 1:
            issues.append(
                ReadinessIssue(
                    code="store_pk",
                    message="A configuração da loja deve usar o ID 1.",
                )
            )

        if store.whatsapp_number == DEMO_WHATSAPP_NUMBER:
            issues.append(
                ReadinessIssue(
                    code="demo_whatsapp",
                    message=(
                        "O WhatsApp ainda é o número fictício do seed. "
                        "Configure um contato autorizado antes de publicar."
                    ),
                )
            )

        if not store.banner_text.strip():
            issues.append(
                ReadinessIssue(
                    code="banner_text",
                    message="O texto do banner está vazio.",
                )
            )

    if active_categories_count == 0:
        issues.append(
            ReadinessIssue(
                code="active_categories",
                message="Não há categorias ativas para o visitante.",
            )
        )

    if public_products_count == 0:
        issues.append(
            ReadinessIssue(
                code="public_products",
                message="Não há produtos visíveis na API pública.",
            )
        )

    checks = (
        (
            "/api/v1/public/store/",
            "public_store_http",
            dict,
        ),
        (
            "/api/v1/public/categories/",
            "public_categories_http",
            list,
        ),
        (
            "/api/v1/public/products/",
            "public_products_http",
            dict,
        ),
        (
            "/api/v1/public/promotions/",
            "public_promotions_http",
            list,
        ),
    )

    for path, code, expected_type in checks:
        issue = _public_endpoint_issue(
            client,
            path=path,
            code=code,
            expected_type=expected_type,
        )
        if issue is not None:
            issues.append(issue)

    return ReadinessReport(
        store_count=store_count,
        active_categories_count=active_categories_count,
        public_products_count=public_products_count,
        active_promotions_count=active_promotions_count,
        issues=tuple(issues),
    )