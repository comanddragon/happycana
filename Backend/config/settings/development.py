
# =============================================================================
# config/settings/development.py
# =============================================================================
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# SQLite for quick local dev — swap to Postgres if you need relational features
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     os.environ.get("DB_NAME",     "ecommerce"),
        "USER":     os.environ.get("DB_USER",     "silkkeith"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "85213"),
        "HOST":     os.environ.get("DB_HOST",     "localhost"),
        "PORT":     os.environ.get("DB_PORT",     "5432"),
    }
}

# CORS — allow all origins locally
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (install separately)
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS   = ["127.0.0.1"]

# Email printed to console instead of sent
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging — print SQL queries to console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} — {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
        "realtime": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
        "daphne": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
    },
}