from datetime import timedelta
from pathlib import Path

from decouple import config
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "unfold.contrib.location_field",  # optional, if django-location-field package is used
    "unfold.contrib.constance",  # optional, if django-constance package is used
    "unfold.contrib.hijack",  # optional, if django-hijack package is used
    # First so core's management commands can intentionally override
    # commands supplied by server integrations such as Daphne.
    "core",
    # Django core
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "channels",
    "drf_spectacular",          # OpenAPI schema generation

    # Local apps
    "apps.users",
    "apps.catalog",
    "apps.inventory",
    "apps.orders",
    "apps.payments",
    "apps.shipping",
    "apps.promotions",
    "apps.notifications",
    "apps.analytics",
    "apps.chat",
    "apps.blog",
    "apps.storefronts",
    "apps.catalog_cannabis",
    "apps.catalog_peptides",
    "apps.catalog_footwear",
]

MIDDLEWARE = [
    "core.middleware.RequestTimingMiddleware",      # wraps the whole request; must stay first
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.storefronts.middleware.StorefrontMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestIDMiddleware",
]

ROOT_URLCONF    = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "users.User"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Authentication — Simple JWT
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------------------------------------------------------------
# Channels (WebSockets)
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(config("REDIS_URL", default="localhost"), 6379)],
        },
    },
}

# ---------------------------------------------------------------------------
# Django Tasks (replaces Celery)
# ---------------------------------------------------------------------------
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", ""),
    }
}

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Africa/Douala"
USE_I18N      = True
USE_TZ        = True

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Unfold admin
# ---------------------------------------------------------------------------
UNFOLD = {
    "SITE_TITLE": _("Axiom Commerce Admin"),
    "SITE_HEADER": _("Axiom Commerce"),
    "SITE_SUBHEADER": _("Store operations"),
    "DASHBOARD_CALLBACK": "core.admin_dashboard.dashboard_callback",
    "STYLES": [lambda request: static("admin/dashboard.css")],
    "SCRIPTS": [lambda request: static("admin/navigation.js")],
    "SITE_ICON": {
        "light": lambda request: static("branding/axiom-commerce-mark-light.png"),
        "dark": lambda request: static("branding/axiom-commerce-mark-dark.png"),
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static(
                "branding/axiom-commerce-favicon-32.png"
            ),
        },
        {
            "rel": "icon",
            "type": "image/x-icon",
            "href": lambda request: static(
                "branding/axiom-commerce-favicon.ico"
            ),
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Overview"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Catalog"),
                "collapsible": True,
                "separator": True,
                "items": [
                    {"title": _("Products"), "icon": "inventory_2", "link": reverse_lazy("admin:catalog_product_changelist")},
                    {"title": _("Variants"), "icon": "style", "link": reverse_lazy("admin:catalog_productvariant_changelist")},
                    {"title": _("Categories"), "icon": "category", "link": reverse_lazy("admin:catalog_category_changelist")},
                    {"title": _("Brands"), "icon": "verified", "link": reverse_lazy("admin:catalog_brand_changelist")},
                    {"title": _("Effects"), "icon": "auto_awesome", "link": reverse_lazy("admin:catalog_effect_changelist")},
                    {"title": _("Product images"), "icon": "image", "link": reverse_lazy("admin:catalog_productimage_changelist")},
                    {"title": _("Product videos"), "icon": "movie", "link": reverse_lazy("admin:catalog_productvideo_changelist")},
                    {"title": _("Variant images"), "icon": "photo_library", "link": reverse_lazy("admin:catalog_variantimage_changelist")},
                    {"title": _("Variant videos"), "icon": "video_library", "link": reverse_lazy("admin:catalog_variantvideo_changelist")},
                ],
            },
            {
                "title": _("Commerce"),
                "collapsible": True,
                "separator": True,
                "items": [
                    {"title": _("Storefronts"), "icon": "storefront", "link": reverse_lazy("admin:storefronts_storefront_changelist")},
                    {"title": _("Orders"), "icon": "receipt_long", "link": reverse_lazy("admin:orders_order_changelist")},
                    {"title": _("Carts"), "icon": "shopping_cart", "link": reverse_lazy("admin:orders_cart_changelist")},
                    {"title": _("Coupons"), "icon": "sell", "link": reverse_lazy("admin:promotions_coupon_changelist")},
                ],
            },
            {
                "title": _("Operations"),
                "collapsible": True,
                "separator": True,
                "items": [
                    {"title": _("Stock"), "icon": "inventory", "link": reverse_lazy("admin:inventory_stock_changelist")},
                    {"title": _("Stock movements"), "icon": "swap_horiz", "link": reverse_lazy("admin:inventory_stockmovement_changelist")},
                    {"title": _("Warehouses"), "icon": "warehouse", "link": reverse_lazy("admin:inventory_warehouse_changelist")},
                    {"title": _("Payments"), "icon": "payments", "link": reverse_lazy("admin:payments_payment_changelist")},
                    {"title": _("Payment methods"), "icon": "credit_card", "link": reverse_lazy("admin:payments_paymentmethod_changelist")},
                    {"title": _("Refunds"), "icon": "currency_exchange", "link": reverse_lazy("admin:payments_refund_changelist")},
                    {"title": _("Shipments"), "icon": "local_shipping", "link": reverse_lazy("admin:shipping_shipment_changelist")},
                    {"title": _("Shipping methods"), "icon": "package_2", "link": reverse_lazy("admin:shipping_shippingmethod_changelist")},
                    {"title": _("Tracking events"), "icon": "location_on", "link": reverse_lazy("admin:shipping_trackingevent_changelist")},
                ],
            },
            {
                "title": _("Customers"),
                "collapsible": True,
                "separator": True,
                "items": [
                    {"title": _("Users"), "icon": "group", "link": reverse_lazy("admin:users_user_changelist")},
                    {"title": _("Addresses"), "icon": "home_pin", "link": reverse_lazy("admin:users_address_changelist")},
                    {"title": _("Notifications"), "icon": "notifications", "link": reverse_lazy("admin:notifications_notification_changelist")},
                    {"title": _("Chat rooms"), "icon": "forum", "link": reverse_lazy("admin:chat_chatroom_changelist")},
                    {"title": _("Chat messages"), "icon": "chat", "link": reverse_lazy("admin:chat_chatmessage_changelist")},
                ],
            },
            {
                "title": _("Insights & content"),
                "collapsible": True,
                "separator": True,
                "items": [
                    {"title": _("Events"), "icon": "data_object", "link": reverse_lazy("admin:analytics_event_changelist")},
                    {"title": _("Daily sales"), "icon": "monitoring", "link": reverse_lazy("admin:analytics_dailysalessnapshot_changelist")},
                    {"title": _("Product performance"), "icon": "query_stats", "link": reverse_lazy("admin:analytics_productperformance_changelist")},
                    {"title": _("Conversion funnel"), "icon": "filter_alt", "link": reverse_lazy("admin:analytics_conversionfunnel_changelist")},
                    {"title": _("Blog posts"), "icon": "article", "link": reverse_lazy("admin:blog_blogpost_changelist")},
                ],
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# OpenAPI
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE":       "E-Commerce API",
    "DESCRIPTION": "High-performance Django e-commerce backend",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "OrderStatusEnum": "apps.orders.models.Order.Status",
        "ChatRoomStatusEnum": "apps.chat.models.ChatRoom.Status",
        "ShipmentStatusEnum": "apps.shipping.models.Shipment.Status",
        "PaymentStatusEnum": "apps.payments.models.Payment.Status",
        "RefundStatusEnum": "apps.payments.models.Refund.Status",
    },
}

