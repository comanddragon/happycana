# =============================================================================
# core/apps.py
# =============================================================================
import logging
import re
import uuid

from django.apps import AppConfig

logger = logging.getLogger("core.cache")


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # ready() runs on every process boot (each gunicorn/daphne worker,
        # the dev autoreloader's child process, management commands, etc.),
        # so this must never raise — a Redis hiccup on startup should log a
        # warning, not crash the app.
        self._check_redis_connection()

        from core.timing import patch_json_renderer
        patch_json_renderer()

    def _check_redis_connection(self):
        from django.core.cache import cache

        probe_key = f"startup:redis-check:{uuid.uuid4().hex[:8]}"

        try:
            cache.set(probe_key, "ok", timeout=5)
            ok = cache.get(probe_key) == "ok"
            cache.delete(probe_key)
        except Exception as exc:
            logger.warning(
                "Redis cache is NOT reachable at startup (target=%s): %s",
                self._safe_target(),
                exc,
            )
            return

        if ok:
            logger.info(
                "Redis cache connected successfully (target=%s)",
                self._safe_target(),
            )
        else:
            logger.warning(
                "Redis cache responded but the round-trip check value didn't "
                "match — connection is up but something looks off (target=%s)",
                self._safe_target(),
            )

    @staticmethod
    def _safe_target():
        """Return the configured Redis LOCATION with any credentials masked,
        so the connection string is never written to logs in full."""
        from django.conf import settings

        location = settings.CACHES.get("default", {}).get("LOCATION", "") or "(not set)"
        # Mask "redis://user:password@host:port" -> "redis://***@host:port"
        return re.sub(r"//[^@/]+@", "//***@", location)
