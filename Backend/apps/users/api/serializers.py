# =============================================================================
# apps/users/api/serializers.py
# =============================================================================
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Address
        fields = ["id", "line1", "line2", "city", "state", "postal_code", "country", "is_default"]
        read_only_fields = ["id"]


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model  = User
        fields = ["id", "email", "first_name", "last_name", "phone", "is_active", "is_guest", "created_at", "addresses"]
        read_only_fields = ["id", "is_active", "is_guest", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ["email", "first_name", "last_name", "phone", "password", "password2"]

    def validate(self, data):
        if data["password"] != data.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class GuestSessionSerializer(serializers.Serializer):
    """
    Optional email — chat can open a guest session with no email yet;
    checkout supplies one so the admin notification has somewhere to reply.
    """
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_email(self, value):
        if not value:
            return value
        # Only a real (registered, password-holding) account should block a
        # guest session — a leftover guest row from a previous checkout with
        # the same email is not something the person can "sign in" to.
        qs = User.objects.filter(email__iexact=value, is_guest=False)
        exclude_id = self.context.get("exclude_user_id")
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise serializers.ValidationError(
                "An account with this email already exists. Please sign in instead."
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user info to the JWT login response."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data