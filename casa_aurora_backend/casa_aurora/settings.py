"""Configurações do backend Casa Aurora."""

import os
from pathlib import Path
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR.parent / "casa_aurora_frontend" / "dist"


def load_dotenv_file(path: Path) -> None:
    """Carrega pares CHAVE=VALOR locais sem sobrescrever o ambiente."""
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export "):].strip()

        key, separator, value = line.partition("=")

        if not separator:
            continue

        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


load_dotenv_file(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ImproperlyConfigured(
        f"{name} deve ser true/false, 1/0, yes/no ou on/off."
    )


def env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


def env_positive_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))

    try:
        number = int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"{name} deve ser um número inteiro positivo."
        ) from exc

    if number <= 0:
        raise ImproperlyConfigured(
            f"{name} deve ser um número inteiro positivo."
        )

    return number


def env_nonnegative_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default))

    try:
        number = int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"{name} deve ser um número inteiro não negativo."
        ) from exc

    if number < 0:
        raise ImproperlyConfigured(
            f"{name} deve ser um número inteiro não negativo."
        )

    return number


DEBUG = env_bool("DJANGO_DEBUG", False)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY no ambiente ou no .env local."
    )

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Defina DJANGO_ALLOWED_HOSTS quando DJANGO_DEBUG=false."
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "casa_aurora.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "casa_aurora.wsgi.application"
ASGI_APPLICATION = "casa_aurora.asgi.application"


DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE == "sqlite":
    sqlite_path = Path(
        os.getenv("SQLITE_PATH", "db.sqlite3").strip() or "db.sqlite3"
    )

    if not sqlite_path.is_absolute():
        sqlite_path = BASE_DIR / sqlite_path

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_path,
        }
    }
elif DB_ENGINE == "postgresql":
    required_db_settings = {
        "DB_NAME": os.getenv("DB_NAME", "").strip(),
        "DB_USER": os.getenv("DB_USER", "").strip(),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "DB_HOST": os.getenv("DB_HOST", "").strip(),
        "DB_PORT": os.getenv("DB_PORT", "").strip(),
    }

    missing_db_settings = [
        name
        for name, value in required_db_settings.items()
        if not value
    ]

    if missing_db_settings:
        raise ImproperlyConfigured(
            "Configure as variáveis de PostgreSQL: "
            + ", ".join(missing_db_settings)
        )

    db_settings = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required_db_settings["DB_NAME"],
        "USER": required_db_settings["DB_USER"],
        "PASSWORD": required_db_settings["DB_PASSWORD"],
        "HOST": required_db_settings["DB_HOST"],
        "PORT": required_db_settings["DB_PORT"],
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }

    if not DEBUG:
        db_settings["OPTIONS"] = {"sslmode": "require"}

    DATABASES = {"default": db_settings}
else:
    raise ImproperlyConfigured(
        "DB_ENGINE deve ser sqlite ou postgresql."
    )


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if FRONTEND_DIST.is_dir():
    STATICFILES_DIRS = [FRONTEND_DIST]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

R2_ENABLED = env_bool("R2_ENABLED", False)

if R2_ENABLED:
    required_r2_settings = {
        "R2_ACCESS_KEY_ID": os.getenv("R2_ACCESS_KEY_ID", "").strip(),
        "R2_SECRET_ACCESS_KEY": os.getenv(
            "R2_SECRET_ACCESS_KEY", ""
        ).strip(),
        "R2_BUCKET_NAME": os.getenv("R2_BUCKET_NAME", "").strip(),
        "R2_ENDPOINT_URL": os.getenv("R2_ENDPOINT_URL", "").strip(),
        "R2_PUBLIC_URL": os.getenv("R2_PUBLIC_URL", "").strip(),
    }

    missing_r2_settings = [
        name
        for name, value in required_r2_settings.items()
        if not value
    ]

    if missing_r2_settings:
        raise ImproperlyConfigured(
            "Configure as variáveis do R2: "
            + ", ".join(missing_r2_settings)
        )

    endpoint = urlparse(required_r2_settings["R2_ENDPOINT_URL"])
    public_url = urlparse(required_r2_settings["R2_PUBLIC_URL"])

    if endpoint.scheme != "https" or not endpoint.netloc:
        raise ImproperlyConfigured(
            "R2_ENDPOINT_URL deve ser uma URL HTTPS válida."
        )

    if public_url.scheme != "https" or not public_url.netloc:
        raise ImproperlyConfigured(
            "R2_PUBLIC_URL deve ser uma URL HTTPS válida."
        )

    if public_url.path.rstrip("/") or public_url.query or public_url.fragment:
        raise ImproperlyConfigured(
            "R2_PUBLIC_URL deve conter apenas a origem HTTPS."
        )

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": required_r2_settings["R2_ACCESS_KEY_ID"],
            "secret_key": required_r2_settings["R2_SECRET_ACCESS_KEY"],
            "bucket_name": required_r2_settings["R2_BUCKET_NAME"],
            "endpoint_url": required_r2_settings["R2_ENDPOINT_URL"],
            "region_name": "auto",
            "custom_domain": public_url.netloc,
            "url_protocol": "https:",
            "querystring_auth": False,
            "file_overwrite": False,
            "default_acl": None,
        },
    }


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
}

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/api/v1/.*$"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    not DEBUG,
)

SECURE_HSTS_SECONDS = env_nonnegative_int(
    "DJANGO_SECURE_HSTS_SECONDS",
    0,
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    False,
)

SECURE_HSTS_PRELOAD = env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    False,
)

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if env_bool("DJANGO_TRUST_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


MAX_IMAGE_UPLOAD_MB = env_positive_int(
    "MAX_IMAGE_UPLOAD_MB",
    5,
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    MAX_IMAGE_UPLOAD_MB * 1024 * 1024 + 1024 * 1024
)

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    MAX_IMAGE_UPLOAD_MB * 1024 * 1024
)