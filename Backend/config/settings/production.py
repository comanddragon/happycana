from urllib.parse import urlparse, parse_qsl

from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

# ---------------------------------------------------------------------------
# Database — Postgres with connection pooling
# ---------------------------------------------------------------------------
tmpPostgres = urlparse(os.environ["DATABASE_URL"])

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     tmpPostgres.path.lstrip("/"),
        "USER":     tmpPostgres.username,
        "PASSWORD": tmpPostgres.password,
        "HOST":     tmpPostgres.hostname,
        "PORT":     tmpPostgres.port or 5432,
        "CONN_MAX_AGE": 60,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "connect_timeout": 10,
            "isolation_level": 2,  # psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
            **dict(parse_qsl(tmpPostgres.query)),
        },
    }
}

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------
def _env_bool(name, default):
    return os.environ.get(name, str(default)).lower() in ("true", "1", "yes")

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
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"].split(",")
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

AWS_ACCESS_KEY_ID     = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION_NAME    = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN  = os.environ.get("AWS_CLOUDFRONT_DOMAIN", "")
AWS_DEFAULT_ACL       = "private"
AWS_S3_FILE_OVERWRITE = False
# The "static" bucket is a Neon Object Storage bucket with public_read
# access, so reads don't need auth. Without this, django-storages defaults
# to signing every .url() call (AWS_QUERYSTRING_AUTH defaults to True),
# which is where the categories endpoint's ~1s/request overhead comes from.
AWS_QUERYSTRING_AUTH  = False

# ---------------------------------------------------------------------------
# Sentry — error tracking
# ---------------------------------------------------------------------------
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[DjangoIntegration()],
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