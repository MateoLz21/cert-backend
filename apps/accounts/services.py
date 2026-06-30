"""Business logic for the accounts app.

Views stay thin and delegate user lifecycle operations here.
"""
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Profile

User = get_user_model()


class AccountService:
    """User and profile lifecycle operations."""

    @staticmethod
    @transaction.atomic
    def register_client(*, email, password, first_name="", last_name=""):
        """Create a client user together with an empty profile."""
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.CLIENT,
        )
        Profile.objects.create(user=user)
        return user
