# =============================================================================
# config/settings/development.py
# =============================================================================
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# BACKEND_URL override — set this to your ngrok tunnel (or any publicly
# reachable URL pointing at this dev server) so outgoing emails show a real,
# loadable logo instead of an unreachable http://localhost:8000 one. Falls
# back to the base.py default when unset, so this is a no-op until you set it.
# e.g. BACKEND_URL=https://abcd1234.ngrok-free.app python manage.py runserver
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# BACKEND_URL override — set this to your ngrok tunnel (or any publicly
# reachable URL pointing at this dev server) so outgoing emails show a real,
# loadable logo instead of an unreachable http://localhost:8000 one. Falls
# back to the base.py value if unset, blank, or hostless (e.g. "http://" from
# a script that interpolated an empty var), so this is a no-op until you set
# it properly. e.g. BACKEND_URL=https://abcd1234.ngrok-free.app manage.py runserver
# ---------------------------------------------------------------------------
_backend_url_env = os.environ.get("BACKEND_URL", "")
if urlparse(_backend_url_env).netloc:
    BACKEND_URL = _backend_url_env
# STORE_LOGO_URL was already built from the old BACKEND_URL in base.py, so it
# needs recomputing here — unless the user explicitly set STORE_LOGO_URL
# themselves, which should win either way.
STORE_LOGO_URL = os.environ.get(
    "STORE_LOGO_URL", f"{BACKEND_URL}{STATIC_URL}branding/logo-lockup-light-bg.png"
)

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