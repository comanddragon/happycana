# =============================================================================
# apps/users/api/views.py
# =============================================================================
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User, Address
from apps.users.tasks import send_welcome_email
from .serializers import (
    UserSerializer, RegisterSerializer, ChangePasswordSerializer,
    AddressSerializer, CustomTokenObtainPairSerializer, GuestSessionSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        send_welcome_email.enqueue(str(user.id))
        token = RefreshToken.for_user(user)
        return Response({
            "user":    UserSerializer(user).data,
            "refresh": str(token),
            "access":  str(token.access_token),
        }, status=status.HTTP_201_CREATED)


class GuestSessionView(APIView):
    """
    Issues a passwordless guest identity so unauthenticated visitors can hit
    the exact same cart/order/chat endpoints as a logged-in user — those all
    key off request.user/JWT and need no special-casing once this exists.

    Called lazily, whenever a guest first needs a session: on "Add to Cart",
    on opening the floating chat widget, or when they type their email into
    the checkout contact step. Safe to call repeatedly — if the caller
    already holds a guest JWT, this reuses that same user (so the cart isn't
    lost) and just attaches the email if one wasn't set yet.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        already_guest = request.user.is_authenticated and getattr(request.user, "is_guest", False)
        s = GuestSessionSerializer(
            data=request.data,
            context={"exclude_user_id": request.user.id if already_guest else None},
        )
        s.is_valid(raise_exception=True)
        email = s.validated_data.get("email")

        # A different guest identity may already own this email (e.g. a
        # previous checkout/session on another device, or one already open
        # in this browser). Reuse that account instead of renaming/creating
        # one that would collide with it on the unique email constraint.
        existing_guest = None
        if email:
            qs = User.objects.filter(email__iexact=email, is_guest=True)
            if already_guest:
                qs = qs.exclude(id=request.user.id)
            existing_guest = qs.first()

        if existing_guest:
            user = existing_guest
            if already_guest:
                self._merge_guest_into(existing_guest, request.user)
        elif already_guest:
            user = request.user
            if email and user.email != email:
                user.email = email
                user.save(update_fields=["email"])
        else:
            user = User.objects.create_guest(email)

        token = RefreshToken.for_user(user)
        return Response({
            "user":    UserSerializer(user).data,
            "refresh": str(token),
            "access":  str(token.access_token),
        }, status=status.HTTP_200_OK)

    @staticmethod
    def _merge_guest_into(target_user, stale_user):
        """
        Folds a just-created guest session's data into a returning guest's
        account before the stale identity is dropped. Without this, any
        address or cart items built up under `stale_user` this visit become
        orphaned the moment the session swaps to `target_user` — the address
        no longer belongs to request.user, so checkout rejects it with
        "Address not found.", and the cart appears empty.
        """
        Address.objects.filter(user=stale_user).update(user=target_user)

        from apps.orders.models import Cart
        stale_cart = Cart.objects.filter(user=stale_user).prefetch_related("items").first()
        if stale_cart:
            target_cart, _ = Cart.objects.get_or_create(user=target_user)
            for item in stale_cart.items.all():
                existing_item = target_cart.items.filter(variant=item.variant).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save(update_fields=["quantity"])
                else:
                    item.cart = target_cart
                    item.save(update_fields=["cart"])
            stale_cart.delete()

        try:
            stale_user.delete()
        except Exception:
            # Has orders (PROTECT) or something else references it — leave
            # the empty shell in place rather than fail the whole request.
            pass


class LogoutView(APIView):
    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)