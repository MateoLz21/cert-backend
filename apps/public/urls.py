"""Rutas públicas del sitio web (montadas bajo /api/v1/public/)."""
from django.urls import path

from .views import (
    CheckoutView,
    PublicLeadCreateView,
    StripeWebhookView,
    VerifyByCodeView,
)

app_name = "public"

urlpatterns = [
    path("leads/", PublicLeadCreateView.as_view(), name="lead-create"),
    path("verify/<str:code>/", VerifyByCodeView.as_view(), name="verify"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
