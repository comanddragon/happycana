
# =============================================================================
# apps/payments/admin.py
# =============================================================================
from django.contrib import admin
from apps.payments.models import Payment, Refund


class RefundInline(admin.TabularInline):
    model           = Refund
    extra           = 0
    readonly_fields = ["status", "created_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    inlines         = [RefundInline]
    list_display    = ["id", "order", "gateway", "amount", "currency", "status", "created_at"]
    list_filter     = ["gateway", "status", "created_at"]
    search_fields   = ["gateway_ref", "order__id"]
    readonly_fields = ["gateway_ref", "created_at"]
    raw_id_fields   = ["order"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display  = ["id", "payment", "amount", "status", "created_at"]
    list_filter   = ["status", "created_at"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["payment"]

    actions = ["approve_refunds", "reject_refunds"]

    @admin.action(description="Approve selected refunds")
    def approve_refunds(self, request, queryset):
        for refund in queryset.filter(status=Refund.Status.PENDING):
            from apps.payments.tasks import process_refund
            process_refund.enqueue(refund_id=str(refund.id))

    @admin.action(description="Reject selected refunds")
    def reject_refunds(self, request, queryset):
        queryset.filter(status=Refund.Status.PENDING).update(status=Refund.Status.REJECTED)
