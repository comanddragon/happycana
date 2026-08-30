from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

STORE_LOGO_URL = os.environ.get("STORE_LOGO_URL", "")

# SQLite for quick local dev — swap to Postgres if you need relational features
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     os.environ.get("DB_NAME",     ""),
        "USER":     os.environ.get("DB_USER",     ""),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST":     os.environ.get("DB_HOST",     ""),
        "PORT":     os.environ.get("DB_PORT",     ""),
    }
}

# CORS — allow all origins locally
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (install separately)
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS   = ["127.0.0.1"]

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
        "services.email": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
    },
}