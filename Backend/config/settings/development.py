from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

STORE_LOGO_URL = config("STORE_LOGO_URL", "")

# Postgres for local dev too — connection details come from env vars below
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     config("DB_NAME",     ""),
        "USER":     config("DB_USER",     ""),
        "PASSWORD": config("DB_PASSWORD", ""),
        "HOST":     config("DB_HOST",     ""),
        "PORT":     config("DB_PORT",     ""),
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
            "formatter": "verbose",
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
        "core.cache": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
        "core.timing": {
            "handlers": ["console"],
            "level":    "INFO",
            "propagate": False,
        },
    },
}
