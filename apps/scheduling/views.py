from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin

from .models import AvailabilitySlot
from .serializers import AvailabilitySlotSerializer


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """Gestión de los slots de disponibilidad de la agenda."""

    queryset = AvailabilitySlot.objects.all()
    serializer_class = AvailabilitySlotSerializer

    filterset_fields = ["status", "date"]
    ordering_fields = ["date", "start_time"]
    ordering = ["date", "start_time"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "available"]:
            return [AllowAny()]
        return [IsAdmin()]

    @action(detail=False, methods=["get"])
    def available(self, request):
        """Devuelve únicamente los slots con estado disponible."""
        slots = self.get_queryset().filter(
            status=AvailabilitySlot.SlotStatus.AVAILABLE
        )
        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)
