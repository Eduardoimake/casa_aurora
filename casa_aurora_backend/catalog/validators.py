"""Validação de dados e geração de caminhos para uploads do catálogo."""

import re
import uuid
import warnings
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_FORMATS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "WEBP": {".webp"},
}

CANONICAL_IMAGE_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


def validate_whatsapp_number(value):
    """Aceita um número internacional sem sinal de mais ou separadores."""
    if not isinstance(value, str) or not re.fullmatch(
        r"[1-9][0-9]{9,14}",
        value,
    ):
        raise ValidationError(
            "Informe o WhatsApp em formato internacional, somente com "
            "10 a 15 dígitos, sem +, espaços ou pontuação.",
            code="invalid_whatsapp_number",
        )


def validate_uploaded_image(value):
    """Verifica tamanho, extensão, formato real e decodificação da imagem."""
    if not value:
        return

    maximum_bytes = settings.MAX_IMAGE_UPLOAD_MB * 1024 * 1024

    try:
        file_size = value.size
    except (AttributeError, OSError, ValueError, TypeError) as exc:
        raise ValidationError(
            "Não foi possível determinar o tamanho da imagem.",
            code="invalid_image_size",
        ) from exc

    if file_size > maximum_bytes:
        raise ValidationError(
            f"A imagem deve ter no máximo {settings.MAX_IMAGE_UPLOAD_MB} MB.",
            code="image_too_large",
        )

    original_name = getattr(value, "name", "") or ""
    extension = Path(original_name).suffix.lower()

    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValidationError(
            "Envie uma imagem JPEG, PNG ou WebP.",
            code="unsupported_image_extension",
        )

    try:
        original_position = value.tell()
    except (AttributeError, OSError, ValueError):
        original_position = None

    try:
        value.seek(0)

        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(value) as image:
                detected_format = image.format
                image.verify()

            value.seek(0)

            with Image.open(value) as image:
                image.load()

        if detected_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError(
                "Envie uma imagem JPEG, PNG ou WebP.",
                code="unsupported_image_format",
            )

        if extension not in ALLOWED_IMAGE_FORMATS[detected_format]:
            raise ValidationError(
                "A extensão do arquivo não corresponde ao formato da imagem.",
                code="image_extension_mismatch",
            )

    except ValidationError:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        SyntaxError,
        ValueError,
    ) as exc:
        raise ValidationError(
            "O arquivo enviado não é uma imagem válida ou está corrompido.",
            code="invalid_image",
        ) from exc
    finally:
        try:
            value.seek(
                original_position if original_position is not None else 0
            )
        except (AttributeError, OSError, ValueError):
            pass


def _image_upload_path(directory, filename):
    """Cria um caminho independente dos diretórios enviados pelo cliente."""
    extension = Path(filename or "").suffix.lower()

    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        extension = ".jpg"

    return f"{directory}/{uuid.uuid4().hex}{extension}"


def product_image_upload_to(instance, filename):
    """Define o caminho de armazenamento da imagem de um produto."""
    return _image_upload_path("products", filename)


def store_banner_upload_to(instance, filename):
    """Define o caminho de armazenamento do banner da loja."""
    return _image_upload_path("store", filename)


def promotion_image_upload_to(instance, filename):
    """Define o caminho de armazenamento da imagem de uma promoção."""
    return _image_upload_path("promotions", filename)