import logging
import time
import uuid

from django.db import connection

logger = logging.getLogger("core.timing")

SLOW_REQUEST_THRESHOLD_MS = 500


class RequestIDMiddleware:
    """Attaches a unique X-Request-ID header to every request and response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


class RequestTimingMiddleware:
    """
    Logs wall-clock duration and DB query count/time for every request.
    force_debug_cursor is set so connection.queries is populated even in
    production (DEBUG=False), where it's normally empty.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prev_force_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True
        query_count_before = len(connection.queries)
        start = time.perf_counter()

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start) * 1000
        queries = connection.queries[query_count_before:]
        query_time_ms = sum(float(q["time"]) for q in queries) * 1000
        connection.force_debug_cursor = prev_force_debug_cursor

        log_fn = logger.warning if duration_ms >= SLOW_REQUEST_THRESHOLD_MS else logger.info
        log_fn(
            "%s %s completed in %.1fms (%d queries, %.1fms in DB)",
            request.method, request.get_full_path(), duration_ms, len(queries), query_time_ms,
            extra={
                "request_id": getattr(request, "request_id", None),
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 1),
                "query_count": len(queries),
                "query_time_ms": round(query_time_ms, 1),
            },
        )
        return response
