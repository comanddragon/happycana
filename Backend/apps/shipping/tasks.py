# =============================================================================
# apps/shipping/tasks.py
# =============================================================================
# Uses the same Django Tasks backend configured for every other application.
# =============================================================================
from django.tasks import task

import logging
logger = logging.getLogger(__name__)


@task()
def poll_tracking_updates():
    """
    Fetches latest tracking events from shipping providers for all
    in-transit shipments. Schedule every 2 hours via Celery Beat.
    """
    from apps.shipping.models import Shipment, TrackingEvent
    from apps.shipping.providers.dhl import DHLProvider
    from apps.shipping.providers.fedex import FedExProvider

    providers = {"dhl": DHLProvider(), "fedex": FedExProvider()}

    active = Shipment.objects.filter(
        status__in=[Shipment.Status.SHIPPED, Shipment.Status.IN_TRANSIT]
    ).select_related("order__user")

    for shipment in active:
        provider = providers.get(shipment.provider)
        if not provider or not shipment.tracking_number:
            continue

        try:
            events = provider.get_tracking_events(shipment.tracking_number)

            for event in events:
                TrackingEvent.objects.get_or_create(
                    shipment    = shipment,
                    occurred_at = event["occurred_at"],
                    defaults    = {
                        "status":      event["status"],
                        "location":    event.get("location", ""),
                        "description": event.get("description", ""),
                    },
                )

            # Auto-advance to DELIVERED if provider confirms it
            if events and "delivered" in events[-1]["status"].lower():
                if shipment.status != Shipment.Status.DELIVERED:
                    from services.order_fulfillment import FulfillmentService
                    # transition_to() stamps delivered_at and saves atomically
                    shipment.transition_to(Shipment.Status.DELIVERED)
                    FulfillmentService.mark_delivered(shipment.order)

        except Exception as exc:
            logger.exception("Tracking poll failed for shipment %s: %s", shipment.id, exc)
            raise


@task()
def send_shipping_notification(shipment_id: str):
    from apps.shipping.models import Shipment
    from services.email import EmailService
    from services.sms import SMSService

    try:
        shipment = Shipment.objects.select_related("order__user").get(id=shipment_id)
    except Shipment.DoesNotExist:
        logger.warning("send_shipping_notification: shipment %s not found", shipment_id)
        return

    EmailService.send_order_shipped(shipment.order, shipment)
    SMSService.send_order_shipped(shipment.order, shipment.tracking_number)
