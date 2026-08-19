# =============================================================================
# config/settings/test.py
# =============================================================================
from .base import *  # noqa

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":   os.environ.get("TEST_DB_NAME", "ecommerce_test"),
        "USER":   os.environ.get("DB_USER",      "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD","postgres"),
        "HOST":   os.environ.get("DB_HOST",      "localhost"),
        "PORT":   "5432",
    }
}

# Use in-memory channel layer — no Redis needed for tests
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Faster password hashing in tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


