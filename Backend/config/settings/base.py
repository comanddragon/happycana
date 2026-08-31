# =============================================================================
# config/settings/base.py
# =============================================================================
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

INSTALLED_APPS = [
    # Django core
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "channels",
    "drf_spectacular",          # OpenAPI schema generation

    # Local apps
    "apps.users",
    "apps.catalog",
    "apps.inventory",
    "apps.orders",
    "apps.payments",
    "apps.shipping",
    "apps.promotions",
    "apps.notifications",
    "apps.analytics",
    "apps.chat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestIDMiddleware",         # attaches X-Request-ID to every request
]

ROOT_URLCONF    = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "users.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# ---------------------------------------------------------------------------
# Authentication — Simple JWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# Channels (WebSockets)
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("REDIS_HOST", "127.0.0.1"), 6379)],
        },
    },
}

# ---------------------------------------------------------------------------
# Django Tasks (replaces Celery)
# ---------------------------------------------------------------------------
TASKS = {
    "default": {
        # There's no separate worker process in this project, so run tasks
        # synchronously in-process rather than queuing them to a backend
        # that's never drained. Swap for a real queuing backend once a
        # worker exists.
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", ""),
    }
}

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# OpenAPI
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE":       "E-Commerce API",
    "DESCRIPTION": "High-performance Django e-commerce backend",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# Email (base — overridden per environment)
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = os.environ.get(
    "RESEND_FROM_EMAIL", os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")
)

# Resend — all transactional email goes through services/email.py.
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
ADMIN_NOTIFICATION_EMAIL = os.environ.get("ADMIN_NOTIFICATION_EMAIL", "")

# Branding vars injected into every templates/emails/*.html render.
STORE_NAME    = os.environ.get("STORE_NAME", "Our Store")
FRONTEND_URL  = os.environ.get("FRONTEND_URL", "https://example.com")

BACKEND_URL = os.environ.get("BACKEND_URL", "")
STORE_LOGO_URL= os.environ.get("STORE_LOGO_URL", "")
SUPPORT_EMAIL = os.environ.get("SUPPORT_EMAIL", "support@example.com")
STORE_ADDRESS = os.environ.get("STORE_ADDRESS", "")