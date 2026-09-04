# =============================================================================
# config/urls.py  — Root URL config
# =============================================================================
from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = settings.STORE_NAME
admin.site.site_title  = settings.STORE_NAME

API = "api/"

def health(request):
    # Runs a trivial query (not just an app-level ping) so external cron
    # hits to this endpoint also count as DB activity for Neon — otherwise
    # the web service stays warm while the Neon compute still auto-suspends
    # after ~5 min of no queries, and the next real API call pays the
    # multi-second wake-up cost.
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("", health),
    path("admin/",     admin.site.urls),

    # API apps
    path(API, include("apps.storefronts.urls")),
    path(API, include("apps.users.api.urls")),
    path(API, include("apps.catalog.api.urls")),
    path(API, include("apps.inventory.api.urls")),
    path(API, include("apps.orders.api.urls")),
    path(API, include("apps.payments.api.urls")),
    path(API, include("apps.shipping.api.urls")),
    path(API, include("apps.promotions.api.urls")),
    path(API, include("apps.notifications.api.urls")),
    path(API, include("apps.chat.api.urls")),
    path(API, include("apps.analytics.api.urls")),
    path(API, include("apps.blog.api.urls")),

    # OpenAPI docs
    path("api/schema/",          SpectacularAPIView.as_view(),        name="schema"),
    path("api/docs/",            SpectacularSwaggerView.as_view(),    name="swagger-ui"),
    path("api/redoc/",           SpectacularRedocView.as_view(),      name="redoc"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
