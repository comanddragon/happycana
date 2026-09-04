# =============================================================================
# apps/orders/api/views.py
# =============================================================================
from django.db.models import Prefetch
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsOwnerOrAdmin
from apps.orders.models import Cart, CartItem, Order, OrderItem
from services.checkout import CheckoutService, CheckoutError
from .serializers import (
    CartSerializer, CartItemWriteSerializer,
    OrderSerializer, OrderCreateSerializer, OrderStatusSerializer,
)


def _cart_items_prefetch():
    """
    Everything CartItemSerializer.variant (a full ProductVariantSerializer)
    touches: attributes/images/videos/stock_levels (prefetch), product/lab
    (select_related). Without this, every field access on a cart item's
    variant is a fresh query per item.
    """
    return Prefetch(
        "items",
        queryset=CartItem.objects.select_related(
            "variant__product", "variant__lab",
        ).prefetch_related(
            "variant__attributes", "variant__images",
            "variant__videos", "variant__stock_levels",
        ),
    )


def _get_full_cart(user):
    cart, _ = Cart.objects.prefetch_related(_cart_items_prefetch()).get_or_create(user=user)
    return cart


def _order_items_prefetch():
    """Same relations as _cart_items_prefetch, for OrderItem.variant."""
    return Prefetch(
        "items",
        queryset=OrderItem.objects.select_related(
            "variant__product", "variant__lab",
        ).prefetch_related(
            "variant__attributes", "variant__images",
            "variant__videos", "variant__stock_levels",
        ),
    )


class CartView(APIView):
    """Always returns or creates the current user's cart."""
    def get(self, request):
        cart = _get_full_cart(request.user)
        return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        s = CartItemWriteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        variant  = s.validated_data["variant"]
        quantity = s.validated_data["quantity"]
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        cart = _get_full_cart(request.user)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemUpdateView(APIView):
    def patch(self, request, pk):
        item = CartItem.objects.get(pk=pk, cart__user=request.user)
        s = CartItemWriteSerializer(item, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        cart = _get_full_cart(request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request, pk):
        CartItem.objects.filter(pk=pk, cart__user=request.user).delete()
        cart = _get_full_cart(request.user)
        return Response(CartSerializer(cart).data)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    filter_backends  = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields  = ["created_at", "total"]
    ordering         = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs   = Order.objects.select_related("address", "coupon", "payment_method").prefetch_related(_order_items_prefetch())
        return qs if user.is_staff else qs.filter(user=user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Order.objects.select_related("address", "coupon", "payment_method").prefetch_related(_order_items_prefetch())


class OrderCreateView(APIView):
    """Delegates to CheckoutService — cart → order → stock reservation."""
    def post(self, request):
        s = OrderCreateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        try:
            order = CheckoutService.create_order(
                user               = request.user,
                address_id         = s.validated_data["address_id"],
                coupon_code        = s.validated_data.get("coupon_code"),
                shipping_method_id = s.validated_data["shipping_method_id"],
                payment_method_id  = s.validated_data["payment_method_id"],
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except CheckoutError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from apps.orders.state_machine import OrderStateMachine, InvalidTransitionError

class OrderCancelView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        self.check_object_permissions(request, order)
        try:
            sm = OrderStateMachine(order)
            sm.cancel()
        except InvalidTransitionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Admin-only — manually advance an order's status."""
    queryset           = Order.objects.all()
    serializer_class   = OrderStatusSerializer
    permission_classes = [permissions.IsAdminUser]
