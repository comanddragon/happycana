# =============================================================================
# apps/orders/state_machine.py
#
# Centralises all order status transition logic.
# Every status change in the system must go through OrderStateMachine —
# no code should ever write order.status = "..." directly.
#
# Valid transitions:
#
#   PENDING ──► CONFIRMED ──► PROCESSING ──► SHIPPED ──► DELIVERED
#      │             │              │
#      └─────────────┴──────────────┴──────────────────► CANCELLED
#                                                              │
#   DELIVERED ──────────────────────────────────────────► REFUNDED
#   SHIPPED   ──────────────────────────────────────────► REFUNDED
# =============================================================================
from django.db import transaction
from apps.orders.models import Order


class InvalidTransitionError(Exception):
    """Raised when an attempted status transition is not permitted."""
    pass


# Maps each status to the set of statuses it is allowed to move to.
TRANSITIONS: dict[str, set[str]] = {
    Order.Status.PENDING:    {Order.Status.CONFIRMED,  Order.Status.CANCELLED},
    Order.Status.CONFIRMED:  {Order.Status.PROCESSING, Order.Status.CANCELLED},
    Order.Status.PROCESSING: {Order.Status.SHIPPED,    Order.Status.CANCELLED},
    Order.Status.SHIPPED:    {Order.Status.DELIVERED,  Order.Status.REFUNDED},
    Order.Status.DELIVERED:  {Order.Status.REFUNDED},
    Order.Status.CANCELLED:  set(),   # terminal
    Order.Status.REFUNDED:   set(),   # terminal
}


class OrderStateMachine:

    def __init__(self, order: Order):
        self.order = order

    # ------------------------------------------------------------------
    # Public transition methods
    # ------------------------------------------------------------------

    def confirm(self):
        """PENDING → CONFIRMED. Called after successful payment."""
        self._transition(Order.Status.CONFIRMED)

    def start_processing(self):
        """CONFIRMED → PROCESSING. Called when warehouse picks the order."""
        self._transition(Order.Status.PROCESSING)

    def ship(self):
        """PROCESSING → SHIPPED. Called when a Shipment is dispatched."""
        self._transition(Order.Status.SHIPPED)

    def deliver(self):
        """SHIPPED → DELIVERED. Called by tracking poll or manual update."""
        self._transition(Order.Status.DELIVERED)

    def cancel(self):
        """PENDING | CONFIRMED | PROCESSING → CANCELLED."""
        self._transition(Order.Status.CANCELLED)

    def refund(self):
        """SHIPPED | DELIVERED → REFUNDED. Called after refund is approved."""
        self._transition(Order.Status.REFUNDED)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def can_transition_to(self, target: str) -> bool:
        return target in TRANSITIONS.get(self.order.status, set())

    def available_transitions(self) -> set[str]:
        return TRANSITIONS.get(self.order.status, set())

    def is_terminal(self) -> bool:
        return not self.available_transitions()

    # ------------------------------------------------------------------
    # Core engine
    # ------------------------------------------------------------------

    @transaction.atomic
    def _transition(self, target: str):
        allowed = TRANSITIONS.get(self.order.status, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition order '{self.order.id}' "
                f"from '{self.order.status}' to '{target}'. "
                f"Allowed transitions: {allowed or 'none (terminal state)'}."
            )
        self.order.status = target
        self.order.save(update_fields=["status", "updated_at"])