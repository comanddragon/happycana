from django.apps import AppConfig


class StorefrontsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.storefronts"

    def ready(self):
        from . import signals  # noqa: F401
