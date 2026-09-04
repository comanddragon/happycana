import logging
import time
import uuid

from django.db import connection

from core.timing import reset_serialization_timer, get_serialization_time_ms

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
    Logs a stage-by-stage timing breakdown for every request: inbound
    network hop from the caller (Next.js), Django processing, DB query
    time/count, and JSON serialization time. force_debug_cursor is set so
    connection.queries is populated even in production (DEBUG=False), where
    it's normally empty.

    The inbound network hop is only known if the caller sends an
    `X-Client-Sent-At` header (epoch ms, e.g. `Date.now()` in Node). This
    middleware always emits `X-Django-Received-At` / `X-Django-Sent-At`
    (epoch ms) so the caller can work out the outbound hop and total round
    trip on its own side — see frontend/src/lib/timedFetch.server.ts.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        django_received_at = time.time() * 1000

        client_sent_at = None
        header_value = request.headers.get("X-Client-Sent-At")
        if header_value:
            try:
                client_sent_at = float(header_value)
            except ValueError:
                client_sent_at = None
        network_in_ms = max(django_received_at - client_sent_at, 0.0) if client_sent_at is not None else None

        prev_force_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True
        query_count_before = len(connection.queries)
        reset_serialization_timer()
        start = time.perf_counter()

        response = self.get_response(request)

        total_ms = (time.perf_counter() - start) * 1000
        queries = connection.queries[query_count_before:]
        query_time_ms = sum(float(q["time"]) for q in queries) * 1000
        serialization_ms = get_serialization_time_ms()
        processing_ms = max(total_ms - query_time_ms - serialization_ms, 0.0)
        connection.force_debug_cursor = prev_force_debug_cursor

        django_sent_at = time.time() * 1000
        response["Server-Timing"] = (
            f"django_total;dur={total_ms:.1f}, "
            f"processing;dur={processing_ms:.1f}, "
            f"db;dur={query_time_ms:.1f}, "
            f"serialization;dur={serialization_ms:.1f}"
        )
        response["X-Django-Received-At"] = str(django_received_at)
        response["X-Django-Sent-At"] = str(django_sent_at)

        log_fn = logger.warning if total_ms >= SLOW_REQUEST_THRESHOLD_MS else logger.info
        log_fn(
            "%s %s | network_in=%s processing=%.1fms db=%.1fms (%d queries) serialization=%.1fms total=%.1fms",
            request.method, request.get_full_path(),
            f"{network_in_ms:.1f}ms" if network_in_ms is not None else "n/a",
            processing_ms, query_time_ms, len(queries), serialization_ms, total_ms,
            extra={
                "request_id": getattr(request, "request_id", None),
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "network_in_ms": round(network_in_ms, 1) if network_in_ms is not None else None,
                "processing_ms": round(processing_ms, 1),
                "query_count": len(queries),
                "query_time_ms": round(query_time_ms, 1),
                "serialization_ms": round(serialization_ms, 1),
                "duration_ms": round(total_ms, 1),
            },
        )
        return response
