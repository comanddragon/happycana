import time
from contextvars import ContextVar

_serialization_ms: ContextVar[float] = ContextVar("_serialization_ms", default=0.0)


def reset_serialization_timer() -> None:
    _serialization_ms.set(0.0)


def add_serialization_time(elapsed_ms: float) -> None:
    _serialization_ms.set(_serialization_ms.get() + elapsed_ms)


def get_serialization_time_ms() -> float:
    return _serialization_ms.get()


def patch_json_renderer() -> None:
    """
    Wraps DRF's JSONRenderer.render (the step that turns response.data into
    JSON bytes) so its time is tracked as "serialization time" per request.
    Idempotent — safe to call from AppConfig.ready() on every process boot.
    """
    from rest_framework.renderers import JSONRenderer

    if getattr(JSONRenderer, "_timing_patched", False):
        return

    original_render = JSONRenderer.render

    def timed_render(self, *args, **kwargs):
        start = time.perf_counter()
        result = original_render(self, *args, **kwargs)
        add_serialization_time((time.perf_counter() - start) * 1000)
        return result

    JSONRenderer.render = timed_render
    JSONRenderer._timing_patched = True
