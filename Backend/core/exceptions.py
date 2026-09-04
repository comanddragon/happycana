# =============================================================================
# core/exceptions.py
# =============================================================================
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        request_id = getattr(context.get("request"), "request_id", None)
        response.data = {
            "error":      True,
            "request_id": request_id,
            "status_code": response.status_code,
            "detail":     response.data,
        }

    return response