# ---------------------------------------------------------------------------
# Email (base — overridden per environment)
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = config(
    "RESEND_FROM_EMAIL", config("DEFAULT_FROM_EMAIL", "noreply@example.com")
)

# Resend — all transactional email goes through services/email.py.
RESEND_API_KEY = config("RESEND_API_KEY", "")
ADMIN_NOTIFICATION_EMAIL = config("ADMIN_NOTIFICATION_EMAIL", "")

# Payment providers. Individual storefronts can override these through a
# provider-account model later; these defaults preserve the existing gateways.
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", "")
PAYPAL_CLIENT_ID = config("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = config("PAYPAL_CLIENT_SECRET", "")
PAYPAL_BASE_URL = config("PAYPAL_BASE_URL", "https://api-m.paypal.com")
PAYPAL_WEBHOOK_ID = config("PAYPAL_WEBHOOK_ID", "")
PAYPAL_RETURN_URL = config("PAYPAL_RETURN_URL", "")
PAYPAL_CANCEL_URL = config("PAYPAL_CANCEL_URL", "")

# Branding vars injected into every templates/emails/*.html render.
STORE_NAME    = config("STORE_NAME", "Our Store")
FRONTEND_URL  = config("FRONTEND_URL", "https://example.com")

BACKEND_URL = config("BACKEND_URL", "")
STORE_LOGO_URL= config("STORE_LOGO_URL", "")
SUPPORT_EMAIL = config("SUPPORT_EMAIL", "support@example.com")
STORE_ADDRESS = config("STORE_ADDRESS", "")
