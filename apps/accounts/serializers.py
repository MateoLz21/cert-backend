"""Serializers for the accounts app."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "phone", "avatar", "document_id"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "date_joined", "role", "is_active"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        read_only_fields = ["id"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for user management by admins/super admins.

    Unlike ``UserSerializer``, ``role`` is writable here so a super admin can
    assign it. ``password`` is write-only, required on create and optional on
    update.
    """

    profile = ProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "password",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "date_joined", "profile"]

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("La contraseña no puede estar vacía.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError(
                {"password": "La contraseña es obligatoria al crear un usuario."}
            )
        role = validated_data.pop("role", User.Role.CLIENT)
        user = User.objects.create_user(
            password=password, role=role, **validated_data
        )
        Profile.objects.get_or_create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
