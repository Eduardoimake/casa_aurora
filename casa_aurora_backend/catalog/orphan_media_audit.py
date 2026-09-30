"""Inventário não destrutivo de mídias sem referência no catálogo."""

from dataclasses import dataclass

from .models import Product, Promotion, StoreSettings


MANAGED_DIRECTORIES = (
    "products",
    "store",
    "promotions",
)


@dataclass(frozen=True)
class OrphanMediaIssue:
    """Falha que impede a inspeção completa de um diretório."""

    directory: str
    kind: str
    detail: str


@dataclass(frozen=True)
class OrphanMediaReport:
    """Arquivos encontrados, candidatos sem referência e falhas."""

    scanned_files: int
    candidates: tuple[str, ...]
    issues: tuple[OrphanMediaIssue, ...]

    @property
    def complete(self) -> bool:
        return not self.issues


def _stored_references() -> set[str]:
    """Reúne nomes atualmente associados aos três campos de imagem."""
    references = set()

    for name in Product.objects.exclude(
        main_image=""
    ).values_list("main_image", flat=True):
        if name:
            references.add(name)

    for name in StoreSettings.objects.exclude(
        banner_image=""
    ).values_list("banner_image", flat=True):
        if name:
            references.add(name)

    for name in Promotion.objects.exclude(
        image=""
    ).values_list("image", flat=True):
        if name:
            references.add(name)

    return references


def _media_storage():
    """Obtém o storage associado aos campos gerenciados pelo catálogo."""
    return Product._meta.get_field("main_image").storage


def inspect_orphan_media() -> OrphanMediaReport:
    """Lista arquivos gerenciados e compara com referências do banco."""
    references = _stored_references()
    storage = _media_storage()

    scanned = 0
    candidates = []
    issues = []
    pending = list(MANAGED_DIRECTORIES)

    while pending:
        directory = pending.pop()

        try:
            subdirectories, filenames = storage.listdir(directory)
        except FileNotFoundError:
            # Pasta ainda não criada: não há arquivo para inventariar nela.
            continue
        except NotImplementedError as exc:
            issues.append(
                OrphanMediaIssue(
                    directory=directory,
                    kind="listing_not_supported",
                    detail=type(exc).__name__,
                )
            )
            continue
        except Exception as exc:
            issues.append(
                OrphanMediaIssue(
                    directory=directory,
                    kind="listing_error",
                    detail=type(exc).__name__,
                )
            )
            continue

        for filename in filenames:
            stored_name = f"{directory}/{filename}"
            scanned += 1

            if stored_name not in references:
                candidates.append(stored_name)

        for subdirectory in subdirectories:
            if subdirectory not in {".", ".."}:
                pending.append(f"{directory}/{subdirectory}")

    return OrphanMediaReport(
        scanned_files=scanned,
        candidates=tuple(sorted(candidates)),
        issues=tuple(issues),
    )