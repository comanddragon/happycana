from .base import *  # noqa
import sentry_sdk
from urllib.parse import parse_qsl, urlparse
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

ALLOWED_HOSTS = config["ALLOWED_HOSTS"].split(",")

# ---------------------------------------------------------------------------
# Database — Postgres with connection pooling
# ---------------------------------------------------------------------------
tmp_postgres = urlparse(config["DATABASE_URL"])

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     tmp_postgres.path.lstrip("/"),
        "USER":     tmp_postgres.username,
        "PASSWORD": tmp_postgres.password,
        "HOST":     tmp_postgres.hostname,
        "PORT":     tmp_postgres.port or 5432,
        "CONN_MAX_AGE": 60,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "connect_timeout": 10,
            "isolation_level": 2,  # psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
            **dict(parse_qsl(tmp_postgres.query)),
        },
    }
}

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------
def _env_bool(name, default):
    return config.get(name, str(default)).lower() in ("true", "1", "yes")

SECURE_SSL_REDIRECT            = _env_bool("SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SESSION_COOKIE_SECURE          = _env_bool("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE             = _env_bool("CSRF_COOKIE_SECURE", True)
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = "DENY"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config["CORS_ALLOWED_ORIGINS"].split(",")
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Static files — WhiteNoise serves them efficiently
# ---------------------------------------------------------------------------
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    # Media files — S3
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

AWS_ACCESS_KEY_ID     = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = config["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION = config.get("AWS_S3_REGION", "us-east-1")
AWS_S3_CUSTOM_DOMAIN  = config.get("AWS_CLOUDFRONT_DOMAIN", "")
AWS_DEFAULT_ACL       = "private"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH  = False

# ---------------------------------------------------------------------------
# Sentry — error tracking
# ---------------------------------------------------------------------------
sentry_sdk.init(
    dsn=config["SENTRY_DSN"],
    integrations=[DjangoIntegration(),CeleryIntegration(),RedisIntegration()],
    traces_sample_rate=0.2,
    send_default_pii=False,
)

# ---------------------------------------------------------------------------
# Logging — structured JSON to stdout (picked up by your log aggregator)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level":    "INFO",
    },
    "loggers": {
        "django": {
            "handlers":  ["console"],
            "level":     "WARNING",
            "propagate": False,
        },
        "core.timing": {
            "handlers":  ["console"],
            "level":     "INFO",
            "propagate": False,
        },
    },
}
