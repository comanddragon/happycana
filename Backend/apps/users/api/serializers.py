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
        fields = ["id", "email", "first_name", "last_name", "phone", "is_active", "created_at", "addresses"]
        read_only_fields = ["id", "is_active", "created_at"]


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

