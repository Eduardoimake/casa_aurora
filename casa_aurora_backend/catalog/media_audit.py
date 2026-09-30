"""Inspeção não destrutiva de imagens referenciadas pelo catálogo."""

from dataclasses import dataclass

from .models import Product, Promotion, StoreSettings


@dataclass(frozen=True)
class MediaIssue:
    """Referência de mídia ausente ou impossível de verificar."""

    model: str
    object_id: int
    field: str
    name: str
    reason: str


@dataclass(frozen=True)
class MediaAuditReport:
    """Resultado agregado da verificação das referências de imagens."""

    checked: int
    missing: tuple[MediaIssue, ...]
    errors: tuple[MediaIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.missing and not self.errors


IMAGE_FIELDS = (
    (Product, "product", "main_image"),
    (StoreSettings, "store", "banner_image"),
    (Promotion, "promotion", "image"),
)


def inspect_media_references() -> MediaAuditReport:
    """Consulta referências no banco e sua existência no storage."""
    checked = 0
    missing = []
    errors = []

    for model, label, field_name in IMAGE_FIELDS:
        for instance in model.objects.all().iterator():
            image = getattr(instance, field_name)
            name = image.name

            if not name:
                continue

            checked += 1

            try:
                exists = image.storage.exists(name)
            except Exception as exc:
                errors.append(
                    MediaIssue(
                        model=label,
                        object_id=instance.pk,
                        field=field_name,
                        name=name,
                        reason=type(exc).__name__,
                    )
                )
                continue

            if not exists:
                missing.append(
                    MediaIssue(
                        model=label,
                        object_id=instance.pk,
                        field=field_name,
                        name=name,
                        reason="not_found",
                    )
                )

    return MediaAuditReport(
        checked=checked,
        missing=tuple(missing),
        errors=tuple(errors),
    )